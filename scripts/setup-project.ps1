# Setup script for Mallios MP3 Downloader
param (
    [switch]$Force = $false
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path "$PSScriptRoot\.."
$ToolsDir = Join-Path $ProjectRoot "tools"
$ConfigsDir = Join-Path $ProjectRoot "configs"
$LogsDir = Join-Path $ProjectRoot "logs"
$RuntimeDir = Join-Path $ProjectRoot "runtime\python"
$DownloadsDir = Join-Path $ProjectRoot "downloads"
$RequirementsFile = Join-Path $ProjectRoot "requirements.txt"

# Force UTF-8 Output
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "     MALLIOS MP3 DOWNLOADER - BO CAI DAT TU DONG HOAN CHINH" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Tao cac thu muc can thiet
if (-not (Test-Path $ToolsDir)) {
    New-Item -ItemType Directory -Path $ToolsDir -Force | Out-Null
}
if (-not (Test-Path $ConfigsDir)) {
    New-Item -ItemType Directory -Path $ConfigsDir -Force | Out-Null
}
if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null
}
if (-not (Test-Path $DownloadsDir)) {
    New-Item -ItemType Directory -Path $DownloadsDir -Force | Out-Null
}

# 2. Tu dong copy cac file mau neu chua co
$driveExample = Join-Path $ConfigsDir "drive_config.example.json"
$driveTarget = Join-Path $ConfigsDir "drive_config.json"
if ((-not (Test-Path $driveTarget)) -and (Test-Path $driveExample)) {
    Copy-Item $driveExample $driveTarget
    Write-Host "[OK] Da tao configs/drive_config.json tu ban mau." -ForegroundColor Green
}

$historyExample = Join-Path $ConfigsDir "history.example.json"
$historyTarget = Join-Path $ConfigsDir "history.json"
if ((-not (Test-Path $historyTarget)) -and (Test-Path $historyExample)) {
    Copy-Item $historyExample $historyTarget
    Write-Host "[OK] Da tao configs/history.json tu ban mau." -ForegroundColor Green
}

# 3. Kiem tra & Tai yt-dlp.exe
$ytdlpPath = Join-Path $ToolsDir "yt-dlp.exe"
if ((-not (Test-Path $ytdlpPath)) -or $Force) {
    Write-Host "[1/3] Dang tai yt-dlp.exe ban moi nhat..." -ForegroundColor Yellow
    $ytdlpUrl = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls13
        Invoke-WebRequest -Uri $ytdlpUrl -OutFile $ytdlpPath -UseBasicParsing
        Write-Host "      -> Tai yt-dlp.exe thanh cong!" -ForegroundColor Green
    } catch {
        Write-Host "      -> Loi tai yt-dlp.exe: $_" -ForegroundColor Red
    }
} else {
    Write-Host "[OK] yt-dlp.exe da co san." -ForegroundColor Green
}

# 4. Kiem tra & Tai FFmpeg (ffmpeg.exe, ffprobe.exe)
$ffmpegPath = Join-Path $ToolsDir "ffmpeg.exe"
$ffprobePath = Join-Path $ToolsDir "ffprobe.exe"
if ((-not (Test-Path $ffmpegPath)) -or (-not (Test-Path $ffprobePath)) -or $Force) {
    Write-Host "[2/3] Dang tai FFmpeg (audio converter)..." -ForegroundColor Yellow
    $ffmpegZipUrl = "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    $tempZip = Join-Path $ToolsDir "ffmpeg_temp.zip"
    $tempExtract = Join-Path $ToolsDir "ffmpeg_temp_extract"
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls13
        Write-Host "      -> Dang tai file zip FFmpeg tu GitHub..." -ForegroundColor Cyan
        Invoke-WebRequest -Uri $ffmpegZipUrl -OutFile $tempZip -UseBasicParsing
        
        Write-Host "      -> Dang giai nen FFmpeg..." -ForegroundColor Cyan
        if (Test-Path $tempExtract) { Remove-Item $tempExtract -Recurse -Force }
        Expand-Archive -Path $tempZip -DestinationPath $tempExtract -Force
        
        $extractedFfmpeg = Get-ChildItem -Path $tempExtract -Filter "ffmpeg.exe" -Recurse | Select-Object -First 1
        $extractedFfprobe = Get-ChildItem -Path $tempExtract -Filter "ffprobe.exe" -Recurse | Select-Object -First 1
        
        if ($extractedFfmpeg) {
            Copy-Item $extractedFfmpeg.FullName $ffmpegPath -Force
        }
        if ($extractedFfprobe) {
            Copy-Item $extractedFfprobe.FullName $ffprobePath -Force
        }
        
        # Don dep file tam
        if (Test-Path $tempZip) { Remove-Item $tempZip -Force }
        if (Test-Path $tempExtract) { Remove-Item $tempExtract -Recurse -Force }
        
        Write-Host "      -> Cai dat FFmpeg & FFprobe thanh cong!" -ForegroundColor Green
    } catch {
        Write-Host "      -> Khong the tai tu dong FFmpeg: $_" -ForegroundColor Red
        Write-Host "      -> Ban co the copy ffmpeg.exe vao thu muc tools/ thu cong." -ForegroundColor Yellow
    }
} else {
    Write-Host "[OK] FFmpeg & FFprobe da co san." -ForegroundColor Green
}

