"""Mallios local API for converting YouTube audio to MP3.

The server listens on localhost only. It is intended to be used by
the accompanying Chrome extension, never exposed as an internet-facing API.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import threading
import time
import shutil
import platform
import sys
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, jsonify, request, send_file, Response, redirect
import urllib.request
import urllib.error

try:
    import drive_service
except ImportError:
    from backend import drive_service
DEFAULT_DOWNLOAD_FOLDER = Path.home() / "Downloads"
CONFIGS_DIR = PROJECT_ROOT / "configs"
LOGS_DIR = PROJECT_ROOT / "logs"
CONFIGS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

TOOLS_DIR = PROJECT_ROOT / "tools"
FFMPEG_PATH = TOOLS_DIR
YTDLP_PATH = TOOLS_DIR / "yt-dlp.exe"
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
VALID_QUALITIES = {"0", "2", "5"}
YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be"}

PROGRESS_STATE = {
    "status": "idle",  # "idle", "running", "completed", "failed"
    "percent": 0.0,
    "message": "",
    "error": "",
}
PROGRESS_LOCK = threading.Lock()
PARALLEL_PROGRESS = {}
MATCHING_DUPLICATE_FILES = []

# Cụm biến kiểm soát hủy tải
CANCEL_REQUESTED = False
ACTIVE_PROCESSES = {}
ACTIVE_PROCESSES_LOCK = threading.Lock()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024


def is_allowed_origin(origin: str) -> bool:
    if not origin:
        return True
    origin_lower = origin.lower()
    if origin_lower.startswith("chrome-extension://"):
        return True
    if any(h in origin_lower for h in ["youtube.com", "localhost", "127.0.0.1"]):
        return True
    return False


def apply_cors_headers(res):
    origin = request.headers.get("Origin", "")
    if is_allowed_origin(origin):
        res.headers["Access-Control-Allow-Origin"] = origin if origin else "*"
        res.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
        res.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        res.headers["Access-Control-Allow-Private-Network"] = "true"
        res.headers["Vary"] = "Origin"
    return res


def response(payload: dict, status: int = 200):
    result = jsonify(payload)
    return apply_cors_headers(result), status


@app.after_request
def cors_after_request(result):
    return apply_cors_headers(result)


def is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"} and len(parsed.netloc) > 0
    except Exception:
        return False


def normalize_links(raw_links: object) -> list[str]:
    links = [raw_links] if isinstance(raw_links, str) else raw_links
    if not isinstance(links, list):
        return []
    clean = [link.strip() for link in links if isinstance(link, str) and link.strip()]
    return clean if clean and all(is_valid_url(link) for link in clean) else []


def detect_browser_for_cookies() -> str | None:
    system = platform.system().lower()
    if system != "windows":
        return None

    local_appdata = os.environ.get("LOCALAPPDATA", "")
    appdata = os.environ.get("APPDATA", "")

    browser_checks = [
        ("edge", Path(local_appdata) / "Microsoft" / "Edge" / "User Data"),
        ("chrome", Path(local_appdata) / "Google" / "Chrome" / "User Data"),
        ("brave", Path(local_appdata) / "BraveSoftware" / "Brave-Browser" / "User Data"),
        ("firefox", Path(appdata) / "Mozilla" / "Firefox" / "Profiles"),
        ("opera", Path(appdata) / "Opera Software" / "Opera Stable"),
        ("chromium", Path(local_appdata) / "Chromium" / "User Data"),
    ]

    for browser_name, profile_path in browser_checks:
        if profile_path.exists():
            return browser_name

    return None


def add_cookie_args(arguments: list[str]) -> list[str]:
    """
    Ưu tiên cookies.txt nếu có.
    Không tự động đọc live DB của trình duyệt đang mở để tránh bị lock file gây đơ 15s.
    """
    cookies_file = CONFIGS_DIR / "cookies.txt"
    if cookies_file.is_file() and cookies_file.stat().st_size > 0:
        return [*arguments, "--cookies", str(cookies_file)]
    return arguments


def is_cookie_auth_error(output: str) -> bool:
    """Nhận diện lỗi có khả năng liên quan đến xác thực/cookie hoặc 403 Forbidden."""
    message = (output or "").lower()
    auth_patterns = (
        "403",
        "forbidden",
        "http error 403",
        "sign in to confirm",
        "sign in to confirm you're not a bot",
        "sign in to confirm you’re not a bot",
        "authentication",
        "authentication required",
        "requires authentication",
        "login required",
        "login to",
        "use --cookies",
        "use --cookies-from-browser",
        "cookies are required",
        "cookies required",
        "confirm your age",
        "age-restricted",
        "age restricted",
        "private video",
        "members-only",
        "members only",
        "this content is only available to members",
        "only available to members",
    )
    return any(pattern in message for pattern in auth_patterns)


def refresh_cookies_from_browser() -> bool:
    """
    Xuất cookie từ browser vào configs/cookies.txt.
    Ghi ra file tạm trước, chỉ thay file cũ khi export thành công.
    """
    browser_name = detect_browser_for_cookies()
    if not browser_name:
        return False

    cookies_file = CONFIGS_DIR / "cookies.txt"
    temp_cookie_file = cookies_file.with_name(
        f"{cookies_file.stem}.refresh-{os.getpid()}-{threading.get_ident()}.txt"
    )

    try:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["LANG"] = "en_US.UTF-8"

        completed = subprocess.run(
            [
                str(YTDLP_PATH),
                "--encoding", "utf-8",
                "--cookies-from-browser", browser_name,
                "--cookies", str(temp_cookie_file),
                "--skip-download",
                "--flat-playlist",
                "https://www.youtube.com/",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
            creationflags=CREATE_NO_WINDOW,
            check=False,
            env=env,
        )

        if temp_cookie_file.is_file() and temp_cookie_file.stat().st_size > 0:
            header = temp_cookie_file.read_text(
                encoding="utf-8", errors="replace"
            )[:300]
            if (
                completed.returncode == 0
                or "# HTTP Cookie File" in header
                or "# Netscape HTTP Cookie File" in header
            ):
                os.replace(temp_cookie_file, cookies_file)
                return True

    except (OSError, subprocess.TimeoutExpired):
        pass
    finally:
        try:
            if temp_cookie_file.exists():
                temp_cookie_file.unlink()
        except Exception:
            pass

    return False


def run_ytdlp_with_cookie_fallback(
    base_arguments: list[str],
) -> subprocess.CompletedProcess[str]:
    """
    Chạy yt-dlp bình thường.
    Nếu lỗi xác thực và có browser thì refresh cookies.txt và thử lại ngay.
    Nếu không có browser thì thử lại không cookie.
    """
    cookies_file = PROJECT_ROOT / "cookies.txt"
    arguments = add_cookie_args(base_arguments)

    completed = run_ytdlp(arguments)
    if completed.returncode == 0:
        return completed

    if not is_cookie_auth_error(f"{completed.stdout}\n{completed.stderr}"):
        return completed

    if refresh_cookies_from_browser():
        return run_ytdlp([*base_arguments, "--cookies", str(cookies_file)])

    return run_ytdlp(base_arguments)


def run_ytdlp(arguments: list[str]) -> subprocess.CompletedProcess[str]:
    # Ép buộc python và yt-dlp sử dụng bảng mã UTF-8 để tránh lỗi ký tự tiếng Việt có dấu
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["LANG"] = "en_US.UTF-8"
    
    return subprocess.run(
        [str(YTDLP_PATH), *arguments],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60 * 60,
        creationflags=CREATE_NO_WINDOW,
        check=False,
        env=env
    )


@app.route("/", methods=["GET"])
@app.route("/api/status", methods=["GET"])
def status():
    return response({"status": "online", "message": "Mallios MP3 server đang chạy."})


@app.route("/select-folder", methods=["POST", "OPTIONS"])
def select_folder():
    if request.method == "OPTIONS":
        return response({})

    # Windows Common Item Dialog - chọn thư mục
    # Hiển thị giao diện Folder + Select Folder + Cancel
    script = r"""
Add-Type -AssemblyName System.Windows.Forms

$source = @'
using System;
using System.Runtime.InteropServices;

public static class WindowsFolderPicker
{
    [ComImport]
    [Guid("DC1C5A9C-E88A-4DDE-A5A1-60F82A20AEF7")]
    private class FileOpenDialog
    {
    }

