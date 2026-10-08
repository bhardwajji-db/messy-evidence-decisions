@echo off
setlocal EnableDelayedExpansion

:: Determine project root directory
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

title Messy Evidence - Environment Check

echo ========================================================================
echo   MESSY EVIDENCE - DECISIONS : SYSTEM ENVIRONMENT AUDIT
echo ========================================================================
echo Running full diagnostic check...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%PROJECT_ROOT%scripts\check_env.ps1"

echo.
pause
