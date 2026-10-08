@echo off
setlocal EnableDelayedExpansion

:: ========================================================================
::  MESSY EVIDENCE -> DECISIONS
::  ONE-CLICK HACKATHON LAUNCHER
:: ========================================================================

:: Determine project root directory regardless of current working directory
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

title Messy Evidence - Hackathon Launcher

echo ========================================================================
echo   MESSY EVIDENCE - DECISIONS : ONE-CLICK SYSTEM LAUNCHER
echo ========================================================================
echo Starting system components in sequence...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%PROJECT_ROOT%scripts\start_services.ps1"

echo.
pause
