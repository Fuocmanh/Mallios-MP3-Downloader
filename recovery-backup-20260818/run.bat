@echo off
setlocal
cd /d "%~dp0"
title Mallios MP3 Downloader Server (127.0.0.1:37491)

echo ======================================================
echo   MALLIOS MP3 DOWNLOADER - KHOI DONG HE THONG
echo   Dia chi: http://127.0.0.1:37491
echo ======================================================
echo.

rem Kiem tra xem may da co du cong cu va moi truong chua
set NEED_SETUP=0

if not exist "tools\yt-dlp.exe" set NEED_SETUP=1
if not exist "tools\ffmpeg.exe" set NEED_SETUP=1
if not exist "tools\FolderPicker.exe" set NEED_SETUP=1
if not exist "native-host\MalliosNativeHost.exe" set NEED_SETUP=1
if not exist "runtime\python\python.exe" (
    if not exist ".venv\Scripts\python.exe" set NEED_SETUP=1
)

rem Neu thieu bat ky thu gi (khi vua clone tu Git ve), tu dong chay cai dat
if "%NEED_SETUP%"=="1" (
    echo [!] Phat hien he thong chua du cong cu hoac clone lan dau tu Git.
    echo [*] Dang tu dong tai yt-dlp, ffmpeg va cai dat moi truong...
    echo.
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup-project.ps1"
    echo.
    echo [*] Cai dat hoan tat! Dang khoi dong may chu...
    echo.
)



echo ======================================================
rem Neu server da chay thi dung lai, khong kill tien trinh dang tai
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest http://127.0.0.1:37491/api/status -UseBasicParsing -TimeoutSec 2 | Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1
if not errorlevel 1 (
    echo Server Mallios da dang chay. Khong khoi dong lai de tranh mat phien tai.
    goto end
)

echo   MAY CHU DANG CHAY TAI: http://127.0.0.1:37491
echo   (Vui long de cua so nay mo khi su dung Extension)
echo ======================================================
echo.

if exist "runtime\python\python.exe" (
    "runtime\python\python.exe" "backend\app.py"
    goto end
)

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" "backend\app.py"
    goto end
)

python "backend\app.py"

:end
pause
