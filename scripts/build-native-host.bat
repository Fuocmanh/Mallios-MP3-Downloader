@echo off
setlocal
cd /d "%~dp0"
echo Dang bien dich MalliosNativeHost.exe...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0build-native-host.ps1"
pause
