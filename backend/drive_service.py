"""Module quản lý tương tác với Google Drive cho Mallios MP3 Downloader.

Hỗ trợ 2 phương thức:
1. Google Apps Script Web App (Cách 2: Cực kỳ đơn giản, chỉ cần dán 1 link Web App).
2. Google OAuth 2.0 API v3.
"""

from __future__ import annotations

import base64
import json
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIGS_DIR = PROJECT_ROOT / "configs"
CONFIGS_DIR.mkdir(exist_ok=True)

DRIVE_AUTH_FILE = CONFIGS_DIR / "drive_auth.json"
DRIVE_CONFIG_FILE = CONFIGS_DIR / "drive_config.json"

DRIVE_LOCK = threading.Lock()

DEFAULT_OAUTH_CONFIG = {
    "client_id": "",
    "client_secret": "",
    "redirect_uri": "http://127.0.0.1:37491/auth/google/callback",
    "auth_uri": "https://accounts.google.com/o/oauth2/v2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "userinfo_uri": "https://www.googleapis.com/oauth2/v2/userinfo",
    "scopes": [
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/userinfo.email"
    ]
}


def load_config() -> dict:
    """Tải cấu hình OAuth Client ID & Secret."""
    config = DEFAULT_OAUTH_CONFIG.copy()
    example_file = CONFIGS_DIR / "drive_config.example.json"
    
    # Nếu chưa có drive_config.json nhưng có file example, tự động tạo drive_config.json từ mẫu
    if not DRIVE_CONFIG_FILE.is_file() and example_file.is_file():
        try:
            shutil.copy2(example_file, DRIVE_CONFIG_FILE)
        except Exception:
            pass

    if DRIVE_CONFIG_FILE.is_file():
        try:
            with open(DRIVE_CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                if isinstance(saved, dict):
                    config.update(saved)
        except Exception:
            pass
    return config


def save_config(config_data: dict):
    """Lưu cấu hình OAuth Client ID & Secret."""
    try:
        with open(DRIVE_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def load_auth() -> dict:
    """Tải thông tin token và tài khoản đã xác thực."""
    if not DRIVE_AUTH_FILE.is_file():
        return {}
    try:
        with open(DRIVE_AUTH_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_auth(auth_data: dict):
    """Lưu thông tin token và tài khoản."""
    try:
        with open(DRIVE_AUTH_FILE, "w", encoding="utf-8") as f:
            json.dump(auth_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def get_script_url() -> str:
    """Lấy Web App URL của Google Apps Script nếu có."""
    auth = load_auth()
    return auth.get("script_url", "").strip()


def set_script_url(script_url: str) -> tuple[bool, str, dict]:
    """Lưu và kiểm tra Google Apps Script Web App URL."""
    url = script_url.strip()
    if not url:
        return False, "Vui lòng nhập đường dẫn Google Apps Script Web App.", {}
    if not url.startswith("https://script.google.com/macros/s/"):
        return False, "Đường dẫn không hợp lệ. Phải bắt đầu bằng https://script.google.com/macros/s/...", {}

    if "/edit" in url:
        return False, "Đường dẫn bạn dán là link chỉnh sửa script (/edit). Vui lòng bấm nút 'Triển khai' (Deploy) -> 'Ứng dụng web' để lấy link kết thúc bằng /exec!", {}

    # Thử kiểm tra kết nối với Apps Script
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            content = resp.read().decode("utf-8", errors="replace")
            if "accounts.google.com" in content:
                return False, "Google Apps Script yêu cầu đăng nhập. Hãy chỉnh: 'Ai có quyền truy cập' (Who has access) là 'Bất kỳ ai' (Anyone).", {}
    except urllib.error.HTTPError as he:
        return False, f"Lỗi HTTP {he.code} từ Google Apps Script. Vui lòng kiểm tra lại quyền triển khai.", {}
    except Exception:
        pass

    with DRIVE_LOCK:
        auth = load_auth()
        auth["script_url"] = url
        auth["method"] = "apps_script"
        auth["folder_name"] = auth.get("folder_name", "Mallios Music")
        auth["email"] = "Google Apps Script"
        auth["updated_at"] = time.time()
        save_auth(auth)

    return True, "Đã kết nối Google Drive qua Apps Script thành công!", auth


def is_connected() -> bool:
    """Kiểm tra xem người dùng đã kết nối Google Drive chưa."""
    auth = load_auth()
    if auth.get("script_url"):
        return True
    return bool(auth.get("refresh_token") or auth.get("access_token"))


def get_account_status() -> dict:
    """Lấy thông tin trạng thái tài khoản Google Drive hiện tại."""
    config = load_config()
    auth = load_auth()
    script_url = auth.get("script_url", "").strip()
    connected = is_connected()
    
    if script_url:
        email = "Google Apps Script"
        method = "apps_script"
    else:
        email = auth.get("email", "")
        method = "oauth"

    folder_name = auth.get("folder_name", "Mallios Music")
    has_client_credentials = bool(config.get("client_id") and config.get("client_secret"))

    return {
        "connected": connected,
        "email": email,
        "folder_name": folder_name,
        "script_url": script_url,
        "method": method,
        "has_client_credentials": has_client_credentials,
        "client_id": config.get("client_id", "")
    }


def logout_drive() -> bool:
    """Xóa thông tin kết nối Google Drive."""
    with DRIVE_LOCK:
        try:
            if DRIVE_AUTH_FILE.is_file():
                DRIVE_AUTH_FILE.unlink()
            return True
        except Exception:
            return False


def set_direct_token(access_token: str, expires_in: int = 3600) -> tuple[bool, str, dict]:
    """Lưu Access Token nhận trực tiếp từ Chrome Extension (chrome.identity)."""
    if not access_token:
        return False, "Thiếu Access Token.", {}

    config = load_config()
    email = ""
    try:
        userinfo_req = urllib.request.Request(
            config["userinfo_uri"],
            headers={"Authorization": f"Bearer {access_token}"}
        )
        with urllib.request.urlopen(userinfo_req, timeout=15) as u_resp:
            userinfo = json.loads(u_resp.read().decode("utf-8"))
            email = userinfo.get("email", "")
    except Exception as e:
        return False, f"Không thể xác thực token với Google: {e}", {}

    with DRIVE_LOCK:
        current_auth = load_auth()
        auth_info = {
            "access_token": access_token,
            "refresh_token": current_auth.get("refresh_token", ""),
            "expires_at": time.time() + float(expires_in) - 60,
            "email": email or current_auth.get("email", ""),
            "folder_name": current_auth.get("folder_name", "Mallios Music"),
            "method": "oauth",
            "updated_at": time.time()
        }
        save_auth(auth_info)

    return True, "Kết nối Google Drive thành công!", auth_info


def get_auth_url() -> str:
    """Tạo URL để người dùng đăng nhập OAuth 2.0 trên trình duyệt."""
    config = load_config()
    client_id = config.get("client_id", "").strip()
    if not client_id:
        raise ValueError("Chưa cấu hình Google OAuth Client ID.")

    params = {
        "client_id": client_id,
        "redirect_uri": config.get("redirect_uri", "http://127.0.0.1:37491/auth/google/callback"),
        "response_type": "code",
        "scope": " ".join(config.get("scopes", DEFAULT_OAUTH_CONFIG["scopes"])),
        "access_type": "offline",
        "prompt": "consent",
        "include_granted_scopes": "true"
    }
    return f"{config['auth_uri']}?{urllib.parse.urlencode(params)}"


def exchange_code_for_token(code: str) -> tuple[bool, str, dict]:
    """Đổi Authorization Code lấy Access Token và Refresh Token."""
    config = load_config()
    client_id = config.get("client_id", "").strip()
    client_secret = config.get("client_secret", "").strip()
    redirect_uri = config.get("redirect_uri", "http://127.0.0.1:37491/auth/google/callback")

    if not client_id or not client_secret:
        return False, "Thiếu Google OAuth Client ID hoặc Client Secret.", {}

    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }

    try:
        encoded_data = urllib.parse.urlencode(data).encode("utf-8")
        req = urllib.request.Request(
            config["token_uri"],
            data=encoded_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            token_res = json.loads(resp.read().decode("utf-8"))

        access_token = token_res.get("access_token")
        refresh_token = token_res.get("refresh_token")
        expires_in = token_res.get("expires_in", 3600)
        expires_at = time.time() + float(expires_in) - 60

        if not access_token:
            return False, "Không nhận được Access Token từ Google.", {}

        email = ""
        try:
            userinfo_req = urllib.request.Request(
                config["userinfo_uri"],
                headers={"Authorization": f"Bearer {access_token}"}
            )
            with urllib.request.urlopen(userinfo_req, timeout=15) as u_resp:
                userinfo = json.loads(u_resp.read().decode("utf-8"))
                email = userinfo.get("email", "")
        except Exception:
            pass

        with DRIVE_LOCK:
            current_auth = load_auth()
            auth_info = {
                "access_token": access_token,
                "refresh_token": refresh_token or current_auth.get("refresh_token", ""),
                "expires_at": expires_at,
                "email": email or current_auth.get("email", ""),
                "folder_name": current_auth.get("folder_name", "Mallios Music"),
                "method": "oauth",
                "updated_at": time.time()
            }
            save_auth(auth_info)

        return True, "Xác thực Google Drive thành công!", auth_info
    except Exception as e:
        return False, f"Lỗi đổi mã xác thực: {e}", {}


def get_valid_access_token() -> str | None:
    """Lấy Access Token hợp lệ, tự động refresh nếu đã hết hạn."""
    with DRIVE_LOCK:
        auth = load_auth()
        access_token = auth.get("access_token")
        refresh_token = auth.get("refresh_token")
        expires_at = auth.get("expires_at", 0)

        if not access_token and not refresh_token:
            return None

        if access_token and time.time() < (expires_at - 60):
            return access_token

        if not refresh_token:
            return access_token

        config = load_config()
        client_id = config.get("client_id", "").strip()
        client_secret = config.get("client_secret", "").strip()

        if not client_id or not client_secret:
            return access_token

        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }

        try:
            encoded_data = urllib.parse.urlencode(data).encode("utf-8")
            req = urllib.request.Request(
                config["token_uri"],
                data=encoded_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                token_res = json.loads(resp.read().decode("utf-8"))

            new_access_token = token_res.get("access_token")
            expires_in = token_res.get("expires_in", 3600)

            if new_access_token:
                auth["access_token"] = new_access_token
                auth["expires_at"] = time.time() + float(expires_in) - 60
                auth["updated_at"] = time.time()
                save_auth(auth)
                return new_access_token
        except Exception:
            pass

        return access_token


def upload_bytes_via_apps_script(
    script_url: str,
    file_bytes: bytes,
    filename: str,
    artist_name: str = "",
    progress_callback = None
) -> dict:
    """Tải chuỗi bytes MP3 trực tiếp từ RAM lên Google Drive qua Apps Script với cơ chế Auto-Retry."""
    if not file_bytes:
        raise ValueError("Dữ liệu MP3 rỗng, không thể tải lên Google Drive.")

    if progress_callback:
        progress_callback(96.0, "Đang chuẩn bị dữ liệu MP3 từ bộ nhớ RAM...")

    b64_content = base64.b64encode(file_bytes).decode("utf-8")

    payload = {
        "filename": filename,
        "artist": artist_name.strip() if artist_name else "Mallios",
        "base64": b64_content
    }

    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        script_url,
        data=req_data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
    )

    max_retries = 3
    last_error = None

    for attempt in range(1, max_retries + 1):
        if progress_callback:
            retry_msg = f" (Lần thử {attempt}/{max_retries})" if attempt > 1 else ""
            progress_callback(97.0, f"Đang đẩy file lên Google Drive qua Apps Script{retry_msg}...")

        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                res_text = resp.read().decode("utf-8", errors="replace")
                try:
                    res_json = json.loads(res_text)
                except Exception:
                    if "accounts.google.com" in res_text:
                        raise RuntimeError("Google Apps Script yêu cầu đăng nhập. Vui lòng cài quyền 'Ai có quyền truy cập' (Who has access) là 'Bất kỳ ai' (Anyone).")
                    raise RuntimeError(f"Phản hồi từ Google Apps Script không hợp lệ: {res_text[:200]}")

            if res_json.get("status") != "success":
                raise RuntimeError(res_json.get("message", "Lỗi không xác định từ Google Apps Script."))

            file_id = res_json.get("file_id", "")
            view_url = res_json.get("url") or res_json.get("view_url") or (f"https://drive.google.com/file/d/{file_id}/view" if file_id else "https://drive.google.com")

            if progress_callback:
                progress_callback(100.0, "Hoàn tất lưu trên Google Drive.")

            return {
                "id": file_id,
                "name": filename,
                "webViewLink": view_url
            }

        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as e:
            last_error = e
            if attempt < max_retries:
                backoff_time = 1  # 1s nhanh gọn
                if progress_callback:
                    progress_callback(97.0, "Mạng bận, đang thử lại...")
                time.sleep(backoff_time)
            else:
                if isinstance(e, urllib.error.HTTPError):
                    raise RuntimeError(f"Lỗi HTTP từ Google Apps Script ({e.code}): {e.reason}")
                elif isinstance(e, urllib.error.URLError):
                    raise RuntimeError(f"Không thể kết nối tới Google Apps Script sau {max_retries} lần thử: {e.reason}")
                else:
                    raise RuntimeError(f"Lỗi kết nối tới Google Apps Script: {e}")

    raise RuntimeError(f"Không thể tải file lên Google Drive: {last_error}")


def upload_via_apps_script(
    script_url: str,
    file_path: Path,
    filename: str,
    artist_name: str = "",
    progress_callback = None
) -> dict:
    """Tải file MP3 từ ổ đĩa lên Google Drive thông qua Google Apps Script Web App."""
    if not file_path.is_file():
        raise FileNotFoundError(f"Không tìm thấy file MP3 để tải lên: {file_path}")

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    return upload_bytes_via_apps_script(
        script_url=script_url,
        file_bytes=file_bytes,
        filename=filename,
        artist_name=artist_name,
        progress_callback=progress_callback
    )


def upload_bytes_to_drive(
    file_bytes: bytes,
    filename: str,
    artist_name: str = "",
    progress_callback = None
) -> dict:
    """
    Tải chuỗi bytes MP3 trực tiếp từ RAM lên Google Drive theo cấu trúc: Mallios Music / <Artist> / <Song.mp3>.
    Tự động chọn giữa Apps Script Web App hoặc OAuth 2.0 API mà không cần ghi ra đĩa.
    """
    if not file_bytes:
        raise ValueError("Dữ liệu MP3 rỗng, không thể tải lên Google Drive.")

    auth = load_auth()
    script_url = auth.get("script_url", "").strip()

    # 1. Nếu dùng Google Apps Script Web App
    if script_url:
        return upload_bytes_via_apps_script(
            script_url=script_url,
            file_bytes=file_bytes,
            filename=filename,
            artist_name=artist_name,
            progress_callback=progress_callback
        )

    # 2. Nếu dùng OAuth 2.0
    token = get_valid_access_token()
    if not token:
        raise RuntimeError("Chưa kết nối Google Drive. Vui lòng dán Web App URL hoặc kết nối tài khoản.")

    root_folder_name = auth.get("folder_name", "Mallios Music")

    # Tìm/Tạo thư mục
    root_folder_id = get_or_create_folder(root_folder_name)
    target_folder_id = root_folder_id

    if artist_name and artist_name.strip():
        target_folder_id = get_or_create_folder(artist_name.strip(), parent_id=root_folder_id)

    # Resumable upload
    init_url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable"
    metadata = {
        "name": filename,
        "mimeType": "audio/mpeg",
        "parents": [target_folder_id]
    }

    total_size = len(file_bytes)
    init_req = urllib.request.Request(
        init_url,
        data=json.dumps(metadata).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=UTF-8",
            "X-Upload-Content-Type": "audio/mpeg",
            "X-Upload-Content-Length": str(total_size)
        }
    )

    with urllib.request.urlopen(init_req, timeout=30) as resp:
        upload_location = resp.headers.get("Location")

    if not upload_location:
        raise RuntimeError("Không lấy được URL khởi tạo Resumable Upload từ Google Drive.")

    chunk_size = 2 * 1024 * 1024
    bytes_sent = 0
    while bytes_sent < total_size:
        chunk = file_bytes[bytes_sent:bytes_sent + chunk_size]
        chunk_len = len(chunk)
        range_header = f"bytes {bytes_sent}-{bytes_sent + chunk_len - 1}/{total_size}"

        req_chunk = urllib.request.Request(
            upload_location,
            data=chunk,
            headers={
                "Content-Range": range_header,
                "Content-Type": "audio/mpeg"
            },
            method="PUT"
        )

        try:
            with urllib.request.urlopen(req_chunk, timeout=60) as chunk_resp:
                if chunk_resp.status in {200, 201}:
                    result_data = json.loads(chunk_resp.read().decode("utf-8"))
                    file_id = result_data.get("id")
                    web_view_link = f"https://drive.google.com/file/d/{file_id}/view"
                    
                    if progress_callback:
                        progress_callback(100.0, "Hoàn tất lưu trên Google Drive.")

                    return {
                        "id": file_id,
                        "name": filename,
                        "webViewLink": web_view_link,
                        "folder_id": target_folder_id
                    }
        except urllib.error.HTTPError as http_err:
            if http_err.code == 308:
                bytes_sent += chunk_len
                if progress_callback:
                    percent = min(99.0, round((bytes_sent / total_size) * 100.0, 1))
                    progress_callback(percent, f"Đang upload lên Drive ({percent}%)...")
            else:
                raise

        bytes_sent += chunk_len
        if progress_callback:
            percent = min(99.0, round((bytes_sent / total_size) * 100.0, 1))
            progress_callback(percent, f"Đang upload lên Drive ({percent}%)...")

    return {}


def upload_mp3_to_drive(
    file_path: Path,
    filename: str,
    artist_name: str = "",
    progress_callback = None
) -> dict:
    """
    Tải file MP3 lên Google Drive theo cấu trúc: Mallios Music / <Artist> / <Song.mp3>.
    Tự động chọn giữa Apps Script Web App hoặc OAuth 2.0 API.
    """
    if not file_path.is_file():
        raise FileNotFoundError(f"Không tìm thấy file để upload: {file_path}")

    auth = load_auth()
    script_url = auth.get("script_url", "").strip()

    # 1. Nếu dùng Google Apps Script Web App
    if script_url:
        return upload_via_apps_script(
            script_url=script_url,
            file_path=file_path,
            filename=filename,
            artist_name=artist_name,
            progress_callback=progress_callback
        )

    # 2. Nếu dùng OAuth 2.0
    token = get_valid_access_token()
    if not token:
        raise RuntimeError("Chưa kết nối Google Drive. Vui lòng dán Web App URL hoặc kết nối tài khoản.")

    root_folder_name = auth.get("folder_name", "Mallios Music")

    # Tìm/Tạo thư mục
    root_folder_id = get_or_create_folder(root_folder_name)
    target_folder_id = root_folder_id

    if artist_name and artist_name.strip():
        target_folder_id = get_or_create_folder(artist_name.strip(), parent_id=root_folder_id)

    # Resumable upload
    init_url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable"
    metadata = {
        "name": filename,
        "mimeType": "audio/mpeg",
        "parents": [target_folder_id]
    }

    init_req = urllib.request.Request(
        init_url,
        data=json.dumps(metadata).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=UTF-8",
            "X-Upload-Content-Type": "audio/mpeg",
            "X-Upload-Content-Length": str(file_path.stat().st_size)
        }
    )

    with urllib.request.urlopen(init_req, timeout=30) as resp:
        upload_location = resp.headers.get("Location")

    if not upload_location:
        raise RuntimeError("Không lấy được URL khởi tạo Resumable Upload từ Google Drive.")

    total_size = file_path.stat().st_size
    chunk_size = 2 * 1024 * 1024

    with open(file_path, "rb") as f:
        bytes_sent = 0
        while bytes_sent < total_size:
            chunk = f.read(chunk_size)
            chunk_len = len(chunk)
            range_header = f"bytes {bytes_sent}-{bytes_sent + chunk_len - 1}/{total_size}"

            req_chunk = urllib.request.Request(
                upload_location,
                data=chunk,
                headers={
                    "Content-Range": range_header,
                    "Content-Type": "audio/mpeg"
                },
                method="PUT"
            )

            try:
                with urllib.request.urlopen(req_chunk, timeout=60) as chunk_resp:
                    if chunk_resp.status in {200, 201}:
                        result_data = json.loads(chunk_resp.read().decode("utf-8"))
                        file_id = result_data.get("id")
                        web_view_link = f"https://drive.google.com/file/d/{file_id}/view"
                        
                        if progress_callback:
                            progress_callback(100.0, "Hoàn tất lưu trên Google Drive.")

                        return {
                            "id": file_id,
                            "name": filename,
                            "webViewLink": web_view_link,
                            "folder_id": target_folder_id
                        }
            except urllib.error.HTTPError as http_err:
                if http_err.code == 308:
                    bytes_sent += chunk_len
                    if progress_callback:
                        percent = min(99.0, round((bytes_sent / total_size) * 100.0, 1))
                        progress_callback(percent, f"Đang upload lên Drive ({percent}%)...")
                else:
                    raise

            bytes_sent += chunk_len
            if progress_callback:
                percent = min(99.0, round((bytes_sent / total_size) * 100.0, 1))
                progress_callback(percent, f"Đang upload lên Drive ({percent}%)...")

    return {}


def get_or_create_folder(folder_name: str, parent_id: str | None = None) -> str | None:
    token = get_valid_access_token()
    if not token:
        raise RuntimeError("Chưa đăng nhập Google Drive.")

    safe_name = folder_name.replace("'", "\\'")
    query = f"mimeType='application/vnd.google-apps.folder' and name='{safe_name}' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    search_url = f"https://www.googleapis.com/drive/v3/files?q={urllib.parse.quote(query)}&fields=files(id,name)"
    req = urllib.request.Request(search_url, headers={"Authorization": f"Bearer {token}"})

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            files = data.get("files", [])
            if files:
                return files[0]["id"]
    except Exception:
        pass

    create_url = "https://www.googleapis.com/drive/v3/files"
    metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder"
    }
    if parent_id:
        metadata["parents"] = [parent_id]

    req_create = urllib.request.Request(
        create_url,
        data=json.dumps(metadata).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )

    with urllib.request.urlopen(req_create, timeout=20) as resp:
        res_data = json.loads(resp.read().decode("utf-8"))
        return res_data.get("id")


