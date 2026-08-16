@echo off
setlocal
cd /d "%~dp0"
title Cai dat Mallios MP3 Downloader

echo ============================================================
echo   MALLIOS MP3 DOWNLOADER - KHOI TAO & TAI CONG CU TU DONG
echo ============================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup-project.ps1"

echo.
pause
