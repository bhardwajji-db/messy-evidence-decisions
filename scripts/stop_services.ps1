# scripts/stop_services.ps1
# Targeted shutdown for "Messy Evidence -> Decisions"
param()

$ErrorActionPreference = "SilentlyContinue"

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "         MESSY EVIDENCE -> DECISIONS : STOPPING SYSTEM" -ForegroundColor White
Write-Host "========================================================================" -ForegroundColor Cyan

# 1. Stop Backend on port 8000
$stoppedBackend = $false
try {
    $conns8000 = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
    if ($conns8000) {
        foreach ($c in $conns8000) {
            $pidToKill = $c.OwningProcess
            if ($pidToKill -and $pidToKill -gt 0) {
                # Stop process tree
                Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
                # Kill any child processes
                cmd /c "taskkill /PID $pidToKill /T /F" 2>$null
                $stoppedBackend = $true
            }
        }
    }
} catch {}

if ($stoppedBackend) {
    Write-Host "  Backend Server (Port 8000)     : [STOPPED]" -ForegroundColor Green
} else {
    Write-Host "  Backend Server (Port 8000)     : [NOT RUNNING]" -ForegroundColor Gray
}

# 2. Stop Frontend on port 5173
$stoppedFrontend = $false
try {
    $conns5173 = Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue
    if ($conns5173) {
        foreach ($c in $conns5173) {
            $pidToKill = $c.OwningProcess
            if ($pidToKill -and $pidToKill -gt 0) {
                Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
                cmd /c "taskkill /PID $pidToKill /T /F" 2>$null
                $stoppedFrontend = $true
            }
        }
    }
} catch {}

if ($stoppedFrontend) {
    Write-Host "  Frontend Server (Port 5173)    : [STOPPED]" -ForegroundColor Green
} else {
    Write-Host "  Frontend Server (Port 5173)    : [NOT RUNNING]" -ForegroundColor Gray
}

# 3. Clean up any lingering terminal windows started by the launcher
try {
    Get-Process cmd -ErrorAction SilentlyContinue | Where-Object {
        $_.MainWindowTitle -like "*Messy Evidence*"
    } | Stop-Process -Force -ErrorAction SilentlyContinue
} catch {}

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  SYSTEM STOPPED: All application services terminated safely." -ForegroundColor Yellow
Write-Host "  Unrelated Python, Node, and Ollama services were left untouched." -ForegroundColor Gray
Write-Host "========================================================================" -ForegroundColor Cyan
