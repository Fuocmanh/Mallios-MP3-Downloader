$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$nativeHostDir = Join-Path $projectRoot 'native-host'
$hostExePath = Join-Path $nativeHostDir 'MalliosNativeHost.exe'
$installedManifest = Join-Path $nativeHostDir 'com.mallios.mp3.installed.json'
$sourceCs = Join-Path $nativeHostDir 'MalliosNativeHost.cs'

# 1. Build host if missing
if (-not (Test-Path $hostExePath)) {
    Write-Host "Dang bien dich MalliosNativeHost.exe..."
    Add-Type -TypeDefinition (Get-Content -Raw $sourceCs -Encoding UTF8) -OutputAssembly $hostExePath -OutputType ConsoleApplication
}

# 2. Tao file manifest JSON chuan UTF-8 khong BOM
$manifestObject = @{
    name = "com.mallios.mp3"
    description = "Starts the Mallios local server when Chrome requests it."
    path = $hostExePath
    type = "stdio"
    allowed_origins = @(
        "chrome-extension://ejbmglcdgkjndmficeeejojlejaignmm/"
    )
}

$jsonText = $manifestObject | ConvertTo-Json -Depth 4
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($installedManifest, $jsonText, $utf8NoBom)

# 3. Dang ky Registry cho cac trinh duyet Chromium pho bien tren Windows
$registryKeys = @(
    'HKCU:\Software\Google\Chrome\NativeMessagingHosts\com.mallios.mp3',
    'HKCU:\Software\Microsoft\Edge\NativeMessagingHosts\com.mallios.mp3',
    'HKCU:\Software\BraveSoftware\Brave-Browser\NativeMessagingHosts\com.mallios.mp3',
    'HKCU:\Software\CocCoc\Browser\NativeMessagingHosts\com.mallios.mp3',
    'HKCU:\Software\Chromium\NativeMessagingHosts\com.mallios.mp3'
)

foreach ($key in $registryKeys) {
    try {
        if (-not (Test-Path $key)) {
            New-Item -Path $key -Force | Out-Null
        }
        Set-ItemProperty -Path $key -Name '(Default)' -Value $installedManifest
    } catch {
        # Bo qua neu trinh duyet khong cai dat hoac khong co quyen tao nhánh
    }
}

Write-Host "=========================================================="
Write-Host "[OK] Da cai dat Native Host thanh cong cho Chrome/Edge/Brave/CocCoc!"
Write-Host "Host executable : $hostExePath"
Write-Host "Manifest file   : $installedManifest"
Write-Host "Vui long vao chrome://extensions va bam nut Reload (tai lai) extension."
Write-Host "=========================================================="
