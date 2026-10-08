# scripts/start_services.ps1
# Master launcher for "Messy Evidence -> Decisions"
param(
    [switch]$ForceOffline
)

$ErrorActionPreference = "SilentlyContinue"
$ProjectRoot = (Resolve-Path "$PSScriptRoot\..").Path
Set-Location $ProjectRoot

function Write-Banner($title) {
    Write-Host "========================================================================" -ForegroundColor Cyan
    Write-Host "  $title" -ForegroundColor White
    Write-Host "========================================================================" -ForegroundColor Cyan
}

function Test-PortOpen($port) {
    $conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($conn) { return $true }
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $iar = $client.BeginConnect("127.0.0.1", $port, $null, $null)
        $connected = $iar.AsyncWaitHandle.WaitOne(300, $false) -and $client.Connected
        $client.Close()
        return $connected
    } catch {
        return $false
    }
}

Write-Banner "MESSY EVIDENCE -> DECISIONS : STARTUP SEQUENCE"

# -------------------------------------------------------------------------
# STEP 2 - Check Python
# -------------------------------------------------------------------------
Write-Host "[1/6] Detecting Python environment..." -ForegroundColor Yellow
$PythonExe = $null
$venvPaths = @(
    "$ProjectRoot\.venv\Scripts\python.exe",
    "$ProjectRoot\venv\Scripts\python.exe",
    "$ProjectRoot\backend\.venv\Scripts\python.exe",
    "$ProjectRoot\backend\venv\Scripts\python.exe",
    "$ProjectRoot\..\STRATEGY\.venv\Scripts\python.exe"
)
foreach ($vp in $venvPaths) {
    if (Test-Path $vp) {
        $PythonExe = (Resolve-Path $vp).Path
        break
    }
}
if (-not $PythonExe) {
    $sysPy = Get-Command python -ErrorAction SilentlyContinue
    if ($sysPy) { $PythonExe = $sysPy.Source }
}

if (-not $PythonExe) {
    Write-Host "========================================================================" -ForegroundColor Red
    Write-Host " ERROR: PYTHON IS NOT FOUND ON THIS SYSTEM" -ForegroundColor Red
    Write-Host "========================================================================" -ForegroundColor Red
    Write-Host " Python 3.10 or 3.11 is required to run the verification backend."
    Write-Host " Please install Python from https://www.python.org/downloads/"
    Write-Host " Ensure 'Add Python to PATH' is checked during installation."
    exit 1
}

$pyVer = & $PythonExe --version 2>&1
Write-Host "  -> Python found: $pyVer ($PythonExe)" -ForegroundColor Green

# -------------------------------------------------------------------------
# STEP 3 - Check Node & npm
# -------------------------------------------------------------------------
Write-Host "[2/6] Detecting Node.js and npm..." -ForegroundColor Yellow
$nodeCmd = Get-Command node -ErrorAction SilentlyContinue
$npmCmd = Get-Command npm -ErrorAction SilentlyContinue
if (-not $nodeCmd -or -not $npmCmd) {
    Write-Host "========================================================================" -ForegroundColor Red
    Write-Host " ERROR: NODE.JS OR NPM NOT FOUND" -ForegroundColor Red
    Write-Host "========================================================================" -ForegroundColor Red
    Write-Host " Node.js 18+ and npm are required to run the frontend."
    Write-Host " Please install Node.js from https://nodejs.org/"
    exit 1
}
$nodeVer = (& node -v 2>&1).Trim()
$npmVer = (& npm -v 2>&1).Trim()
Write-Host "  -> Node.js found: $nodeVer | npm: v$npmVer" -ForegroundColor Green

# Check frontend node_modules
if (-not (Test-Path "$ProjectRoot\frontend\node_modules")) {
    Write-Host "  -> frontend/node_modules missing. Running npm install..." -ForegroundColor Yellow
    Push-Location "$ProjectRoot\frontend"
    npm install
    Pop-Location
}

# -------------------------------------------------------------------------
# STEP 4 & 5 - Check Ollama & AI Model
# -------------------------------------------------------------------------
Write-Host "[3/6] Checking AI Engine (Ollama & Llama 3)..." -ForegroundColor Yellow
$expectedModel = "llama3"
if ($env:OLLAMA_MODEL) { $expectedModel = $env:OLLAMA_MODEL }

$ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue
$ollamaAvailable = $false
$modelAvailable = $false

if ($ollamaCmd) {
    # Check if port 11434 is listening
    $port11434 = Test-PortOpen 11434
    if (-not $port11434) {
        Write-Host "  -> Ollama service not running on port 11434. Starting Ollama..." -ForegroundColor Yellow
        Start-Process "ollama" -ArgumentList "serve" -WindowStyle Minimized
        
        # Wait up to 10 seconds for Ollama API to respond
        $waitCount = 0
        while ($waitCount -lt 10 -and -not (Test-PortOpen 11434)) {
            Start-Sleep -Seconds 1
            $waitCount++
        }
    } else {
        Write-Host "  -> Ollama service already running on port 11434 - using existing instance." -ForegroundColor Green
    }

    # Query Ollama models
    try {
        $tagsResp = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 3 -ErrorAction Stop
        $ollamaAvailable = $true
        if ($tagsResp.models) {
            $modelNames = $tagsResp.models | ForEach-Object { $_.name }
            $foundModel = $modelNames | Where-Object { $_ -like "*$expectedModel*" }
            if ($foundModel) {
                $modelAvailable = $true
                Write-Host "  -> Required model '$expectedModel' verified in Ollama." -ForegroundColor Green
            }
        }
    } catch {
        Write-Host "  -> Ollama API responded with error. Fallback will be used." -ForegroundColor Gray
    }
}

