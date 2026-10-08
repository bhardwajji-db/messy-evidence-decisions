@echo off
title Messy Evidence - Backend (Port 8000)
set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%\backend"

echo ========================================================================
echo  MESSY EVIDENCE - BACKEND SERVER (FastAPI : Port 8000)
echo ========================================================================

:: Detect python
if defined MESSY_PYTHON_EXE set "PYTHON_EXE=%MESSY_PYTHON_EXE%"
if not defined PYTHON_EXE set "PYTHON_EXE=%~1"
if not defined PYTHON_EXE if exist "%PROJECT_ROOT%\.venv\Scripts\python.exe" set "PYTHON_EXE=%PROJECT_ROOT%\.venv\Scripts\python.exe"
if not defined PYTHON_EXE if exist "%PROJECT_ROOT%\venv\Scripts\python.exe" set "PYTHON_EXE=%PROJECT_ROOT%\venv\Scripts\python.exe"
if not defined PYTHON_EXE if exist "%PROJECT_ROOT%\backend\.venv\Scripts\python.exe" set "PYTHON_EXE=%PROJECT_ROOT%\backend\.venv\Scripts\python.exe"
if not defined PYTHON_EXE if exist "%PROJECT_ROOT%\..\..\STRATEGY\.venv\Scripts\python.exe" set "PYTHON_EXE=%PROJECT_ROOT%\..\..\STRATEGY\.venv\Scripts\python.exe"
if not defined PYTHON_EXE set "PYTHON_EXE=python"

echo Running with: %PYTHON_EXE%
echo Starting Uvicorn on http://127.0.0.1:8000 ...
"%PYTHON_EXE%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
