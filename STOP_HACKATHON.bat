@echo off
setlocal EnableDelayedExpansion

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

title Messy Evidence - Stop Services

powershell -NoProfile -ExecutionPolicy Bypass -File "%PROJECT_ROOT%scripts\stop_services.ps1"

echo.
pause
