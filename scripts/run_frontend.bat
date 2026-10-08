@echo off
title Messy Evidence - Frontend (Port 5173)
set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%\frontend"

echo ========================================================================
echo  MESSY EVIDENCE - FRONTEND DEV SERVER (Vite : Port 5173)
echo ========================================================================
echo Starting Vite dev server on http://localhost:5173 ...
npm run dev
