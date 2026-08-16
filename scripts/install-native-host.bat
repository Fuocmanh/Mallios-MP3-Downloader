@echo off
setlocal
cd /d "%~dp0"
echo Dang cai dat Native Host cho Chrome/Edge/Brave/CocCoc...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-native-host.ps1"
pause
