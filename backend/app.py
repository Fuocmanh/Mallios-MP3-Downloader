"""Mallios local API for converting YouTube audio to MP3.

The server listens on localhost only. It is intended to be used by
the accompanying Chrome extension, never exposed as an internet-facing API.
"""

from __future__ import annotations

import gc
import json
import os
import re
import socket
import subprocess
import tempfile
import threading
import time
import unicodedata
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

try:
    import yt_dlp
    HAS_YTDLP_MODULE = True
except ImportError:
    HAS_YTDLP_MODULE = False
DEFAULT_DOWNLOAD_FOLDER = Path.home() / "Downloads"
CONFIGS_DIR = PROJECT_ROOT / "configs"
LOGS_DIR = PROJECT_ROOT / "logs"
CONFIGS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

TOOLS_DIR = PROJECT_ROOT / "tools"
FFMPEG_PATH = TOOLS_DIR
YTDLP_PATH = TOOLS_DIR / "yt-dlp.exe"
ARIA2C_PATH = TOOLS_DIR / "aria2c.exe"
FOLDER_PICKER_EXE = TOOLS_DIR / "FolderPicker.exe"
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
DRIVE_UPLOAD_SEMAPHORE = threading.Semaphore(2)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024


def is_allowed_origin(origin: str) -> bool:
    if not origin:
        return True
    origin_lower = origin.lower()
    if origin_lower.startswith("chrome-extension://"):
        return True
    try:
        parsed = urlparse(origin)
        host = (parsed.hostname or "").lower()
        if host in {"localhost", "127.0.0.1"} or host.endswith(".youtube.com") or host == "youtube.com" or host.endswith(".soundcloud.com") or host == "soundcloud.com":
            return True
    except Exception:
        pass
    return False


def apply_cors_headers(res):
    origin = request.headers.get("Origin", "")
    if is_allowed_origin(origin):
        res.headers["Access-Control-Allow-Origin"] = origin if origin else "*"
        res.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
        res.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        res.headers["Access-Control-Allow-Private-Network"] = "true"
        res.headers["Connection"] = "keep-alive"
        res.headers["Keep-Alive"] = "timeout=60, max=1000"
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
    cookies_file = CONFIGS_DIR / "cookies.txt"
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
    return response({
        "status": "online",
        "message": "Mallios MP3 server đang chạy.",
        "default_folder": str(DEFAULT_DOWNLOAD_FOLDER)
    })


@app.route("/api/default-folder", methods=["GET", "OPTIONS"])
def default_folder():
    if request.method == "OPTIONS":
        return response({"status": "ok"})
    return response({
        "status": "success",
        "default_folder": str(DEFAULT_DOWNLOAD_FOLDER)
    })


@app.route("/select-folder", methods=["POST", "OPTIONS"])
def select_folder():
    if request.method == "OPTIONS":
        return response({})

    req_data = request.get_json(silent=True) or {}
    initial_path = str(req_data.get("initial_path", "")).strip()
    title = str(req_data.get("title", "Chọn thư mục lưu nhạc MP3")).strip()

    # Tier 1: Sử dụng FolderPicker.exe hiện đại chuẩn Windows Explorer (IFileOpenDialog / FOS_PICKFOLDERS)
    if os.name == "nt" and FOLDER_PICKER_EXE.is_file():
        try:
            completed = subprocess.run(
                [str(FOLDER_PICKER_EXE), title, initial_path or str(DEFAULT_DOWNLOAD_FOLDER)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=180,
                creationflags=CREATE_NO_WINDOW
            )
            folder = completed.stdout.strip()
            if folder and os.path.exists(folder):
                return response({"status": "success", "path": str(Path(folder))})
            elif completed.returncode == 0:
                return response({"status": "cancel", "message": "Chưa chọn thư mục."})
        except Exception:
            pass

    # Tier 2: PowerShell IFileOpenDialog hiện đại
    if os.name == "nt":
        try:
            clean_title = title.replace('"', '\\"')
            clean_init = initial_path.replace('"', '\\"') if (initial_path and os.path.exists(initial_path)) else str(DEFAULT_DOWNLOAD_FOLDER).replace('"', '\\"')
            ps_code = f"""
            $code = @"
            using System;
            using System.Runtime.InteropServices;
            public class MPicker {{
                [DllImport("shell32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
                private static extern int SHCreateItemFromParsingName([MarshalAs(UnmanagedType.LPWStr)] string pszPath, IntPtr pbc, ref Guid riid, [MarshalAs(UnmanagedType.Interface)] out IShellItem ppv);
                [ComImport, Guid("DC1C5A9C-E88A-4dde-A5A1-60F82A20AEF7"), ClassInterface(ClassInterfaceType.None)]
                private class FileOpenDialogRCW {{ }}
                [ComImport, Guid("d57c5270-705d-44e8-83d7-f421f640e1bd"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
                private interface IFileOpenDialog {{
                    [PreserveSig] int Show(IntPtr parent);
                    void SetFileTypes(); void SetFileTypeIndex(); void GetFileTypeIndex(); void Advise(); void Unadvise();
                    void SetOptions(uint fos); void GetOptions(out uint fos); void SetDefaultFolder(IShellItem psi); void SetFolder(IShellItem psi);
                    void GetFolder(out IShellItem ppsi); void GetCurrentSelection(out IShellItem ppsi);
                    void SetFileName([MarshalAs(UnmanagedType.LPWStr)] string pszName); void GetFileName([MarshalAs(UnmanagedType.LPWStr)] out string pszName);
                    void SetTitle([MarshalAs(UnmanagedType.LPWStr)] string pszTitle); void SetOkButtonLabel([MarshalAs(UnmanagedType.LPWStr)] string pszText);
                    void SetFileNameLabel([MarshalAs(UnmanagedType.LPWStr)] string pszLabel); void GetResult(out IShellItem ppsi);
                    void AddPlace(IShellItem psi, int alignment); void SetDefaultExtension([MarshalAs(UnmanagedType.LPWStr)] string pszDefaultExtension);
                    void Close(int hr); void SetClientGuid(ref Guid guid); void ClearClientData(); void SetFilter([MarshalAs(UnmanagedType.Interface)] object pFilter);
                    void GetResults(out IntPtr ppenum); void GetSelectedItems(out IntPtr ppsai);
                }}
                [ComImport, Guid("43826D1E-E718-42EE-BC55-A1E261C37BFE"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
                private interface IShellItem {{
                    void BindToHandler(); void GetParent(); void GetDisplayName(uint sigdnName, [MarshalAs(UnmanagedType.LPWStr)] out string ppszName);
                    void GetAttributes(); void Compare();
                }}
                public static string Pick(string t, string init) {{
                    var d = (IFileOpenDialog)new FileOpenDialogRCW();
                    d.SetOptions(0x20 | 0x40);
                    if (!string.IsNullOrEmpty(t)) d.SetTitle(t);
                    if (!string.IsNullOrEmpty(init) && System.IO.Directory.Exists(init)) {{
                        var iid = new Guid("43826D1E-E718-42EE-BC55-A1E261C37BFE");
                        IShellItem item;
                        if (SHCreateItemFromParsingName(init, IntPtr.Zero, ref iid, out item) == 0) d.SetFolder(item);
                    }}
                    if (d.Show(IntPtr.Zero) == 0) {{
                        IShellItem res; d.GetResult(out res);
                        if (res != null) {{ string p; res.GetDisplayName(0x80058000, out p); return p; }}
                    }}
                    return "";
                }}
            }}
            "@
            Add-Type -TypeDefinition $code -Language CSharp
            [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
            Write-Output ([MPicker]::Pick("{clean_title}", "{clean_init}"))
            """
            completed = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", ps_code],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=180,
                creationflags=CREATE_NO_WINDOW
            )
            folder = completed.stdout.strip()
            if folder and os.path.exists(folder):
                return response({"status": "success", "path": str(Path(folder))})
            elif completed.returncode == 0:
                return response({"status": "cancel", "message": "Chưa chọn thư mục."})
        except Exception:
            pass

    # Tier 3: Fallback qua Tkinter
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        folder = filedialog.askdirectory(title=title, initialdir=initial_path or str(DEFAULT_DOWNLOAD_FOLDER))
        root.destroy()
        if folder and os.path.exists(folder):
            return response({"status": "success", "path": str(Path(folder))})
    except Exception:
        pass

    return response({"status": "cancel", "message": "Chưa chọn thư mục."})