def list_drive_music_files() -> list[dict]:
    """
    Quét và trả về danh sách tất cả các bài hát MP3 đang có trên Google Drive trong thư mục Mallios Music.
    Hỗ trợ cả Google Apps Script Web App lẫn OAuth 2.0.
    """
    auth = load_auth()
    script_url = auth.get("script_url", "").strip()

    # 1. Quét qua Google Apps Script Web App
    if script_url:
        try:
            url = f"{script_url}?action=list"
            req = urllib.request.Request(url, headers={"User-Agent": "Mallios-MP3/3.7"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("status") == "success":
                    files = data.get("files", [])
                    result = []
                    for f in files:
                        raw_name = f.get("name", "")
                        title = raw_name[:-4] if raw_name.lower().endswith(".mp3") else raw_name
                        artist = f.get("artist") or "Mallios"
                        file_id = f.get("id", "")
                        web_link = f.get("url") or f"https://drive.google.com/file/d/{file_id}/view"
                        updated_ts = int(f.get("updated", 0) / 1000) if f.get("updated") else int(time.time())
                        result.append({
                            "drive_file_id": file_id,
                            "drive_web_link": web_link,
                            "title": title,
                            "uploader": artist,
                            "filename": raw_name,
                            "timestamp": updated_ts,
                            "storage_type": "drive"
                        })
                    return result
        except Exception:
            return []

    # 2. Quét qua OAuth 2.0 API
    token = get_valid_access_token()
    if not token:
        return []

    try:
        root_folder_name = auth.get("folder_name", "Mallios Music")
        root_folder_id = get_or_create_folder(root_folder_name)
        if not root_folder_id:
            return []

        # Lấy tất cả thư mục con (các ca sĩ)
        q_folders = f"mimeType='application/vnd.google-apps.folder' and '{root_folder_id}' in parents and trashed=false"
        url_folders = f"https://www.googleapis.com/drive/v3/files?q={urllib.parse.quote(q_folders)}&fields=files(id,name)"
        req_folders = urllib.request.Request(url_folders, headers={"Authorization": f"Bearer {token}"})
        
        folder_map = {root_folder_id: "Mallios"}
        with urllib.request.urlopen(req_folders, timeout=8) as resp:
            f_data = json.loads(resp.read().decode("utf-8"))
            for f in f_data.get("files", []):
                folder_map[f["id"]] = f["name"]

        # Lấy tất cả file MP3 trong các folder đó
        parents_query = " or ".join([f"'{fid}' in parents" for fid in folder_map.keys()])
        q_files = f"mimeType='audio/mpeg' and ({parents_query}) and trashed=false"
        url_files = f"https://www.googleapis.com/drive/v3/files?q={urllib.parse.quote(q_files)}&fields=files(id,name,parents,webViewLink,modifiedTime)&pageSize=1000"
        req_files = urllib.request.Request(url_files, headers={"Authorization": f"Bearer {token}"})

        result = []
        with urllib.request.urlopen(req_files, timeout=10) as resp:
            files_data = json.loads(resp.read().decode("utf-8"))
            for f in files_data.get("files", []):
                raw_name = f.get("name", "")
                title = raw_name[:-4] if raw_name.lower().endswith(".mp3") else raw_name
                parent_id = f.get("parents", [""])[0] if f.get("parents") else ""
                artist = folder_map.get(parent_id, "Mallios")
                file_id = f.get("id", "")
                web_link = f.get("webViewLink") or f"https://drive.google.com/file/d/{file_id}/view"
                
                result.append({
                    "drive_file_id": file_id,
                    "drive_web_link": web_link,
                    "title": title,
                    "uploader": artist,
                    "filename": raw_name,
                    "timestamp": int(time.time()),
                    "storage_type": "drive"
                })
        return result
    except Exception:
        return []

