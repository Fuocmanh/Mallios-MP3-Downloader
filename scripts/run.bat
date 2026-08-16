@echo off
setlocal
cd /d "%~dp0.."
echo Starting Mallios local server...
"runtime\python\python.exe" "backend\app.py"