@app.route("/get-playlist", methods=["POST", "OPTIONS"])
def get_playlist():
    if request.method == "OPTIONS":
        return response({})
    url = str((request.get_json(silent=True) or {}).get("url", "")).strip()
    if not is_valid_url(url):
        return response({"status": "error", "message": "Đường dẫn không hợp lệ."}, 400)

    try:
        args = ["--dump-single-json", "--extractor-args", "youtube:player_client=android,web"]
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
    
    # Nạp trước ngầm tối đa 6 bài đầu tiên để người dùng bấm nghe thử là phát tức thì
    try:
        urls_to_preload = [item["url"] for item in items if item.get("url")][:6]
        if urls_to_preload:
            background_preload_streams(urls_to_preload)
    except Exception:
        pass

    return response({"status": "success", "items": items})


def extract_playlist_links(playlist_url: str, max_files: int = 0) -> list[str]:
    # Phân tích danh sách phát để lấy danh sách URL video con
    base_arguments = [
        "--flat-playlist", "--dump-single-json",
        "--extractor-args", "youtube:player_client=android,web",
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
            cookies_file = CONFIGS_DIR / "cookies.txt"
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
    if not text:
        return ""
    text = text.replace("đ", "d").replace("Đ", "D")
    normalized = unicodedata.normalize("NFD", text)
    return "".join(c for c in normalized if unicodedata.category(c) != "Mn")


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


def normalize_title_for_check(text: str) -> str:
    """Chuẩn hóa tiêu đề bài hát / tên file (xóa đuôi .mp3, rác, dấu tiếng Việt, đưa về chữ thường) để so sánh trùng lặp."""
    clean = clean_video_title(str(text).replace(".mp3", ""))
    return remove_vietnamese_accents(clean).lower().strip()


def find_duplicate_file(save_folder: Path, clean_title: str) -> Path | None:
    # clean_title là tên file đã xóa dấu và làm sạch, ví dụ: "Hay Trao Cho Anh.mp3"
    target_stem = normalize_title_for_check(clean_title)
    
    try:
        # Quét các file ở thư mục gốc và thư mục con cấp 1
        files = list(save_folder.glob("*.mp3")) + list(save_folder.glob("*/*.mp3"))
        for f in files:
            if f.is_file():
                # Làm sạch và xóa dấu tên file trên đĩa để so sánh
                disk_stem = normalize_title_for_check(f.stem)
                
                # 1. So sánh khớp hoàn toàn (không phân biệt hoa thường, có dấu hay không dấu)
                if disk_stem == target_stem:
                    return f
                    
                # 2. Hỗ trợ trường hợp file trên đĩa có/không có tên ca sĩ ghép vào (ví dụ: "Son Tung M-TP - Hay Trao Cho Anh" vs "Hay Trao Cho Anh")
                # Xóa phần tên ca sĩ phía trước nếu có dấu gạch ngang " - "
                if " - " in disk_stem and disk_stem.split(" - ", 1)[1].strip() == target_stem:
                    return f
                if " - " in target_stem and target_stem.split(" - ", 1)[1].strip() == disk_stem:
                    return f
    except Exception:
        pass
        
    return None


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
    target_stem = normalize_title_for_check(clean_title)
    matches: list[Path] = []

    try:
        files = list(save_folder.glob("*.mp3")) + list(save_folder.glob("*/*.mp3"))
        for f in files:
            if not f.is_file():
                continue

            disk_stem = normalize_title_for_check(f.stem)
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


def run_single_download(link: str, quality: str, save_folder: Path, state_key: str, save_target: str = "local", options: dict = None):
    global PARALLEL_PROGRESS, MATCHING_DUPLICATE_FILES
    temp_dl_dir = None
    temp_drive_dir = None
    if options is None:
        options = {}
    enable_loudnorm = bool(options.get("enable_loudnorm", False))
    enable_sponsorblock = bool(options.get("enable_sponsorblock", False))
    embed_thumbnail = bool(options.get("embed_thumbnail", False))
    no_subfolder = bool(options.get("no_subfolder", False))
    skip_metadata = bool(options.get("skip_metadata", False))
    
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
    effective_save_folder = save_folder
    temp_drive_dir = None
    if save_target == "drive":
        # Tạo thư mục tạm cô lập trong AppData/Temp của Windows để tuyệt đối không tạo file trong thư mục người dùng
        temp_drive_dir = Path(tempfile.gettempdir()) / "mallios_cache" / "drive" / str(int(time.time())) / str(abs(hash(link)) % 10000000)
        temp_drive_dir.mkdir(parents=True, exist_ok=True)
        effective_save_folder = temp_drive_dir

    before_files = set()
    try:
        before_files = {
            str(p.resolve()) 
            for p in list(effective_save_folder.glob("*.mp3")) + list(effective_save_folder.glob("*/*.mp3"))
        }
    except Exception:
        pass

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["LANG"] = "en_US.UTF-8"

    # Thư mục chứa các phần tải tạm thời .part, .ytdl đặt trong AppData/Temp của Windows
    temp_dl_dir = Path(tempfile.gettempdir()) / "mallios_cache" / f"dl_{state_key}_{int(time.time() * 1000)}_{abs(hash(link)) % 10000}"
    temp_dl_dir.mkdir(parents=True, exist_ok=True)

    postprocessor_args = "ExtractAudio:-threads 0"
    if enable_loudnorm:
        postprocessor_args += " -af loudnorm=I=-16:TP=-1.5:LRA=11"

    output_template = "%(title)s.%(ext)s" if no_subfolder else "%(uploader)s/%(title)s.%(ext)s"

    arguments = [
        "--encoding", "utf-8",
        "--windows-filenames",
        "-f", "ba/18/b/best",
        "--extract-audio", "--audio-format", "mp3",
        "--audio-quality", quality,
        "--ffmpeg-location", str(FFMPEG_PATH),
        "--paths", f"temp:{temp_dl_dir}",
        "--paths", f"home:{effective_save_folder}",
        "--output", output_template,
        "--no-playlist",
        "--newline",
        "--no-color",
        "--concurrent-fragments", "10",
        "--buffer-size", "256K",
        "--http-chunk-size", "10M",
        "--no-mtime",
        "--force-ipv4",
        "--socket-timeout", "5",
        "--file-access-retries", "3",
        "--fragment-retries", "3",
        "--postprocessor-args", postprocessor_args
    ]
    
    if not skip_metadata:
        arguments.append("--add-metadata")
    
    if embed_thumbnail:
        arguments.append("--embed-thumbnail")
    
    is_youtube = any(host in link.lower() for host in YOUTUBE_HOSTS)
    if is_youtube:
        arguments.extend([
            "--extractor-args", "youtube:player_client=android"
        ])
        if enable_sponsorblock:
            arguments.extend([
                "--sponsorblock-remove", "music_offtopic,sponsor,selfpromo,intro,outro"
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
        # Nếu lỗi rate-limit -> chuyển sang client ios/mweb độc lập.
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
                        p_float = float(percent_match.group(1))
                        with PROGRESS_LOCK:
                            PARALLEL_PROGRESS[state_key]["started"] = True
                            PARALLEL_PROGRESS[state_key]["status"] = "downloading"
                            PARALLEL_PROGRESS[state_key]["percent"] = p_float
                            PARALLEL_PROGRESS[state_key]["message"] = f"Đang tải... {p_float:.1f}%"
                    except ValueError:
                        pass

                if "[ExtractAudio]" in line_str or "[ffmpeg]" in line_str or "[Metadata]" in line_str or "[ThumbnailsConvertor]" in line_str:
                    with PROGRESS_LOCK:
                        PARALLEL_PROGRESS[state_key]["started"] = True
                        PARALLEL_PROGRESS[state_key]["status"] = "converting"
                        PARALLEL_PROGRESS[state_key]["percent"] = 95.0
                        PARALLEL_PROGRESS[state_key]["message"] = "Đang nhúng bìa & chuyển MP3..."

            stdout_rem, stderr_data = process.communicate()
            returncode = process.returncode

            with ACTIVE_PROCESSES_LOCK:
                ACTIVE_PROCESSES.pop(state_key, None)

            combined_output = f"{stdout_rem}\n{stderr_data}"

            if returncode != 0 and not retried_auth:
                if is_cookie_auth_error(combined_output):
                    retried_auth = True
                    if refresh_cookies_from_browser():
                        arguments = [*base_download_args, "--cookies", str(CONFIGS_DIR / "cookies.txt")]
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
                            if arg != "--cookies" and arg != str(CONFIGS_DIR / "cookies.txt")
                        ]
                        with PROGRESS_LOCK:
                            PARALLEL_PROGRESS[state_key]["started"] = False
                            PARALLEL_PROGRESS[state_key]["percent"] = 0.0
                            PARALLEL_PROGRESS[state_key]["status"] = "downloading"
                            PARALLEL_PROGRESS[state_key]["message"] = "Không có browser, thử tải không cookie..."
                        continue
                elif any(phrase in combined_output for phrase in ["rate-limited", "This content isn't available", "Requested format", "403", "Forbidden", "Error opening output files"]):
                    retried_auth = True
                    # Chuyển sang format tương thích cao và client dự phòng
                    new_args = []
                    skip_next = False
                    for idx, arg in enumerate(arguments):
                        if skip_next:
                            skip_next = False
                            continue
                        if arg == "--extractor-args":
                            skip_next = True
                            continue
                        if arg == "-f":
                            new_args.extend(["-f", "ba/18/b/best"])
                            skip_next = True
                            continue
                        new_args.append(arg)
                    new_args.extend(["--extractor-args", "youtube:player_client=android,web", "--sleep-requests", "1"])
                    arguments = new_args
                    with PROGRESS_LOCK:
                        PARALLEL_PROGRESS[state_key]["started"] = False
                        PARALLEL_PROGRESS[state_key]["percent"] = 0.0
                        PARALLEL_PROGRESS[state_key]["status"] = "downloading"
                        PARALLEL_PROGRESS[state_key]["message"] = "Đang đổi phương thức tải dự phòng..."
                    continue

            break

        # Đổi tên file và thư mục để xóa dấu tiếng Việt sau khi hoàn thành tải xuống thành công
        if returncode in {0, 101}:
            try:
                # Quét lại danh sách file sau khi tải xong (chỉ quét thư mục gốc và thư mục con cấp 1)
                after_files = list(effective_save_folder.glob("*.*")) + list(effective_save_folder.glob("*/*.*"))
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
                            if original_parent != effective_save_folder:
                                clean_parent = original_parent.parent / clean_parent_name
                            else:
                                clean_parent = original_parent
                                
                            final_parent = original_parent
                            if original_parent != clean_parent:
                                if clean_parent.is_dir():
                                    final_parent = clean_parent
                                else:
                                    # Thêm cơ chế thử lại để tránh lỗi khóa tệp tạm thời trên Windows
                                    for attempt in range(10):
                                        try:
                                            original_parent.rename(clean_parent)
                                            final_parent = clean_parent
                                            # Cập nhật đường dẫn tệp sau khi thư mục cha bị đổi tên (tránh WinError 3)
                                            original_file = final_parent / original_file.name
                                            break
                                        except (PermissionError, OSError):
                                            if attempt < 9:
                                                time.sleep(1.0)
                                            else:
                                                raise
                                        
                            final_file_path = final_parent / clean_filename
                            if original_file != final_file_path:
                                if final_file_path.is_file():
                                    try:
                                        final_file_path.unlink()
                                    except Exception:
                                        pass
                                
                                # Thêm cơ chế thử lại đổi tên tệp (tránh WinError 32 và WinError 5)
                                for attempt in range(10):
                                    try:
                                        original_file.rename(final_file_path)
                                        break
                                    except (PermissionError, OSError):
                                        if attempt < 9:
                                            time.sleep(1.0)
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
                                PARALLEL_PROGRESS[state_key]["percent"] = 96.0
                                PARALLEL_PROGRESS[state_key]["message"] = "Đang nạp file vào bộ nhớ RAM..."

                            def on_drive_progress(pct, msg):
                                with PROGRESS_LOCK:
                                    PARALLEL_PROGRESS[state_key]["percent"] = pct
                                    PARALLEL_PROGRESS[state_key]["message"] = msg

                            # Đọc toàn bộ dữ liệu MP3 vào bộ nhớ RAM ảo
                            with open(final_file_path, "rb") as f_mp3:
                                mp3_bytes = f_mp3.read()

                            # Dọn dẹp xóa ngay lập tức file đĩa tạm trước khi bắt đầu upload
                            try:
                                if final_file_path.is_file():
                                    final_file_path.unlink()
                                if final_parent != effective_save_folder and final_parent.is_dir() and not any(final_parent.iterdir()):
                                    final_parent.rmdir()
                            except Exception:
                                pass

                            # Đẩy trực tiếp bytes từ RAM lên Drive với Semaphore giới hạn 2 upload đồng thời
                            with DRIVE_UPLOAD_SEMAPHORE:
                                drive_res = drive_service.upload_bytes_to_drive(
                                    mp3_bytes,
                                    clean_filename,
                                    clean_parent_name,
                                    progress_callback=on_drive_progress
                                )

                            # Giải phóng bộ nhớ RAM ngay lập tức
                            del mp3_bytes
                            gc.collect()

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
                
                PARALLEL_PROGRESS[state_key]["message"] = f"Lỗi: {clean_err}"
                
                error_msg = f"yt-dlp error code {returncode} for link {link}. Stderr: {stderr_data}"
                with open(LOGS_DIR / "error.log", "a", encoding="utf-8") as f:
                    f.write(f"\n--- SINGLE DOWNLOAD ERROR ---\n{error_msg}\n")
                
    except Exception as e:
        with PROGRESS_LOCK:
            PARALLEL_PROGRESS[state_key]["status"] = "failed"
            PARALLEL_PROGRESS[state_key]["percent"] = 0.0
            PARALLEL_PROGRESS[state_key]["message"] = str(e)
    finally:
        # Luôn luôn dọn sạch thư mục tạm của Drive trong mọi trường hợp
        if temp_drive_dir and temp_drive_dir.is_dir():
            try:
                shutil.rmtree(temp_drive_dir, ignore_errors=True)
            except Exception:
                pass
                
        # Dọn sạch thư mục tạm của yt-dlp (chứa các file .part, .webm chưa hoàn thành)
        if temp_dl_dir and temp_dl_dir.is_dir():
            try:
                shutil.rmtree(temp_dl_dir, ignore_errors=True)
            except Exception:
                pass
                
        if 'process' in locals() and process:
            try:
                if process.poll() is None:
                    subprocess.run(
                        f"taskkill /F /T /PID {process.pid}",
                        shell=True,
                        creationflags=CREATE_NO_WINDOW,
                        capture_output=True
                    )
                    process.kill()
            except Exception:
                pass

        with ACTIVE_PROCESSES_LOCK:
            if state_key in ACTIVE_PROCESSES:
                del ACTIVE_PROCESSES[state_key]


def cleanup_orphaned_processes():
    """Dọn dẹp an toàn các tiến trình tải con do Mallios quản lý."""
    with ACTIVE_PROCESSES_LOCK:
        for state_key, proc in list(ACTIVE_PROCESSES.items()):
            try:
                if proc.poll() is None:
                    subprocess.run(
                        f"taskkill /F /T /PID {proc.pid}",
                        shell=True,
                        creationflags=CREATE_NO_WINDOW,
                        capture_output=True
                    )
            except Exception:
                pass
        ACTIVE_PROCESSES.clear()


def cleanup_stray_temp_folders(folder: Path):
    """Xóa sạch mọi thư mục rác .temp_dl_* còn sót lại trong thư mục người dùng."""
    try:
        if folder and folder.is_dir():
            for p in list(folder.glob(".temp_dl_*")):
                if p.is_dir():
                    shutil.rmtree(p, ignore_errors=True)
            for p in list(folder.glob(".temp_drive*")):
                if p.is_dir():
                    shutil.rmtree(p, ignore_errors=True)
    except Exception:
        pass


def run_parallel_downloads_background(links: list[str], quality: str, save_folder: Path, max_files: int, save_target: str = "local", options: dict = None):
    global PROGRESS_STATE, PARALLEL_PROGRESS, CANCEL_REQUESTED, MATCHING_DUPLICATE_FILES

    CANCEL_REQUESTED = False
    MATCHING_DUPLICATE_FILES = []
    if options is None:
        options = {}
        
    cleanup_stray_temp_folders(save_folder)
    cleanup_stray_temp_folders(DEFAULT_DOWNLOAD_FOLDER)
    
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
            
    # Giới hạn luồng: 5 luồng cho local (tải cực nhanh), 3 luồng cho Drive (có Semaphore 2)
    max_workers = 5 if save_target == "local" else 3
    
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            for idx, link in enumerate(resolved_links):
                state_key = f"item_{idx}"
                fut = executor.submit(run_single_download, link, quality, save_folder, state_key, save_target, options)
                futures[fut] = state_key
                time.sleep(0.2)
                
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
                        elif state["status"] in {"downloading", "converting", "uploading"}:
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
    finally:
        with ACTIVE_PROCESSES_LOCK:
            ACTIVE_PROCESSES.clear()
        cleanup_orphaned_processes()
        cleanup_stray_temp_folders(save_folder)
        cleanup_stray_temp_folders(DEFAULT_DOWNLOAD_FOLDER)


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
@app.route("/download-parallel", methods=["POST", "OPTIONS"])
def download():
    if request.method == "OPTIONS":
        return response({})
        
    global PROGRESS_STATE
    with PROGRESS_LOCK:
        if PROGRESS_STATE["status"] == "running":
            return response({"status": "error", "message": "Có một tiến trình tải đang chạy. V vui lòng đợi."}, 400)
        
        # Reset trạng thái đồng bộ ngay lập tức để tránh tranh chấp (race condition) khi polling
        PROGRESS_STATE["status"] = "running"
        PROGRESS_STATE["percent"] = 0.0
        PROGRESS_STATE["message"] = "Đang khởi tạo tải..."
        PROGRESS_STATE["error"] = ""
            
    data = request.get_json(silent=True) or {}
    raw_links = data.get("links", []) or data.get("urls", [])
    if isinstance(raw_links, str):
        raw_links = [raw_links]
    links = normalize_links(raw_links)
    if not links:
        with PROGRESS_LOCK:
            PROGRESS_STATE["status"] = "failed"
            PROGRESS_STATE["error"] = "Không có link YouTube hợp lệ."
            PROGRESS_STATE["message"] = "Tải thất bại."
            
        return response({"status": "error", "message": "Hãy chọn ít nhất một link YouTube hợp lệ."}, 400)
 
    requested_path = str(data.get("download_path", "") or data.get("save_folder", "")).strip()
    save_target = str(data.get("save_target", "local")).strip().lower()
    if save_target != "drive":
        save_target = "local"

    requested_folder = Path(requested_path) if requested_path else None
    save_folder = requested_folder if requested_folder and requested_folder.is_dir() else DEFAULT_DOWNLOAD_FOLDER
    quality = str(data.get("quality", "0"))
    quality = quality if quality in VALID_QUALITIES else "0"
    max_files = data.get("max_files", 0)
    download_options = {
        "enable_loudnorm": bool(data.get("enable_loudnorm", False)),
        "enable_sponsorblock": bool(data.get("enable_sponsorblock", False)),
        "embed_thumbnail": bool(data.get("embed_thumbnail", False)),
        "no_subfolder": bool(data.get("no_subfolder", False)),
        "skip_metadata": bool(data.get("skip_metadata", False))
    }

    try:
        thread = threading.Thread(
            target=run_parallel_downloads_background,
            args=(links, quality, save_folder, max_files, save_target, download_options)
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
    download_options = {
        "enable_loudnorm": bool(data.get("enable_loudnorm", False)),
        "enable_sponsorblock": bool(data.get("enable_sponsorblock", False)),
        "embed_thumbnail": bool(data.get("embed_thumbnail", False)),
        "no_subfolder": bool(data.get("no_subfolder", False)),
        "skip_metadata": bool(data.get("skip_metadata", False))
    }
    
    # Khởi động tải song song cho các link bị lỗi
    with PROGRESS_LOCK:
        PROGRESS_STATE["status"] = "running"
        PROGRESS_STATE["percent"] = 0.0
        PROGRESS_STATE["message"] = f"Đang tải lại {len(failed_links)} bài hát bị lỗi..."
        PROGRESS_STATE["error"] = ""
        
    try:
        thread = threading.Thread(
            target=run_parallel_downloads_background,
            args=(failed_links, quality, save_folder, len(failed_links), save_target, download_options)
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
    cleanup_orphaned_processes()
        
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


@app.route("/sync-history", methods=["POST", "GET", "OPTIONS"])
def sync_history():
    if request.method == "OPTIONS":
        return response({})
        
    data = request.get_json(silent=True) or {}
    custom_path_str = str(data.get("download_path", "")).strip()
    folders_to_scan = [DEFAULT_DOWNLOAD_FOLDER]
    if custom_path_str:
        cp = Path(custom_path_str)
        if cp.is_dir() and cp != DEFAULT_DOWNLOAD_FOLDER:
            folders_to_scan.append(cp)

    # 1. Quét danh sách bài hát trên Google Drive (nếu đã kết nối)
    drive_files = []
    is_drive_scanned = False
    try:
        drive_files = drive_service.list_drive_music_files()
        if drive_files is not None and len(drive_files) > 0:
            is_drive_scanned = True
    except Exception:
        pass

    with HISTORY_LOCK:
        raw_history = load_history()
        history = []
        removed_count = 0

        drive_ids_on_cloud = {f["drive_file_id"] for f in drive_files if f.get("drive_file_id")}

        # 2. Kiểm tra các bài hát hiện có trong lịch sử (Xóa bài nếu file trên máy/Drive đã bị xóa)
        for item in raw_history:
            storage_type = item.get("storage_type", "local")
            if storage_type == "drive":
                # Nếu đã quét Drive thành công và có danh sách file
                if is_drive_scanned and drive_files:
                    item_drive_id = item.get("drive_file_id", "")
                    if item_drive_id and item_drive_id not in drive_ids_on_cloud:
                        # File trên Google Drive đã bị xóa vào thùng rác hoặc xóa vĩnh viễn!
                        removed_count += 1
                        continue
                history.append(item)
                continue

            fp_str = item.get("file_path", "")
            if not fp_str:
                removed_count += 1
                continue

            fp = Path(fp_str.replace("/", "\\"))
            if fp.is_file():
                history.append(item)
            else:
                # Tìm kiếm lại nếu file bị đổi tên/xóa dấu tiếng Việt
                found = False
                parent_dir = fp.parent
                if parent_dir.is_dir():
                    target_clean = remove_vietnamese_accents(fp.name).lower()
                    for f in parent_dir.glob("*.mp3"):
                        if remove_vietnamese_accents(f.name).lower() == target_clean:
                            item["file_path"] = str(f.resolve()).replace("\\", "/")
                            history.append(item)
                            found = True
                            break
                if not found:
                    # File thực sự không còn trên máy tính -> Loại bỏ khỏi lịch sử!
                    removed_count += 1

        existing_drive_ids = {item.get("drive_file_id") for item in history if item.get("drive_file_id")}
        existing_paths = {item.get("file_path", "").lower() for item in history if item.get("file_path")}
        existing_titles = {remove_vietnamese_accents(clean_video_title(item.get("title", ""))).lower().strip() for item in history if item.get("title")}

        added_count = 0

        # 3. Tự động thêm các bài mới tìm thấy trên Google Drive
        for df in drive_files:
            df_id = df.get("drive_file_id")
            clean_title_stem = remove_vietnamese_accents(clean_video_title(df.get("title", ""))).lower().strip()
            if df_id in existing_drive_ids or clean_title_stem in existing_titles:
                continue

            new_record = {
                "video_id": "",
                "url": "",
                "title": clean_video_title(df.get("title", "")),
                "uploader": df.get("uploader", "Mallios"),
                "file_path": "",
                "relative_path": df.get("filename", ""),
                "drive_file_id": df.get("drive_file_id", ""),
                "drive_web_link": df.get("drive_web_link", ""),
                "timestamp": df.get("timestamp", int(time.time())),
                "storage_type": "drive"
            }
            history.append(new_record)
            existing_drive_ids.add(df_id)
            existing_titles.add(clean_title_stem)
            added_count += 1

        # 4. Quét các file .mp3 trên ổ đĩa máy tính
        for folder in folders_to_scan:
            if not folder.is_dir():
                continue
            mp3_files = list(folder.glob("*.mp3")) + list(folder.glob("*/*.mp3")) + list(folder.glob("*/*/*.mp3"))
            for mp3_file in mp3_files:
                if not mp3_file.is_file():
                    continue
                file_path_str = str(mp3_file.resolve()).replace("\\", "/")
                file_path_lower = file_path_str.lower()
                clean_title_stem = remove_vietnamese_accents(clean_video_title(mp3_file.stem)).lower().strip()

                if file_path_lower in existing_paths or clean_title_stem in existing_titles:
                    continue

                uploader = mp3_file.parent.name if mp3_file.parent != folder else "Nghệ sĩ"
                title = mp3_file.stem
                try:
                    relative_path = str(mp3_file.resolve().relative_to(folder.resolve())).replace("\\", "/")
                except Exception:
                    relative_path = mp3_file.name

                try:
                    mtime = int(mp3_file.stat().st_mtime)
                except Exception:
                    mtime = int(time.time())

                new_record = {
                    "video_id": "",
                    "url": "",
                    "title": clean_video_title(title),
                    "uploader": uploader,
                    "file_path": file_path_str,
                    "relative_path": relative_path,
                    "timestamp": mtime,
                    "storage_type": "local"
                }
                history.append(new_record)
                existing_paths.add(file_path_lower)
                existing_titles.add(clean_title_stem)
                added_count += 1

        # Sắp xếp bài mới nhất lên đầu
        history.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        history = history[:200]
        save_history(history)

    return response({
        "status": "success",
        "added_count": added_count,
        "removed_count": removed_count,
        "history": history,
        "message": f"Đã đồng bộ {len(history)} bài hát (Thêm {added_count}, xóa {removed_count} bài không còn tồn tại)."
    })


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
PRELOAD_EXECUTOR = ThreadPoolExecutor(max_workers=8)
YTDLP_INSTANCE = None
YTDLP_INSTANCE_LOCK = threading.Lock()
LAST_COOKIE_MTIME = 0


def get_ytdlp_extractor():
    """Lấy hoặc khởi tạo instance YoutubeDL in-process với session tái sử dụng để giải mã stream trong < 1s."""
    global YTDLP_INSTANCE, LAST_COOKIE_MTIME
    cookies_file = CONFIGS_DIR / "cookies.txt"
    current_mtime = cookies_file.stat().st_mtime if cookies_file.is_file() else 0
    with YTDLP_INSTANCE_LOCK:
        if YTDLP_INSTANCE is None or current_mtime != LAST_COOKIE_MTIME:
            opts = {
                "format": "ba/18/b",
                "quiet": True,
                "no_warnings": True,
                "nocheckcertificate": True,
                "extractor_args": {"youtube": {"player_client": ["android"]}},
                "skip_download": True,
                "noplaylist": True,
            }
            if current_mtime > 0 and cookies_file.stat().st_size > 0:
                opts["cookiefile"] = str(cookies_file)
            try:
                YTDLP_INSTANCE = yt_dlp.YoutubeDL(opts)
                LAST_COOKIE_MTIME = current_mtime
            except Exception:
                pass
        return YTDLP_INSTANCE


def background_preload_streams(urls: list[str]):
    """Chạy ngầm nạp trước luồng âm thanh song song vào RAM để người dùng bấm nghe thử là phát tức thì."""
    if not urls:
        return
    for u in urls:
        if not u:
            continue
        with PREVIEW_CACHE_LOCK:
            if u in PREVIEW_STREAM_CACHE or u in IN_FLIGHT_FETCHES:
                continue
        try:
            PRELOAD_EXECUTOR.submit(get_direct_stream_url, u)
        except Exception:
            pass


def get_direct_stream_url(video_url: str) -> str:
    """Lấy direct audio stream URL từ yt-dlp với cache RAM, module in-process siêu tốc (<1s) và khóa chống nghẽn luồng."""
    if not video_url:
        return ""
    now = time.time()
    with PREVIEW_CACHE_LOCK:
        # TTL Eviction: Tự động dọn dẹp các cache quá hạn (14400s = 4 giờ)
        expired_keys = [k for k, v in PREVIEW_STREAM_CACHE.items() if now >= v[1]]
        for k in expired_keys:
            PREVIEW_STREAM_CACHE.pop(k, None)

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
        # Tier 1: In-process yt_dlp siêu tốc (mất ~0.5 - 0.9s, không tốn tài nguyên tạo process con)
        if HAS_YTDLP_MODULE:
            try:
                ydl = get_ytdlp_extractor()
                if ydl:
                    info = ydl.extract_info(video_url, download=False)
                    direct_url = info.get("url") if info else None
                    if direct_url and direct_url.startswith("http"):
                        with PREVIEW_CACHE_LOCK:
                            PREVIEW_STREAM_CACHE[video_url] = (direct_url, now + 14400)
                        return direct_url
            except Exception:
                pass

        # Tier 2: Fallback qua CLI subprocess yt-dlp.exe nếu Tier 1 gặp ngoại lệ
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["LANG"] = "en_US.UTF-8"
        
        base_cmd = [
            "-g", "-f", "ba/18/b",
            "--extractor-args", "youtube:player_client=android",
            "--no-playlist", "--no-warnings",
            video_url
        ]
        cmd = [str(YTDLP_PATH), *add_cookie_args(base_cmd)]
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
                        PREVIEW_STREAM_CACHE[video_url] = (direct_url, now + 14400)
                    return direct_url
        except Exception:
            pass
        return ""
    finally:
        with PREVIEW_CACHE_LOCK:
            if video_url in IN_FLIGHT_FETCHES:
                del IN_FLIGHT_FETCHES[video_url]
        event.set()


@app.route("/api/preview-info", methods=["GET", "POST", "OPTIONS"])
def preview_info():
    """Trả về JSON chứa direct_url của audio stream để frontend cache & phát trực tiếp không cần redirect."""
    if request.method == "OPTIONS":
        return response({})
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        video_url = data.get("url", "").strip()
    else:
        video_url = request.args.get("url", "").strip()
        
    if not video_url:
        return response({"status": "error", "message": "Thiếu tham số url."}, 400)

    direct_url = get_direct_stream_url(video_url)
    if not direct_url:
        return response({"status": "error", "message": "Không thể lấy luồng âm thanh nghe thử."}, 500)

    return response({"status": "success", "direct_url": direct_url})


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


@app.route("/api/preload-playlist", methods=["POST", "OPTIONS"])
def preload_playlist():
    """Nạp trước ngầm luồng âm thanh của các bài hát trong danh sách để nghe thử tức thì."""
    if request.method == "OPTIONS":
        return response({"status": "ok"})
    data = request.get_json(silent=True) or {}
    urls = data.get("urls", [])
    if isinstance(urls, list) and urls:
        # Nạp trước tối đa 15 bài đầu tiên vào RAM cache song song
        background_preload_streams(urls[:15])
    return response({"status": "success"})


@app.route("/api/sync-cookies", methods=["POST", "OPTIONS"])
def sync_cookies():
    """Nhận và cập nhật tệp cookies.txt trực tiếp từ phiên đăng nhập trình duyệt của Extension."""
    if request.method == "OPTIONS":
        return response({"status": "ok"})
    data = request.get_json(silent=True) or {}
    cookies_content = data.get("cookies_content", "").strip()
    if cookies_content:
        cookie_path = CONFIGS_DIR / "cookies.txt"
        try:
            with open(cookie_path, "w", encoding="utf-8") as f:
                f.write(cookies_content)
            return response({"status": "success", "message": "Đã cập nhật cookies thành công!"})
        except Exception as e:
            return response({"status": "error", "message": str(e)}, 500)
    return response({"status": "error", "message": "Nội dung cookie trống."}, 400)


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


def get_lan_ip() -> str:
    """Lấy địa chỉ IP nội bộ của máy tính trong mạng Wi-Fi/LAN để phát nhạc sang điện thoại."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


@app.route("/api/local-ip", methods=["GET", "OPTIONS"])
def get_local_ip():
    if request.method == "OPTIONS":
        return response({"status": "ok"})
    return response({
        "status": "success",
        "ip": get_lan_ip(),
        "port": 37491
    })


@app.route("/api/check-duplicates-batch", methods=["POST", "OPTIONS"])
def check_duplicates_batch():
    """Kiểm tra hàng loạt danh sách URL xem bài nào đã tồn tại trong thư mục lưu hoặc lịch sử."""
    if request.method == "OPTIONS":
        return response({"status": "ok"})
    data = request.get_json(silent=True) or {}
    urls = data.get("urls", [])
    raw_folder = str(data.get("save_folder", "")).strip()
    save_target = str(data.get("save_target", "local")).strip()

    requested_folder = Path(raw_folder) if raw_folder else None
    save_folder = requested_folder if requested_folder and requested_folder.is_dir() else DEFAULT_DOWNLOAD_FOLDER
    history_records = load_history()

    results = {}
    if save_target == "drive":
        drive_history_urls = set()
        drive_history_vids = set()
        for item in history_records:
            if item.get("storage_type") == "drive":
                u = item.get("url", "")
                if u:
                    drive_history_urls.add(u.split("&")[0].strip())
                vid = item.get("video_id") or extract_youtube_video_id(u)
                if vid:
                    drive_history_vids.add(vid)
        for u in urls:
            norm_u = u.split("&")[0].strip()
            vid = extract_youtube_video_id(u)
            results[u] = (norm_u in drive_history_urls) or (bool(vid) and vid in drive_history_vids)
        return response({"status": "success", "duplicates": results})

    # Nếu lưu trên máy, kết hợp quét lịch sử và quét file thực tế trên ổ cứng
    existing_files_normalized = set()
    if save_folder and save_folder.is_dir():
        try:
            for p in list(save_folder.glob("*.mp3")) + list(save_folder.glob("*/*.mp3")):
                norm_name = normalize_title_for_check(p.stem)
                existing_files_normalized.add(norm_name)
                if " - " in norm_name:
                    existing_files_normalized.add(norm_name.split(" - ", 1)[1].strip())
        except Exception:
            pass

    history_local_urls = set()
    history_local_vids = set()
    for item in history_records:
        if item.get("storage_type", "local") == "local":
            u = item.get("url", "")
            if u:
                history_local_urls.add(u.split("&")[0].strip())
            vid = item.get("video_id") or extract_youtube_video_id(u)
            if vid:
                history_local_vids.add(vid)

    for u in urls:
        norm_u = u.split("&")[0].strip()
        vid = extract_youtube_video_id(u)
        is_dup = (norm_u in history_local_urls) or (bool(vid) and vid in history_local_vids)
        results[u] = is_dup

    return response({"status": "success", "duplicates": results})


def auto_update_ytdlp_background():
    """Tự động kiểm tra và cập nhật yt-dlp lên bản mới nhất trong nền khi khởi động."""
    try:
        time.sleep(5)
        if YTDLP_PATH.is_file():
            subprocess.run(
                [str(YTDLP_PATH), "-U", "--no-check-certificate"],
                creationflags=CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=45
            )
    except Exception:
        pass

threading.Thread(target=auto_update_ytdlp_background, daemon=True).start()


if __name__ == "__main__":
    import traceback
    if sys.stdout is None:
        sys.stdout = open(LOGS_DIR / "startup.log", "a", encoding="utf-8")
    if sys.stderr is None:
        sys.stderr = open(LOGS_DIR / "error.log", "a", encoding="utf-8")
    try:
        cleanup_orphaned_processes()
        app.run(host="0.0.0.0", port=37491, threaded=True, use_reloader=False)
    except Exception as e:
        with open(LOGS_DIR / "error.log", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