# 5. Kiem tra & Cai dat Python Runtime & Thu vien
Write-Host "[3/3] Kiem tra moi truong Python & thu vien..." -ForegroundColor Yellow
$pythonExe = $null

# Kiem tra runtime nhung co san
$embeddedPython = Join-Path $RuntimeDir "python.exe"
$venvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (Test-Path $embeddedPython) {
    $pythonExe = $embeddedPython
    Write-Host "      -> Su dung Python Runtime nhung co san." -ForegroundColor Green
} elseif (Test-Path $venvPython) {
    $pythonExe = $venvPython
    Write-Host "      -> Su dung Python Virtual Environment (.venv)." -ForegroundColor Green
} else {
    # Tim Python tren he thong
    $sysPython = Get-Command "python" -ErrorAction SilentlyContinue
    if ($sysPython) {
        Write-Host "      -> Tim thay Python he thong: $($sysPython.Source)" -ForegroundColor Cyan
        Write-Host "      -> Dang khoi tao moi truong ao (.venv)..." -ForegroundColor Cyan
        try {
            & python -m venv "$ProjectRoot\.venv"
            if (Test-Path $venvPython) {
                $pythonExe = $venvPython
                Write-Host "      -> Tao .venv thanh cong!" -ForegroundColor Green
            }
        } catch {
            $pythonExe = $sysPython.Source
        }
    } else {
        Write-Host "      [!] Khong tim thay Python tren may. Vui long cai dat Python 3.10+ hoac tai ban portable." -ForegroundColor Red
    }
}

if ($pythonExe -and (Test-Path $RequirementsFile)) {
    Write-Host "      -> Dang kiem tra va cai dat cac thu vien can thiet tu requirements.txt..." -ForegroundColor Cyan
    try {
        & $pythonExe -m pip install --upgrade pip --quiet
        & $pythonExe -m pip install -r $RequirementsFile --quiet
        Write-Host "      -> Cai dat cac thu vien Python thanh cong!" -ForegroundColor Green
    } catch {
        Write-Host "      -> Loi cai dat pip requirements: $_" -ForegroundColor Red
    }
}

# 6. Cai dat Native Host cho trinh duyet
Write-Host ""
Write-Host "Dang thiet lap Native Host de Extension tu dong khoi dong Server..." -ForegroundColor Yellow
$nativeHostScript = Join-Path $ProjectRoot "scripts\install-native-host.ps1"
if (Test-Path $nativeHostScript) {
    try {
        & powershell -NoProfile -ExecutionPolicy Bypass -File $nativeHostScript
    } catch {
        Write-Host "Loi cai Native Host: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "        CAI DAT HOAN TAT! DU AN DA SAN SANG HOAT DONG" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "1. Vao chrome://extensions -> Bat 'Developer mode' -> Chon 'Load unpacked' -> Chon thu muc 'extension/'."
Write-Host "2. Chay file 'run.bat' de khoi dong may chu (hoac de extension tu khoi dong qua Native Host)."
Write-Host "============================================================" -ForegroundColor Green
