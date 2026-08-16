$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$source = Join-Path $projectRoot 'native-host\MalliosNativeHost.cs'
$output = Join-Path $projectRoot 'native-host\MalliosNativeHost.exe'

# Compile C# using Add-Type
Add-Type -TypeDefinition (Get-Content -Raw $source -Encoding UTF8) -OutputAssembly $output -OutputType ConsoleApplication
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
Write-Host "Da build thanh cong: $output"
