@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Mallios MP3 Downloader Server (127.0.0.1:37491)
set "PORT=37491"
set "HEALTH_URL=http://127.0.0.1:%PORT%/api/status"
echo ======================================================
echo   MALLIOS MP3 DOWNLOADER - KHOI DONG HE THONG
echo   Dia chi: %HEALTH_URL%
echo ======================================================
echo.
rem Reuse a healthy backend; never kill an existing instance.
curl.exe --fail --silent --show-error --max-time 2 "%HEALTH_URL%" >nul 2>&1
if not errorlevel 1 (
    echo [OK] Backend dang chay, tai su dung instance hien tai.
    goto :end
)
set "NEED_SETUP=0"
if not exist "tools\yt-dlp.exe" set "NEED_SETUP=1"
if not exist "tools\ffmpeg.exe" set "NEED_SETUP=1"
if not exist "tools\FolderPicker.exe" set "NEED_SETUP=1"
if not exist "native-host\MalliosNativeHost.exe" set "NEED_SETUP=1"
if not exist "runtime\python\python.exe" if not exist ".venv\Scripts\python.exe" set "NEED_SETUP=1"
if "%NEED_SETUP%"=="1" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup-project.ps1"
)
echo [OK] Dang khoi dong backend duy nhat...
if exist "runtime\python\python.exe" (
    "runtime\python\python.exe" "backend\app.py"
    goto :end
)
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" "backend\app.py"
    goto :end
)
python "backend\app.py"
:end
endlocal
pause