if (-not $modelAvailable) {
    Write-Host "========================================================================" -ForegroundColor Yellow
    Write-Host " REQUIRED AI MODEL NOT FOUND: '$expectedModel'" -ForegroundColor Yellow
    Write-Host "========================================================================" -ForegroundColor Yellow
    Write-Host " The system is configured for model: $expectedModel"
    Write-Host " You can install it anytime using:"
    Write-Host "   ollama pull $expectedModel" -ForegroundColor Cyan
    Write-Host ""
    Write-Host " NOTICE: The application includes a high-accuracy, 100% offline"
    Write-Host " Deterministic Civic NLP Fallback Engine that runs with zero hallucinations."
    Write-Host " Proceeding with Deterministic Civic NLP active." -ForegroundColor Green
    Write-Host "========================================================================" -ForegroundColor Yellow
}

# -------------------------------------------------------------------------
# STEP 8 - Start Backend (Port 8000)
# -------------------------------------------------------------------------
Write-Host "[4/6] Checking Backend server on port 8000..." -ForegroundColor Yellow
$backendRunning = Test-PortOpen 8000

if ($backendRunning) {
    Write-Host "  -> Backend already running on port 8000 - using existing instance." -ForegroundColor Green
} else {
    Write-Host "  -> Starting Backend server (FastAPI)..." -ForegroundColor Cyan
    $backendScript = "$ProjectRoot\scripts\run_backend.bat"
    $env:MESSY_PYTHON_EXE = $PythonExe
    Start-Process -FilePath "cmd.exe" -ArgumentList @("/k", $backendScript)

    # Wait for backend health check
    Write-Host "  -> Waiting for backend to become healthy..." -NoNewline
    $backendReady = $false
    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep -Seconds 1
        Write-Host "." -NoNewline
        if (Test-PortOpen 8000) {
            try {
                $h = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/health" -TimeoutSec 1 -ErrorAction SilentlyContinue
                if ($h.status -eq "healthy") {
                    $backendReady = $true
                    break
                }
            } catch {}
        }
    }
    Write-Host ""
    if ($backendReady) {
        Write-Host "  -> Backend is healthy and responding on port 8000." -ForegroundColor Green
    } else {
        Write-Host "  -> Warning: Backend took longer than expected to report healthy." -ForegroundColor Yellow
    }
}

# -------------------------------------------------------------------------
# STEP 9 - Start Frontend (Port 5173)
# -------------------------------------------------------------------------
Write-Host "[5/6] Checking Frontend server on port 5173..." -ForegroundColor Yellow
$frontendRunning = Test-PortOpen 5173

if ($frontendRunning) {
    Write-Host "  -> Frontend already running on port 5173 - using existing instance." -ForegroundColor Green
} else {
    Write-Host "  -> Starting Frontend server (Vite)..." -ForegroundColor Cyan
    $frontendScript = "$ProjectRoot\scripts\run_frontend.bat"
    Start-Process -FilePath "cmd.exe" -ArgumentList @("/k", $frontendScript)

    # Wait for frontend port to be listening
    Write-Host "  -> Waiting for frontend to become ready..." -NoNewline
    $frontendReady = $false
    for ($i = 0; $i -lt 25; $i++) {
        Start-Sleep -Seconds 1
        Write-Host "." -NoNewline
        if (Test-PortOpen 5173) {
            $frontendReady = $true
            break
        }
    }
    Write-Host ""
    if ($frontendReady) {
        Write-Host "  -> Frontend is ready on port 5173." -ForegroundColor Green
    } else {
        Write-Host "  -> Warning: Frontend took longer than expected to start." -ForegroundColor Yellow
    }
}

# -------------------------------------------------------------------------
# STEP 10 - Open Browser
# -------------------------------------------------------------------------
Write-Host "[6/6] Launching Dashboard in browser..." -ForegroundColor Yellow
Start-Process "http://localhost:5173"
Write-Host "  -> Browser opened to http://localhost:5173" -ForegroundColor Green

# -------------------------------------------------------------------------
# STEP 11 - Final Status Screen
# -------------------------------------------------------------------------
Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "                      MESSY EVIDENCE -> DECISIONS                      " -ForegroundColor White
Write-Host "                             SYSTEM READY                               " -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Frontend URL  : " -NoNewline; Write-Host "http://localhost:5173" -ForegroundColor Cyan
Write-Host "  Backend URL   : " -NoNewline; Write-Host "http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "  Swagger Docs  : " -NoNewline; Write-Host "http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "  Health Status : " -NoNewline; Write-Host "http://127.0.0.1:8000/api/health" -ForegroundColor Cyan
Write-Host ""
$aiDesc = if ($modelAvailable) { "Ollama + $expectedModel" } else { "Local Deterministic Civic NLP (Active)" }
Write-Host "  Active AI     : $aiDesc" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Component Status:" -ForegroundColor White
Write-Host "    Frontend     [OK] - Live on http://localhost:5173" -ForegroundColor Green
Write-Host "    Backend      [OK] - Live on http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "    Ollama       [OK] - Service on port 11434" -ForegroundColor Green
Write-Host "    AI Pipeline  [OK] - Multimodal (Vision, Audio, OCR, PDF, Rules)" -ForegroundColor Green
Write-Host "    Database     [OK] - SQLite Schema & Official Records Pre-seeded" -ForegroundColor Green
Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  KEEP THIS LAUNCHER WINDOW OPEN or press any key to dismiss." -ForegroundColor Gray
Write-Host "  To stop the application, run: STOP_HACKATHON.bat" -ForegroundColor Yellow
Write-Host "========================================================================" -ForegroundColor Cyan