    [ComImport]
    [Guid("42f85136-db7e-439c-85f1-e4075d135fc8")]
    [InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    private interface IFileDialog
    {
        [PreserveSig] int Show(IntPtr parent);
        void SetFileTypes(uint cFileTypes, IntPtr filterSpec);
        void SetFileTypeIndex(uint iFileType);
        void GetFileTypeIndex(out uint piFileType);
        void Advise(IntPtr pfde, out uint cookie);
        void Unadvise(uint cookie);
        void SetOptions(uint fos);
        void GetOptions(out uint fos);
        void SetDefaultFolder(IShellItem psi);
        void SetFolder(IShellItem psi);
        void GetFolder(out IShellItem ppsi);
        void GetCurrentSelection(out IShellItem ppsi);
        void SetFileName([MarshalAs(UnmanagedType.LPWStr)] string pszName);
        void GetFileName([MarshalAs(UnmanagedType.LPWStr)] out string pszName);
        void SetTitle([MarshalAs(UnmanagedType.LPWStr)] string pszTitle);
        void SetOkButtonLabel([MarshalAs(UnmanagedType.LPWStr)] string pszText);
        void SetFileNameLabel([MarshalAs(UnmanagedType.LPWStr)] string pszText);
        void GetResult(out IShellItem ppsi);
        void AddPlace(IShellItem psi, uint fdap);
        void SetDefaultExtension([MarshalAs(UnmanagedType.LPWStr)] string pszDefaultExtension);
        void Close(int hr);
        void SetClientGuid(ref Guid guid);
        void ClearClientData();
        void SetFilter(IntPtr pFilter);
    }

    [ComImport]
    [Guid("43826D1E-E718-42EE-BC55-A1E261C37BFE")]
    [InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    private interface IShellItem
    {
        void BindToHandler(
            IntPtr pbc,
            ref Guid bhid,
            ref Guid riid,
            out IntPtr ppv
        );

        void GetParent(out IShellItem ppsi);

        void GetDisplayName(
            uint sigdnName,
            out IntPtr ppszName
        );

        void GetAttributes(
            uint sfgaoMask,
            out uint psfgaoAttribs
        );

        void Compare(
            IShellItem psi,
            uint hint,
            out int piOrder
        );
    }

    private const uint FOS_PICKFOLDERS = 0x00000020;
    private const uint FOS_FORCEFILESYSTEM = 0x00000040;
    private const uint FOS_PATHMUSTEXIST = 0x00000800;

    private const uint SIGDN_FILESYSPATH = 0x80058000;

    public static string Pick(IntPtr owner)
    {
        IFileDialog dialog = (IFileDialog)new FileOpenDialog();

        try
        {
            uint options;
            dialog.GetOptions(out options);

            options |= FOS_PICKFOLDERS;
            options |= FOS_FORCEFILESYSTEM;
            options |= FOS_PATHMUSTEXIST;

            dialog.SetOptions(options);

            dialog.SetTitle("Chọn thư mục lưu nhạc MP3");
            dialog.SetOkButtonLabel("Select Folder");

            int result = dialog.Show(owner);

            // Cancel
            if (result != 0)
                return "";

            IShellItem item;
            dialog.GetResult(out item);

            IntPtr displayName;
            item.GetDisplayName(
                SIGDN_FILESYSPATH,
                out displayName
            );

            try
            {
                return Marshal.PtrToStringUni(displayName) ?? "";
            }
            finally
            {
                if (displayName != IntPtr.Zero)
                    Marshal.FreeCoTaskMem(displayName);
            }
        }
        finally
        {
            if (dialog != null && Marshal.IsComObject(dialog))
            {
                Marshal.FinalReleaseComObject(dialog);
            }
        }
    }
}
'@

Add-Type -TypeDefinition $source -Language CSharp

$form = New-Object System.Windows.Forms.Form
$form.TopMost = $true
$form.Width = 1
$form.Height = 1
$form.ShowInTaskbar = $false
$form.StartPosition = [System.Windows.Forms.FormStartPosition]::CenterScreen
$form.Opacity = 0

try {
    $form.Show()
    $form.Activate()

    $folder = [WindowsFolderPicker]::Pick($form.Handle)

    if ($folder) {
        [Console]::OutputEncoding =
            [System.Text.UTF8Encoding]::new()

        Write-Output $folder
    }
}
finally {
    $form.Close()
    $form.Dispose()
}
"""

    try:
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-Sta", "-Command", script],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=CREATE_NO_WINDOW,
            timeout=120,
            check=False,
        )

    except (OSError, subprocess.TimeoutExpired) as error:
        return response(
            {
                "status": "error",
                "message": str(error)
            },
            500
        )

    folder = completed.stdout.strip()

    if folder:
        return response(
            {
                "status": "success",
                "path": str(Path(folder))
            }
        )

    if completed.returncode != 0 and completed.stderr.strip():
        return response(
            {
                "status": "error",
                "message": completed.stderr.strip()
            },
            500
        )

    return response(
        {
            "status": "cancel",
            "message": "Chưa chọn thư mục."
        }
    )

@app.route("/get-playlist", methods=["POST", "OPTIONS"])
def get_playlist():
    if request.method == "OPTIONS":
        return response({})
    url = str((request.get_json(silent=True) or {}).get("url", "")).strip()
    if not is_valid_url(url):
        return response({"status": "error", "message": "Đường dẫn không hợp lệ."}, 400)

    try:
        args = ["--dump-single-json", "--extractor-args", "youtube:player_client=android,web,tv"]
        if "list=" in url:
            args.append("--flat-playlist")
        else:
            args.append("--no-playlist")
        args.append(url)
        ytdlp_args = add_cookie_args(args)
        
        completed = run_ytdlp(ytdlp_args)
        if completed.returncode:
            return response({"status": "error", "message": f"Không thể quét danh sách. Stderr: {completed.stderr}"}, 502)
        info = json.loads(completed.stdout)
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as error:
        return response({"status": "error", "message": f"Không thể đọc dữ liệu: {error}"}, 500)

    entries = info.get("entries") or [info]
    items = []
    seen_video_ids = set()

    for entry in entries:
        if not entry:
            continue
        raw_url = entry.get("webpage_url") or entry.get("url") or ""
        v_id = entry.get("id") or extract_youtube_video_id(raw_url)
        
        # Lọc trùng lặp bài hát theo Video ID hoặc URL chuẩn
        dedup_key = v_id if v_id else raw_url
        if not dedup_key or dedup_key in seen_video_ids:
            continue
        seen_video_ids.add(dedup_key)

        canonical_url = f"https://www.youtube.com/watch?v={v_id}" if v_id else raw_url
        items.append({
            "title": entry.get("title") or "Tác phẩm không tên",
            "url": canonical_url,
            "id": v_id
        })
    
    # Nạp trước ngầm trong nền TOÀN BỘ danh sách bài hát để khi bấm ▶ bất kỳ bài nào cũng phát tức thì
    try:
        urls_to_preload = [item["url"] for item in items if item.get("url")]
        if urls_to_preload:
            threading.Thread(target=background_preload_streams, args=(urls_to_preload,), daemon=True).start()
    except Exception:
        pass

    return response({"status": "success", "items": items})


def extract_playlist_links(playlist_url: str, max_files: int = 0) -> list[str]:
    # Phân tích danh sách phát để lấy danh sách URL video con
    base_arguments = [
        "--flat-playlist", "--dump-single-json",
        "--extractor-args", "youtube:player_client=android,web,tv",
        playlist_url
    ]
    arguments = add_cookie_args(base_arguments)
        
    try:
        completed = subprocess.run(
            [str(YTDLP_PATH), *arguments],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            creationflags=CREATE_NO_WINDOW, timeout=45
        )
        if completed.returncode != 0 and is_cookie_auth_error(
            f"{completed.stdout}\n{completed.stderr}"
        ):
            cookies_file = PROJECT_ROOT / "cookies.txt"
            if refresh_cookies_from_browser():
                completed = subprocess.run(
                    [str(YTDLP_PATH), *base_arguments, "--cookies", str(cookies_file)],
                    capture_output=True, text=True, encoding="utf-8", errors="replace",
                    creationflags=CREATE_NO_WINDOW, timeout=45
                )
            else:
                completed = subprocess.run(
                    [str(YTDLP_PATH), *base_arguments],
                    capture_output=True, text=True, encoding="utf-8", errors="replace",
                    creationflags=CREATE_NO_WINDOW, timeout=45
                )

        if completed.returncode == 0:
            info = json.loads(completed.stdout)
            entries = info.get("entries") or []
            urls = []
            seen_ids = set()
            for entry in entries:
                if entry and entry.get("url"):
                    url_val = entry.get("url")
                    v_id = entry.get("id") or extract_youtube_video_id(url_val)
                    dedup_key = v_id if v_id else url_val
                    if dedup_key in seen_ids:
                        continue
                    seen_ids.add(dedup_key)

                    if v_id:
                        url_val = f"https://www.youtube.com/watch?v={v_id}"
                    elif not url_val.startswith("http"):
                        url_val = f"https://www.youtube.com/watch?v={url_val}"
                    urls.append(url_val)
            if max_files > 0:
                urls = urls[:max_files]
            return urls
    except Exception:
        pass
    return []


def remove_vietnamese_accents(text: str) -> str:
    accents = {
        'a': 'áàảãạăắằẳẵặâấầẩẫậ',
        'A': 'ÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬ',
        'd': 'đ',
        'D': 'Đ',
        'e': 'éèẻẽẹêếềểễệ',
        'E': 'ÉÈẺẼẸÊẾỀỂỄỆ',
        'i': 'íìỉĩị',
        'I': 'ÍÌỈĨỊ',
        'o': 'óòỏõọôốồổỗộơớờởỡợ',
        'O': 'ÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢ',
        'u': 'úùủũụưứừửữự',
        'U': 'ÚÙỦŨỤƯỨỪỬỮỰ',
        'y': 'ýỳỷỹỵ',
        'Y': 'ÝỲỶỸỴ'
    }
    for char, accented_chars in accents.items():
        for acc in accented_chars:
            text = text.replace(acc, char)
    return text


HISTORY_FILE = CONFIGS_DIR / "history.json"
HISTORY_BAK_FILE = CONFIGS_DIR / "history.json.bak"
HISTORY_LOCK = threading.Lock()


def normalize_fullwidth_chars(text: str) -> str:
    # Bản đồ chuyển đổi các ký tự fullwidth của Windows sang ASCII chuẩn
    fullwidth_map = {
        '｜': '|',
        '＂': '"',
        '？': '?',
        '：': ':',
        '＊': '*',
        '＜': '<',
        '＞': '>',
        '／': '/',
        '＼': '\\'
    }
    for fw, asc in fullwidth_map.items():
        text = text.replace(fw, asc)
    return text


def clean_video_title(title: str) -> str:
    # 0. Chuẩn hóa ký tự fullwidth Windows về ký tự thường để dễ xử lý
    title = normalize_fullwidth_chars(title)
    
    # 1. Loại bỏ các cụm từ thừa (cả hoa lẫn thường)
    junk_patterns = [
        r'\[Official\s+MV\]', r'\(Official\s+MV\)',
        r'\[Official\s+Music\s+Video\]', r'\(Official\s+Music\s+Video\)',
        r'\[MV\]', r'\(MV\)', r'\[Music\s+Video\]', r'\(Music\s+Video\)',
        r'\[Vietsub\]', r'\(Vietsub\)', r'\[Engsub\]', r'\(Engsub\)',
        r'\(Lyrics\)', r'\[Lyrics\]', r'\(Lrc\)', r'\[Lrc\]',
        r'\(Official\s+Audio\)', r'\[Official\s+Audio\]',
        r'\(Audio\s+Only\)', r'\[Audio\s+Only\]',
        r'\(Official\s+Video\)', r'\[Official\s+Video\]',
        r'\[Lofi\]', r'\(Lofi\)', r'\|Lofi',
        r'4K', r'1080p', r'HD', r'128kbps', r'320kbps'
    ]
    for pattern in junk_patterns:
        title = re.sub(pattern, '', title, flags=re.IGNORECASE)
    
    # 2. Xóa hoặc thay thế toàn bộ ký tự cấm đặt tên trên Windows để tránh lỗi đổi tên
    replacements = {
        '"': '',
        "'": '',
        '?': '',
        '*': '',
        '<': '',
        '>': '',
        '|': ' ',
        ':': ' - ',
        '/': '-',
        '\\': '-'
    }
    for char, rep in replacements.items():
        title = title.replace(char, rep)
        
    # 3. Loại bỏ các dấu ngăn cách thừa ở đầu/cuối sau khi xóa rác
    title = re.sub(r'\s*-\s*', ' - ', title) # Giữ định dạng "Ca sĩ - Bài hát" chuẩn
    
    # 4. Loại bỏ khoảng trắng thừa và dấu ngoặc trống
    title = ' '.join(title.split())
    title = title.replace('()', '').replace('[]', '').replace('{}', '')
    title = ' '.join(title.split())
    
    return title.strip()


def find_duplicate_file(save_folder: Path, clean_title: str) -> Path | None:
    # clean_title là tên file đã xóa dấu và làm sạch, ví dụ: "Hay Trao Cho Anh.mp3"
    target_stem = remove_vietnamese_accents(clean_video_title(clean_title.replace(".mp3", ""))).lower().strip()
    
    try:
        # Quét các file ở thư mục gốc và thư mục con cấp 1
        files = list(save_folder.glob("*.mp3")) + list(save_folder.glob("*/*.mp3"))
        for f in files:
            if f.is_file():
                # Làm sạch và xóa dấu tên file trên đĩa để so sánh
                disk_stem = remove_vietnamese_accents(clean_video_title(f.stem)).lower().strip()
                
                # 1. So sánh khớp hoàn toàn (không phân biệt hoa thường, có dấu hay không dấu)
                if disk_stem == target_stem:
                    return f
                    
                # 2. Hỗ trợ trường hợp file trên đĩa có/không có tên ca sĩ ghép vào (ví dụ: "Son Tung M-TP - Hay Trao Cho Anh" vs "Hay Trao Cho Anh")
                # Xóa phần tên ca sĩ phía trước nếu có dấu gạch ngang " - "
    except Exception:
        pass
        
    return None


HISTORY_BAK_FILE = BACKEND_DIR / "history.bak"


def extract_youtube_video_id(url: str) -> str:
    """Trích xuất ID video YouTube 11 ký tự chuẩn hóa."""
    if not url:
        return ""
    patterns = [
        r"(?:v=|\/v\/|youtu\.be\/|\/embed\/|\/shorts\/|\/live\/)([a-zA-Z0-9_-]{11})",
        r"^([a-zA-Z0-9_-]{11})$"
    ]
    for pattern in patterns:
        match = re.search(pattern, str(url))
        if match:
            return match.group(1)
    return ""


def get_duplicate_file_matches(save_folder: Path, clean_title: str) -> list[Path]:
    target_stem = remove_vietnamese_accents(clean_video_title(clean_title.replace(".mp3", ""))).lower().strip()
    matches: list[Path] = []

    try:
        files = list(save_folder.glob("*.mp3")) + list(save_folder.glob("*/*.mp3"))
        for f in files:
            if not f.is_file():
                continue

            disk_stem = remove_vietnamese_accents(clean_video_title(f.stem)).lower().strip()
            if disk_stem == target_stem:
                matches.append(f)
    except Exception:
        pass

    return matches


def load_history() -> list[dict]:
    """Đọc lịch sử chuẩn xác với cơ chế tự động phục hồi từ backup .bak nếu cần."""
    example_history = CONFIGS_DIR / "history.example.json"
    if not HISTORY_FILE.is_file():
        if example_history.is_file():
            try:
                shutil.copy2(example_history, HISTORY_FILE)
            except Exception:
                pass
        if HISTORY_BAK_FILE.is_file():
            try:
                with open(HISTORY_BAK_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        if HISTORY_BAK_FILE.is_file():
            try:
                with open(HISTORY_BAK_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return []


def save_history(history_data: list[dict]):
    """Ghi lịch sử an toàn nguyên tử (Atomic Write) qua tệp tạm .tmp và sao lưu .bak."""
    try:
        tmp_file = CONFIGS_DIR / "history.json.tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
            
        if HISTORY_FILE.is_file():
            try:
                shutil.copy2(HISTORY_FILE, HISTORY_BAK_FILE)
            except Exception:
                pass
                
        os.replace(tmp_file, HISTORY_FILE)
    except Exception as e:
        print(f"Lỗi lưu history.json: {e}")


def add_to_history(
    url: str,
    title: str,
    uploader: str,
    file_path: Path,
    save_folder: Path,
    storage_type: str = "local",
    drive_file_id: str = "",
    drive_web_link: str = ""
):
    with HISTORY_LOCK:
        history = load_history()
        video_id = extract_youtube_video_id(url)
        clean_target_stem = remove_vietnamese_accents(clean_video_title(title)).lower().strip()
        
        # Xóa bản ghi cũ trùng video_id, url hoặc tên bài trong cùng loại storage
        history = [
            item for item in history 
            if not (
                (video_id and item.get("video_id") == video_id and item.get("storage_type") == storage_type) or
                (url and item.get("url") == url and item.get("storage_type") == storage_type) or
                (remove_vietnamese_accents(clean_video_title(item.get("title", ""))).lower().strip() == clean_target_stem and item.get("storage_type") == storage_type)
            )
        ]
        
        try:
            relative_path = str(file_path.resolve().relative_to(save_folder.resolve())).replace("\\", "/")
        except Exception:
            relative_path = file_path.name
            
        record = {
            "video_id": video_id,
            "url": url,
            "title": clean_video_title(title),
            "uploader": uploader,
            "file_path": str(file_path.resolve()).replace("\\", "/"),
            "relative_path": relative_path,
            "timestamp": int(time.time()),
            "storage_type": storage_type
        }
        if drive_file_id:
            record["drive_file_id"] = drive_file_id
        if drive_web_link:
            record["drive_web_link"] = drive_web_link
            
        history.insert(0, record)
        history = history[:200]
        save_history(history)


def find_duplicate_fast(url: str, save_target: str, save_folder: Path) -> tuple[bool, dict | None]:
    """Kiểm tra trùng lặp siêu tốc từ RAM bằng Video ID (< 0.001ms) không cần chạy lệnh phụ."""
    video_id = extract_youtube_video_id(url)
    history = load_history()
    
    for item in history:
        is_matched = (video_id and item.get("video_id") == video_id) or (url and item.get("url") == url)
        if is_matched:
            if save_target == "drive" and item.get("storage_type") == "drive":
                return True, item
            elif save_target == "local" and item.get("storage_type") == "local":
                stored_path = Path(item.get("file_path", ""))
                if stored_path.is_file():
                    return True, item
    return False, None


def run_single_download(link: str, quality: str, save_folder: Path, state_key: str, save_target: str = "local"):
    global PARALLEL_PROGRESS, MATCHING_DUPLICATE_FILES
    
    if CANCEL_REQUESTED:
        with PROGRESS_LOCK:
            PARALLEL_PROGRESS[state_key]["status"] = "failed"
            PARALLEL_PROGRESS[state_key]["message"] = "Đã ngưng."
        return
        
    # 1. Kiểm tra trùng lặp siêu tốc từ RAM (< 0.001ms)
    is_dup, dup_item = find_duplicate_fast(link, save_target, save_folder)
    if is_dup and dup_item:
        with PROGRESS_LOCK:
            PARALLEL_PROGRESS[state_key]["started"] = True
            PARALLEL_PROGRESS[state_key]["percent"] = 100.0
            PARALLEL_PROGRESS[state_key]["status"] = "completed"
            msg = "Đã có trên Drive (Bỏ qua)." if save_target == "drive" else "Đã có (Bỏ qua)."
            PARALLEL_PROGRESS[state_key]["message"] = msg
            PARALLEL_PROGRESS[state_key]["skipped"] = True
            PARALLEL_PROGRESS[state_key]["duplicate_count"] = 1
            PARALLEL_PROGRESS[state_key]["duplicate_files"] = [
                {
                    "path": dup_item.get("drive_web_link") if save_target == "drive" else dup_item.get("file_path", ""),
                    "name": dup_item.get("title", "") + ".mp3",
                    "relative_path": dup_item.get("relative_path", dup_item.get("title", "") + ".mp3")
                }
            ]
        return
    
    # Quét danh sách file trước khi tải
    before_files = set()
    try:
        before_files = {
            str(p.resolve()) 
            for p in list(save_folder.glob("*.mp3")) + list(save_folder.glob("*/*.mp3"))
        }
    except Exception:
        pass

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["LANG"] = "en_US.UTF-8"

    arguments = [
        "--encoding", "utf-8",
        "-f", "ba[ext=m4a]/ba[ext=webm]/ba/best",
        "--extract-audio", "--audio-format", "mp3",
        "--audio-quality", quality,
        "--ffmpeg-location", str(FFMPEG_PATH),
        "--paths", str(save_folder),
        "--output", "%(uploader)s/%(title)s.%(ext)s",
        "--no-playlist",
        "--concurrent-fragments", "8",
        "--buffer-size", "128K",
        "--http-chunk-size", "10M",
        "--no-mtime",
        "--postprocessor-args", "ffmpeg:-threads 0 -preset ultrafast"
    ]
    
    is_youtube = any(host in link.lower() for host in YOUTUBE_HOSTS)
    if is_youtube:
        arguments.extend([
            "--sponsorblock-remove", "music_offtopic,sponsor,selfpromo,intro,outro",
            "--extractor-args", "youtube:player_client=android,web,tv"
        ])
        
    base_download_args = [*arguments, link]
    arguments = add_cookie_args(base_download_args)

    if CANCEL_REQUESTED:
        with PROGRESS_LOCK:
            PARALLEL_PROGRESS[state_key]["status"] = "failed"
            PARALLEL_PROGRESS[state_key]["message"] = "Đã ngưng."
        return

    try:
        # Tối đa 2 lượt cho cùng một bài:
        # lượt 1 dùng cookie hiện tại;
        # nếu lỗi xác thực -> refresh browser cookie -> thử lại ngay.
        # Nếu không có browser -> thử không cookie.
        retried_auth = False

        while True:
            process = subprocess.Popen(
                [str(YTDLP_PATH), *arguments],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=CREATE_NO_WINDOW,
                env=env
            )

            with ACTIVE_PROCESSES_LOCK:
                if CANCEL_REQUESTED:
                    try:
                        subprocess.run(
                            f"taskkill /F /T /PID {process.pid}",
                            shell=True,
                            creationflags=CREATE_NO_WINDOW
                        )
                    except Exception:
                        pass
                    return
                ACTIVE_PROCESSES[state_key] = process

            percent_regex = re.compile(r'\[download\]\s+([0-9\.]+)%')

            while True:
                if CANCEL_REQUESTED:
                    break
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                line_str = line.strip()
                if not line_str:
                    continue

                if "[download] Destination:" in line_str:
                    with PROGRESS_LOCK:
                        PARALLEL_PROGRESS[state_key]["started"] = True
                        PARALLEL_PROGRESS[state_key]["status"] = "downloading"

                percent_match = percent_regex.search(line_str)
                if percent_match:
                    try:
                        percent = float(percent_match.group(1))
                        with PROGRESS_LOCK:
                            PARALLEL_PROGRESS[state_key]["percent"] = min(percent, 98.0)
                            PARALLEL_PROGRESS[state_key]["message"] = f"Đang tải ({percent}%)"
                    except Exception:
                        pass
                elif "[ExtractAudio]" in line_str:
                    with PROGRESS_LOCK:
                        PARALLEL_PROGRESS[state_key]["percent"] = 99.0
                        PARALLEL_PROGRESS[state_key]["message"] = "Đang chuyển đổi MP3..."

            stdout_rem, stderr_data = process.communicate()
            returncode = process.returncode

            with ACTIVE_PROCESSES_LOCK:
                ACTIVE_PROCESSES.pop(state_key, None)

            combined_output = f"{stdout_rem}\n{stderr_data}"

            if (
                returncode != 0
                and not retried_auth
                and is_cookie_auth_error(combined_output)
            ):
                retried_auth = True

                if refresh_cookies_from_browser():
                    arguments = [*base_download_args, "--cookies", str(PROJECT_ROOT / "cookies.txt")]
                    with PROGRESS_LOCK:
                        PARALLEL_PROGRESS[state_key]["started"] = False
                        PARALLEL_PROGRESS[state_key]["percent"] = 0.0
                        PARALLEL_PROGRESS[state_key]["status"] = "downloading"
                        PARALLEL_PROGRESS[state_key]["message"] = "Cookie lỗi, đang làm mới cookie từ browser..."
                    continue

                # Không có browser -> thử đúng một lần không cookie.
                if "--cookies" in arguments:
                    arguments = [
                        arg for arg in arguments
                        if arg != "--cookies" and arg != str(PROJECT_ROOT / "cookies.txt")
                    ]
                    with PROGRESS_LOCK:
                        PARALLEL_PROGRESS[state_key]["started"] = False
                        PARALLEL_PROGRESS[state_key]["percent"] = 0.0
                        PARALLEL_PROGRESS[state_key]["status"] = "downloading"
                        PARALLEL_PROGRESS[state_key]["message"] = "Không có browser, thử tải không cookie..."
                    continue

            break

        # Đổi tên file và thư mục để xóa dấu tiếng Việt sau khi hoàn thành tải xuống thành công
        if returncode in {0, 101}:
            try:
                # Quét lại danh sách file sau khi tải xong (chỉ quét thư mục gốc và thư mục con cấp 1)
                after_files = list(save_folder.glob("*.mp3")) + list(save_folder.glob("*/*.mp3"))
                after_files.extend(list(save_folder.glob("*.webm")) + list(save_folder.glob("*/*.webm")))
                new_files = [p for p in after_files if str(p.resolve()) not in before_files]
                
                for original_file in new_files:
                    if original_file.is_file():
                        if original_file.suffix.lower() != ".mp3":
                            try:
                                original_file.unlink()
                            except Exception:
                                pass
                            continue

                        clean_title_raw = clean_video_title(original_file.stem)
                        clean_filename = remove_vietnamese_accents(clean_title_raw) + ".mp3"
                        original_parent = original_file.parent
                        clean_parent_name = remove_vietnamese_accents(original_parent.name)
                        
                        final_file_path = original_file
                        
                        # Chỉ đổi tên nếu thực sự có dấu cần xóa hoặc cần làm sạch tên
                        if original_file.name != clean_filename or original_parent.name != clean_parent_name:
                            if original_parent != save_folder:
                                clean_parent = original_parent.parent / clean_parent_name
                            else:
                                clean_parent = original_parent
                                
                            final_parent = original_parent
                            if original_parent != clean_parent:
                                if clean_parent.is_dir():
                                    final_parent = clean_parent
                                else:
                                    # Thêm cơ chế thử lại để tránh lỗi khóa tệp tạm thời trên Windows
                                    for attempt in range(5):
                                        try:
                                            original_parent.rename(clean_parent)
                                            final_parent = clean_parent
                                            # Cập nhật đường dẫn tệp sau khi thư mục cha bị đổi tên (tránh WinError 3)
                                            original_file = final_parent / original_file.name
                                            break
                                        except PermissionError:
                                            if attempt < 4:
                                                time.sleep(0.1)
                                            else:
                                                raise
                                        
                            final_file_path = final_parent / clean_filename
                            if original_file != final_file_path:
                                if final_file_path.is_file():
                                    try:
                                        final_file_path.unlink()
                                    except Exception:
                                        pass
                                
                                # Thêm cơ chế thử lại đổi tên tệp (tránh WinError 32)
                                for attempt in range(5):
                                    try:
                                        original_file.rename(final_file_path)
                                        break
                                    except PermissionError:
                                        if attempt < 4:
                                            time.sleep(0.1)
                                        else:
                                            raise
                                
                            # Dọn dẹp thư mục cũ có dấu nếu nó trống sau khi chuyển file đi
                            if original_parent != final_parent and original_parent.is_dir():
                                try:
                                    if not any(original_parent.iterdir()):
                                        original_parent.rmdir()
                                except Exception:
                                    pass
                        
                        if save_target == "drive":
                            if not drive_service.is_connected():
                                raise RuntimeError("Chưa kết nối tài khoản Google Drive.")

                            with PROGRESS_LOCK:
                                PARALLEL_PROGRESS[state_key]["percent"] = 99.0
                                PARALLEL_PROGRESS[state_key]["message"] = "Đang tải lên Google Drive..."

                            def on_drive_progress(pct, msg):
                                with PROGRESS_LOCK:
                                    PARALLEL_PROGRESS[state_key]["percent"] = pct
                                    PARALLEL_PROGRESS[state_key]["message"] = msg

                            drive_res = drive_service.upload_mp3_to_drive(
                                final_file_path,
                                clean_filename,
                                clean_parent_name,
                                progress_callback=on_drive_progress
                            )

                            add_to_history(
                                link,
                                clean_title_raw,
                                clean_parent_name,
                                final_file_path,
                                save_folder,
                                storage_type="drive",
                                drive_file_id=drive_res.get("id", ""),
                                drive_web_link=drive_res.get("webViewLink", "")
                            )

                            # Dọn dẹp file tạm sau khi upload lên Drive thành công
                            try:
                                if final_file_path.is_file():
                                    final_file_path.unlink()
                                if final_parent != save_folder and final_parent.is_dir() and not any(final_parent.iterdir()):
                                    final_parent.rmdir()
                            except Exception:
                                pass
                        else:
                            # Thêm bản ghi vào lịch sử phát nhạc (local)
                            add_to_history(
                                link,
                                clean_title_raw,
                                clean_parent_name,
                                final_file_path,
                                save_folder,
                                storage_type="local"
                            )
            except Exception as rename_err:
                with open(LOGS_DIR / "error.log", "a", encoding="utf-8") as f:
                    f.write(f"\n--- RENAME ERROR ---\nLink: {link}\nError: {rename_err}\n")
        
        with PROGRESS_LOCK:
            if returncode in {0, 101}:
                PARALLEL_PROGRESS[state_key]["percent"] = 100.0
                PARALLEL_PROGRESS[state_key]["status"] = "completed"
                PARALLEL_PROGRESS[state_key]["message"] = "Hoàn thành."
            else:
                PARALLEL_PROGRESS[state_key]["status"] = "failed"
                PARALLEL_PROGRESS[state_key]["percent"] = 0.0
                
                # Trích xuất dòng thông báo lỗi thực tế để hiện rõ ràng trên UI
                clean_err = "Lỗi yt-dlp"
                if stderr_data:
                    err_lines = [l.strip() for l in stderr_data.splitlines() if "ERROR:" in l or "Warning:" in l]
                    if err_lines:
                        clean_err = err_lines[-1].replace("ERROR:", "").strip()
                    else:
                        clean_err = stderr_data.strip().splitlines()[-1] if stderr_data.strip() else "Lỗi không xác định"
                
                PARALLEL_PROGRESS[state_key]["message"] = clean_err
                
                error_msg = f"yt-dlp error code {returncode} for link {link}. Stderr: {stderr_data}"
                with open(LOGS_DIR / "error.log", "a", encoding="utf-8") as f:
                    f.write(f"\n--- SINGLE DOWNLOAD ERROR ---\n{error_msg}\n")
                
    except Exception as e:
        with PROGRESS_LOCK:
            PARALLEL_PROGRESS[state_key]["status"] = "failed"
            PARALLEL_PROGRESS[state_key]["percent"] = 0.0
            PARALLEL_PROGRESS[state_key]["message"] = str(e)
    finally:
        with ACTIVE_PROCESSES_LOCK:
            if state_key in ACTIVE_PROCESSES:
                del ACTIVE_PROCESSES[state_key]


def run_parallel_downloads_background(links: list[str], quality: str, save_folder: Path, max_files: int, save_target: str = "local"):
    global PROGRESS_STATE, PARALLEL_PROGRESS, CANCEL_REQUESTED, MATCHING_DUPLICATE_FILES

    CANCEL_REQUESTED = False
    MATCHING_DUPLICATE_FILES = []
    
    # 1. Nếu là link danh sách phát và tải nhanh, phân tích danh sách phát trước
    resolved_links = []
    with PROGRESS_LOCK:
        PROGRESS_STATE["message"] = "Đang kiểm tra và chuẩn bị danh sách bài..."
        
    for link in links:
        if max_files == 1:
            resolved_links.append(link)
            continue

        if "list=" in link:
            # Nếu là link playlist hoặc video trong playlist nhưng muốn tải nhiều bài
            if "watch?v=" not in link or max_files > 1:
                urls = extract_playlist_links(link, max_files)
                if urls:
                    resolved_links.extend(urls)
                    continue
        resolved_links.append(link)
        
    if max_files > 0:
        resolved_links = resolved_links[:max_files]
        
    total_files = len(resolved_links)
    if total_files == 0:
        with PROGRESS_LOCK:
            PROGRESS_STATE["status"] = "completed"
            PROGRESS_STATE["percent"] = 100.0
            PROGRESS_STATE["message"] = "Không tìm thấy bài hát nào hợp lệ để tải."
        return

    with PROGRESS_LOCK:
        PARALLEL_PROGRESS.clear()
        for idx, link in enumerate(resolved_links):
            state_key = f"item_{idx}"
            PARALLEL_PROGRESS[state_key] = {
                "link": link,
                "percent": 0.0,
                "status": "pending",
                "message": "Đang xếp hàng...",
                "started": False,
                "skipped": False
            }
            
    # Giới hạn song song tối đa là 3 bài (mỗi bài 8 luồng = 24 luồng tối ưu băng thông)
    max_workers = 3
    
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            for idx, link in enumerate(resolved_links):
                state_key = f"item_{idx}"
                fut = executor.submit(run_single_download, link, quality, save_folder, state_key, save_target)
                futures[fut] = state_key
                
            while True:
                all_done = all(fut.done() for fut in futures)
                
                with PROGRESS_LOCK:
                    total_percent = 0.0
                    completed_count = 0
                    active_downloading = []
                    
                    for state_key, state in PARALLEL_PROGRESS.items():
                        total_percent += state["percent"]
                        if state["status"] == "completed":
                            completed_count += 1
                        elif state["status"] == "downloading" or state["started"]:
                            active_downloading.append(state_key)
                            
                    avg_percent = total_percent / total_files
                    PROGRESS_STATE["percent"] = round(avg_percent, 1)
                    
                    if completed_count < total_files:
                        if active_downloading:
                            active_ids = [str(int(k.split("_")[1]) + 1) for k in active_downloading]
                            active_msg = ", ".join(active_ids)
                            PROGRESS_STATE["message"] = f"Đang tải bài {completed_count + 1}/{total_files} (Đang chạy bài: {active_msg}) ({round(avg_percent, 1)}%)"
                        else:
                            PROGRESS_STATE["message"] = f"Đang chuẩn bị các bài... ({completed_count}/{total_files} đã xong)"
                    else:
                        skipped_count = sum(1 for s in PARALLEL_PROGRESS.values() if s.get("skipped", False))
                        actual_downloaded = completed_count - skipped_count
                        parts = []
                        if actual_downloaded > 0:
                            parts.append(f"đã tải {actual_downloaded} bài mới")
                        if skipped_count > 0:
                            parts.append(f"bỏ qua {skipped_count} bài trùng")
                        folder_label = "Google Drive" if save_target == "drive" else str(save_folder)
                        PROGRESS_STATE["message"] = f"Hoàn thành ({', '.join(parts)}) vào: {folder_label}"
                        
                if all_done:
                    break
                    
                time.sleep(0.5)
                
        with PROGRESS_LOCK:
            failed_count = sum(1 for state in PARALLEL_PROGRESS.values() if state["status"] == "failed")
            completed_count = sum(1 for state in PARALLEL_PROGRESS.values() if state["status"] == "completed")
            skipped_count = sum(1 for state in PARALLEL_PROGRESS.values() if state.get("skipped", False))
            actual_downloaded = completed_count - skipped_count
            
            if completed_count > 0:
                PROGRESS_STATE["status"] = "completed"
                PROGRESS_STATE["percent"] = 100.0
                
                parts = []
                if actual_downloaded > 0:
                    parts.append(f"Đã tải {actual_downloaded} bài mới")
                if skipped_count > 0:
                    parts.append(f"bỏ qua {skipped_count} bài đã có")
                if failed_count > 0:
                    parts.append(f"lỗi {failed_count} bài")
                    
                folder_label = "Google Drive (Mallios Music)" if save_target == "drive" else str(save_folder)
                PROGRESS_STATE["message"] = f"Hoàn thành ({', '.join(parts)}) vào: {folder_label}"
            else:
                PROGRESS_STATE["status"] = "failed"
                PROGRESS_STATE["percent"] = 0.0
                
                failed_msgs = [state["message"] for state in PARALLEL_PROGRESS.values() if state["status"] == "failed" and state.get("message")]
                err_detail = failed_msgs[0] if failed_msgs else "Không thể tải video (Có thể do yt-dlp cũ hoặc link bị chặn)."
                
                PROGRESS_STATE["message"] = f"Lỗi: {err_detail}"
                PROGRESS_STATE["error"] = f"Lỗi: {err_detail}"
            
    except Exception as error:
        with PROGRESS_LOCK:
            PROGRESS_STATE["status"] = "failed"
            PROGRESS_STATE["error"] = str(error)
            PROGRESS_STATE["message"] = "Quá trình tải song song gặp lỗi."


@app.route("/api/progress", methods=["GET"])
def get_progress():
    with PROGRESS_LOCK:
        if PROGRESS_STATE["status"] == "cancelled":
            has_failed = False
        else:
            has_failed = any(state["status"] == "failed" for state in PARALLEL_PROGRESS.values())
        state_copy = PROGRESS_STATE.copy()
        state_copy["has_failed"] = has_failed
        state_copy["duplicate_files"] = list(MATCHING_DUPLICATE_FILES)
        state_copy["duplicate_count"] = sum(state.get("duplicate_count", 0) for state in PARALLEL_PROGRESS.values())
        return response(state_copy)


@app.route("/download", methods=["POST", "OPTIONS"])
def download():
    if request.method == "OPTIONS":
        return response({})
        
    global PROGRESS_STATE
    with PROGRESS_LOCK:
        if PROGRESS_STATE["status"] == "running":
            return response({"status": "error", "message": "Có một tiến trình tải đang chạy. Vui lòng đợi."}, 400)
        
        # Reset trạng thái đồng bộ ngay lập tức để tránh tranh chấp (race condition) khi polling
        PROGRESS_STATE["status"] = "running"
        PROGRESS_STATE["percent"] = 0.0
        PROGRESS_STATE["message"] = "Đang khởi tạo tải..."
        PROGRESS_STATE["error"] = ""
            
    data = request.get_json(silent=True) or {}
    links = normalize_links(data.get("links", []))
    if not links:
        with PROGRESS_LOCK:
            PROGRESS_STATE["status"] = "failed"
            PROGRESS_STATE["error"] = "Không có link YouTube hợp lệ."
            PROGRESS_STATE["message"] = "Tải thất bại."
            
        return response({"status": "error", "message": "Hãy chọn ít nhất một link YouTube hợp lệ."}, 400)
 
    requested_path = str(data.get("download_path", "")).strip()
    save_target = str(data.get("save_target", "local")).strip().lower()
    if save_target != "drive":
        save_target = "local"

    requested_folder = Path(requested_path) if requested_path else None
    save_folder = requested_folder if requested_folder and requested_folder.is_dir() else DEFAULT_DOWNLOAD_FOLDER
    quality = str(data.get("quality", "0"))
    quality = quality if quality in VALID_QUALITIES else "0"
    max_files = data.get("max_files", 0)
    try:
        max_files = max(0, min(int(max_files), 100))
    except (TypeError, ValueError):
        max_files = 0
 
    try:
        thread = threading.Thread(
            target=run_parallel_downloads_background,
            args=(links, quality, save_folder, max_files, save_target)
        )
        thread.daemon = True
        thread.start()
        
        return response({"status": "success", "message": "Bắt đầu tải..."})
        
    except Exception as error:
        with PROGRESS_LOCK:
            PROGRESS_STATE["status"] = "failed"
            PROGRESS_STATE["error"] = str(error)
            PROGRESS_STATE["message"] = "Khởi động luồng tải song song thất bại."
        return response({"status": "error", "message": f"Không thể bắt đầu tải: {error}"}, 500)


@app.route("/retry-failed", methods=["POST", "OPTIONS"])
def retry_failed():
    if request.method == "OPTIONS":
        return response({})
        
    global CANCEL_REQUESTED, PROGRESS_STATE
    
    # Lấy danh sách các liên kết bị lỗi từ PARALLEL_PROGRESS hiện tại
    failed_links = []
    with PROGRESS_LOCK:
        if PROGRESS_STATE["status"] == "running":
            return response({"status": "error", "message": "Có một tiến trình tải đang chạy. Vui lòng đợi."}, 400)
            
        for state in PARALLEL_PROGRESS.values():
            if state["status"] == "failed":
                failed_links.append(state["link"])
                
    if not failed_links:
        return response({"status": "error", "message": "Không có bài hát nào bị lỗi để tải lại."})
        
    data = request.get_json(silent=True) or {}
    requested_path = str(data.get("download_path", "")).strip()
    save_target = str(data.get("save_target", "local")).strip().lower()
    if save_target != "drive":
        save_target = "local"

    requested_folder = Path(requested_path) if requested_path else None
    save_folder = requested_folder if requested_folder and requested_folder.is_dir() else DEFAULT_DOWNLOAD_FOLDER
    quality = str(data.get("quality", "0"))
    quality = quality if quality in VALID_QUALITIES else "0"
    
    # Khởi động tải song song cho các link bị lỗi
    with PROGRESS_LOCK:
        PROGRESS_STATE["status"] = "running"
        PROGRESS_STATE["percent"] = 0.0
        PROGRESS_STATE["message"] = f"Đang tải lại {len(failed_links)} bài hát bị lỗi..."
        PROGRESS_STATE["error"] = ""
        
    try:
        thread = threading.Thread(
            target=run_parallel_downloads_background,
            args=(failed_links, quality, save_folder, len(failed_links), save_target)
        )
        thread.daemon = True
        thread.start()
        return response({"status": "success", "message": f"Bắt đầu tải lại {len(failed_links)} bài hát."})
    except Exception as error:
        with PROGRESS_LOCK:
            PROGRESS_STATE["status"] = "failed"
            PROGRESS_STATE["error"] = str(error)
            PROGRESS_STATE["message"] = "Không thể bắt đầu tải lại."
        return response({"status": "error", "message": f"Không thể bắt đầu tải lại: {error}"}, 500)


@app.route("/cancel", methods=["POST", "OPTIONS"])
def cancel_downloads():
    if request.method == "OPTIONS":
        return response({})
        
    global CANCEL_REQUESTED, PROGRESS_STATE
    CANCEL_REQUESTED = True
    
    # Đóng các tiến trình đang hoạt động
    terminated_count = 0
    with ACTIVE_PROCESSES_LOCK:
        for state_key, proc in list(ACTIVE_PROCESSES.items()):
            try:
                subprocess.run(f"taskkill /F /T /PID {proc.pid}", shell=True, creationflags=CREATE_NO_WINDOW)
                terminated_count += 1
            except Exception:
                pass
        ACTIVE_PROCESSES.clear()
        
    with PROGRESS_LOCK:
        # Đánh dấu các tiến trình chưa xong là cancelled
        for state_key, state in PARALLEL_PROGRESS.items():
            if state["status"] in {"pending", "downloading"}:
                state["status"] = "cancelled"
                state["message"] = "Đã ngưng tải."
                
        PROGRESS_STATE["status"] = "cancelled"
        PROGRESS_STATE["message"] = "Đã ngưng tải theo yêu cầu."
        
    return response({"status": "success", "message": f"Đã ngưng tải ({terminated_count} tiến trình bị đóng)."})


@app.route("/history", methods=["GET"])
def get_history():
    return response({"status": "success", "history": load_history()})


@app.route("/play", methods=["GET"])
def play_audio():
    file_path_str = request.args.get("path")
    if not file_path_str:
        return response({"status": "error", "message": "Thiếu đường dẫn tệp."}, 400)
    
    # 1. Chuẩn hóa đường dẫn cho Windows
    clean_path_str = file_path_str.replace("/", "\\")
    path = Path(clean_path_str)
    
    # 2. Nếu không tìm thấy file do đổi tên/xóa dấu, quét tìm lại file MP3 tương ứng
    if not path.is_file():
        parent_dir = path.parent
        if parent_dir.is_dir():
            target_clean = remove_vietnamese_accents(path.name).lower()
            for f in parent_dir.glob("*.mp3"):
                if remove_vietnamese_accents(f.name).lower() == target_clean:
                    path = f
                    break

    if not path.is_file():
        return response({"status": "error", "message": f"Không tìm thấy tệp nhạc: {file_path_str}"}, 404)
        
    try:
        # 3. Gửi file kèm header Accept-Ranges để Chrome lấy được thời lượng và tua nhạc
        res = send_file(
            str(path.resolve()), 
            mimetype="audio/mpeg", 
            as_attachment=False,
            conditional=True
        )
        res.headers["Accept-Ranges"] = "bytes"
        return res
    except Exception as e:
        return response({"status": "error", "message": str(e)}, 500)


PREVIEW_STREAM_CACHE: dict[str, tuple[str, float]] = {}
PREVIEW_CACHE_LOCK = threading.Lock()
IN_FLIGHT_FETCHES: dict[str, threading.Event] = {}
PRELOAD_EXECUTOR = ThreadPoolExecutor(max_workers=5)


def background_preload_streams(urls: list[str]):
    """Chạy ngầm nạp trước luồng âm thanh song song vào RAM để người dùng bấm nghe thử là phát tức thì."""
    for u in urls:
        if not u:
            continue
        try:
            PRELOAD_EXECUTOR.submit(get_direct_stream_url, u)
        except Exception:
            pass


def get_direct_stream_url(video_url: str) -> str:
    """Lấy direct audio stream URL từ yt-dlp với cache RAM và khóa chống nghẽn luồng."""
    now = time.time()
    with PREVIEW_CACHE_LOCK:
        if video_url in PREVIEW_STREAM_CACHE:
            url, expire_time = PREVIEW_STREAM_CACHE[video_url]
            if now < expire_time:
                return url
        
        # Nếu đang có một luồng khác xử lý bài hát này, đợi luồng đó xong
        if video_url in IN_FLIGHT_FETCHES:
            event = IN_FLIGHT_FETCHES[video_url]
            wait_for_other = True
        else:
            event = threading.Event()
            IN_FLIGHT_FETCHES[video_url] = event
            wait_for_other = False

    if wait_for_other:
        event.wait(timeout=8)
        with PREVIEW_CACHE_LOCK:
            if video_url in PREVIEW_STREAM_CACHE:
                return PREVIEW_STREAM_CACHE[video_url][0]
        return ""

    try:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["LANG"] = "en_US.UTF-8"
        
        cmd = [
            str(YTDLP_PATH),
            "-g", "-f", "ba/18/b",
            "--extractor-args", "youtube:player_client=android",
            "--no-playlist", "--no-warnings",
            video_url
        ]
        try:
            completed = subprocess.run(
                cmd,
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                creationflags=CREATE_NO_WINDOW, timeout=12, env=env
            )
            if completed.returncode == 0:
                lines = [l.strip() for l in completed.stdout.splitlines() if l.strip() and l.startswith("http")]
                if lines:
                    direct_url = lines[0]
                    with PREVIEW_CACHE_LOCK:
                        PREVIEW_STREAM_CACHE[video_url] = (direct_url, now + 1800)
                    return direct_url
        except Exception:
            pass
        return ""
    finally:
        with PREVIEW_CACHE_LOCK:
            if video_url in IN_FLIGHT_FETCHES:
                del IN_FLIGHT_FETCHES[video_url]
        event.set()


@app.route("/api/preview-stream", methods=["GET", "OPTIONS"])
def preview_stream():
    """Chuyển hướng trực tiếp 302 đến Google CDN để phát âm thanh ngay lập tức."""
    if request.method == "OPTIONS":
        return response({})
        
    video_url = request.args.get("url", "").strip()
    if not video_url:
        return response({"status": "error", "message": "Thiếu tham số url."}, 400)

    direct_url = get_direct_stream_url(video_url)
    if not direct_url:
        return response({"status": "error", "message": "Không thể lấy luồng âm thanh nghe thử."}, 500)

    return redirect(direct_url, code=302)


@app.route("/open-folder", methods=["POST", "OPTIONS"])
def open_folder():
    if request.method == "OPTIONS":
        return response({})
        
    data = request.get_json() or {}
    drive_link = data.get("drive_link")
    if drive_link:
        try:
            webbrowser.open(drive_link)
            return response({"status": "success"})
        except Exception as e:
            return response({"status": "error", "message": str(e)}, 500)

    file_path_str = data.get("path")
    if not file_path_str:
        return response({"status": "error", "message": "Thiếu đường dẫn tệp."}, 400)
        
    path = Path(file_path_str)
    if not path.is_file():
        return response({"status": "error", "message": "Không tìm thấy tệp nhạc."}, 404)
        
    try:
        # Mở thư mục và khoanh vùng tô đậm file trên Windows
        subprocess.Popen(f'explorer /select,"{path}"')
        return response({"status": "success"})
    except Exception as e:
        return response({"status": "error", "message": str(e)}, 500)


@app.route("/delete-history", methods=["POST", "OPTIONS"])
def delete_history():
    if request.method == "OPTIONS":
        return response({})
        
    data = request.get_json() or {}
    url = data.get("url")
    delete_file = data.get("delete_file", False)
    file_path_str = data.get("file_path")
    
    with HISTORY_LOCK:
        history = load_history()
        new_history = [item for item in history if item.get("url") != url]
        save_history(new_history)
        
    if delete_file and file_path_str:
        try:
            path = Path(file_path_str)
            if path.is_file():
                path.unlink()
                # Xóa thư mục ca sĩ nếu trống
                if path.parent.is_dir() and not any(path.parent.iterdir()):
                    path.parent.rmdir()
        except Exception:
            pass
            
    return response({"status": "success"})


@app.route("/auth/google/status", methods=["GET"])
def google_auth_status():
    return response({"status": "success", "data": drive_service.get_account_status()})


@app.route("/auth/google/script-url", methods=["POST", "OPTIONS"])
def google_auth_script_url():
    if request.method == "OPTIONS":
        return response({})
    data = request.get_json(silent=True) or {}
    script_url = str(data.get("script_url", "")).strip()
    if not script_url:
        return response({"status": "error", "message": "Vui lòng nhập đường dẫn Google Apps Script."}, 400)

    success, msg, auth_info = drive_service.set_script_url(script_url)
    if success:
        return response({"status": "success", "message": msg, "data": auth_info})
    else:
        return response({"status": "error", "message": msg}, 400)


@app.route("/auth/google/set-token", methods=["POST", "OPTIONS"])
def google_auth_set_token():
    if request.method == "OPTIONS":
        return response({})
    data = request.get_json(silent=True) or {}
    token = str(data.get("access_token", "")).strip()
    if not token:
        return response({"status": "error", "message": "Thiếu Access Token từ Chrome."}, 400)
    
    expires_in = int(data.get("expires_in", 3600))
    success, msg, auth_info = drive_service.set_direct_token(token, expires_in)
    if success:
        return response({"status": "success", "message": msg, "data": auth_info})
    else:
        return response({"status": "error", "message": msg}, 400)


@app.route("/auth/google/config", methods=["POST", "OPTIONS"])
def google_auth_config():
    if request.method == "OPTIONS":
        return response({})
    data = request.get_json(silent=True) or {}
    client_id = str(data.get("client_id", "")).strip()
    client_secret = str(data.get("client_secret", "")).strip()
    folder_name = str(data.get("folder_name", "Mallios Music")).strip() or "Mallios Music"
    
    cfg = drive_service.load_config()
    if client_id:
        cfg["client_id"] = client_id
    if client_secret:
        cfg["client_secret"] = client_secret
    drive_service.save_config(cfg)
    
    auth = drive_service.load_auth()
    auth["folder_name"] = folder_name
    drive_service.save_auth(auth)
    
    return response({
        "status": "success",
        "message": "Đã lưu cấu hình Google Drive.",
        "data": drive_service.get_account_status()
    })


@app.route("/auth/google/login", methods=["POST", "OPTIONS"])
def google_auth_login():
    if request.method == "OPTIONS":
        return response({})
    try:
        auth_url = drive_service.get_auth_url()
        try:
            webbrowser.open(auth_url)
        except Exception:
            pass
        return response({"status": "success", "auth_url": auth_url})
    except Exception as e:
        return response({"status": "error", "message": str(e)}, 400)


@app.route("/auth/google/callback", methods=["GET"])
def google_auth_callback():
    code = request.args.get("code")
    error = request.args.get("error")
    if error:
        return f"""
        <!DOCTYPE html>
        <html>
            <head><meta charset="utf-8"><title>Lỗi kết nối Google Drive</title></head>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; text-align: center; padding: 60px 20px; background: #1a1a24; color: #fff;">
                <div style="max-width: 460px; margin: 0 auto; background: #282935; padding: 32px; border-radius: 16px;">
                    <div style="font-size: 40px; margin-bottom: 12px;">❌</div>
                    <h2 style="color: #ffb4ab; margin-bottom: 12px;">Kết nối thất bại</h2>
                    <p style="color: #c4c6d0; font-size: 14px; margin-bottom: 20px;">Lỗi từ Google: {error}</p>
                    <button onclick="window.close()" style="background: #ffb4ab; color: #690005; border: none; padding: 10px 24px; border-radius: 20px; font-weight: bold; cursor: pointer;">Đóng tab này</button>
                </div>
            </body>
        </html>
        """, 400

    if not code:
        return "Thiếu Authorization Code từ Google.", 400

    success, msg, auth_info = drive_service.exchange_code_for_token(code)
    email = auth_info.get("email", "")
    if success:
        return f"""
        <!DOCTYPE html>
        <html>
            <head><meta charset="utf-8"><title>Kết nối Google Drive thành công</title></head>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; text-align: center; padding: 60px 20px; background: #131318; color: #e2e2e9;">
                <div style="max-width: 480px; margin: 0 auto; background: #1e1f29; padding: 36px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); border: 1px solid #333544;">
                    <div style="font-size: 48px; margin-bottom: 12px;">☁️</div>
                    <h2 style="color: #a8c7fa; margin: 0 0 10px 0;">Kết nối Google Drive thành công!</h2>
                    <p style="color: #c2efb3; font-weight: bold; font-size: 15px; margin: 0 0 16px 0;">{email}</p>
                    <p style="color: #8e9099; font-size: 13px; line-height: 1.5; margin-bottom: 24px;">Giờ đây bài hát tải về sẽ tự động được đồng bộ và lưu vào Google Drive của bạn.</p>
                    <button onclick="window.close()" style="background: #a8c7fa; color: #003355; border: none; padding: 10px 28px; border-radius: 20px; font-weight: bold; cursor: pointer; font-size: 14px;">Đóng tab</button>
                </div>
            </body>
        </html>
        """, 200
    else:
        return f"""
        <!DOCTYPE html>
        <html>
            <head><meta charset="utf-8"><title>Lỗi kết nối</title></head>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; text-align: center; padding: 60px 20px; background: #1a1a24; color: #fff;">
                <div style="max-width: 460px; margin: 0 auto; background: #282935; padding: 32px; border-radius: 16px;">
                    <div style="font-size: 40px; margin-bottom: 12px;">⚠️</div>
                    <h2 style="color: #ffb4ab; margin-bottom: 12px;">Xác thực không thành công</h2>
                    <p style="color: #c4c6d0; font-size: 14px; margin-bottom: 20px;">{msg}</p>
                    <button onclick="window.close()" style="background: #ffb4ab; color: #690005; border: none; padding: 10px 24px; border-radius: 20px; font-weight: bold; cursor: pointer;">Đóng tab</button>
                </div>
            </body>
        </html>
        """, 400


@app.route("/auth/google/logout", methods=["POST", "OPTIONS"])
def google_auth_logout():
    if request.method == "OPTIONS":
        return response({})
    drive_service.logout_drive()
    return response({"status": "success", "message": "Đã ngắt kết nối Google Drive."})


if __name__ == "__main__":
    import traceback
    if sys.stdout is None:
        sys.stdout = open(LOGS_DIR / "startup.log", "a", encoding="utf-8")
    if sys.stderr is None:
        sys.stderr = open(LOGS_DIR / "error.log", "a", encoding="utf-8")
    try:
        app.run(host="127.0.0.1", port=37491, threaded=True, use_reloader=False)
    except Exception as e:
        with open(LOGS_DIR / "error.log", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
