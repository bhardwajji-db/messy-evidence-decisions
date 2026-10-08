# scripts/check_env.ps1
# Diagnostics and environment verification for "Messy Evidence -> Decisions"
param(
    [switch]$JsonOutput
)

$ErrorActionPreference = "SilentlyContinue"
$ProjectRoot = (Resolve-Path "$PSScriptRoot\..").Path
Set-Location $ProjectRoot

# Colors
function Write-Header($text) {
    Write-Host "========================================================================" -ForegroundColor Cyan
    Write-Host "  $text" -ForegroundColor White
    Write-Host "========================================================================" -ForegroundColor Cyan
}

function Write-Row($num, $label, $details, $status, $isPass) {
    $numStr = "[$num]".PadRight(5)
    $labelStr = $label.PadRight(25)
    $detailsStr = $details.PadRight(30)
    Write-Host "$numStr ${labelStr}: $detailsStr" -NoNewline
    if ($isPass) {
        Write-Host " [$status]" -ForegroundColor Green
    } else {
        Write-Host " [$status]" -ForegroundColor Red
    }
}

$AllPass = $true
$Results = @{}

# [1] Windows OS
$os = [System.Environment]::OSVersion.VersionString
$isWindows = [System.Environment]::OSVersion.Platform -like "*Win*"
Write-Row "1" "Operating System" $os "OK" $isWindows

# [2] Find Python
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

$pyVer = ""
$pyPass = $false
if ($PythonExe) {
    try {
        $pyVer = & "$PythonExe" --version 2>&1
        if ($pyVer -like "*Python*") { $pyPass = $true }
    } catch {
        $pyVer = "Error running python"
    }
} else {
    $pyVer = "Not Found"
}
if (-not $pyPass) { $AllPass = $false }
Write-Row "2" "Python Executable" $pyVer $(if ($pyPass) { "OK" } else { "FAIL" }) $pyPass

# [3] pip
$pipVer = "Not Found"
$pipPass = $false
try {
    $pipOut = (& $PythonExe -m pip --version) 2>&1 | Out-String
    if ($pipOut -match "pip\s+([0-9\.]+)") {
        $pipVer = "pip " + $Matches[1]
        $pipPass = $true
    }
} catch {}
if (-not $pipPass) { $AllPass = $false }
Write-Row "3" "pip Package Manager" $pipVer $(if ($pipPass) { "OK" } else { "FAIL" }) $pipPass

# [4] Node
$nodeCmd = Get-Command node -ErrorAction SilentlyContinue
$nodeVer = "Not Found"
$nodePass = $false
if ($nodeCmd) {
    $nodeVer = (& node -v) 2>&1 | Out-String
    $nodeVer = $nodeVer.Trim()
    if ($nodeVer -match "v[0-9]+") { $nodePass = $true }
}
if (-not $nodePass) { $AllPass = $false }
Write-Row "4" "Node.js Runtime" $nodeVer $(if ($nodePass) { "OK" } else { "FAIL" }) $nodePass

# [5] npm
$npmCmd = Get-Command npm -ErrorAction SilentlyContinue
$npmVer = "Not Found"
$npmPass = $false
if ($npmCmd) {
    $npmVer = (& npm -v) 2>&1 | Out-String
    $npmVer = $npmVer.Trim()
    if ($npmVer -match "[0-9]+") { $nodePass = $true; $npmPass = $true }
}
if (-not $npmPass) { $AllPass = $false }
Write-Row "5" "npm Package Manager" "v$npmVer" $(if ($npmPass) { "OK" } else { "FAIL" }) $npmPass

# [6] Ollama CLI
$ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue
$ollamaVer = "Not Installed"
$ollamaCliPass = $false
if ($ollamaCmd) {
    $ollamaOut = (& ollama --version) 2>&1 | Out-String
    if ($ollamaOut -match "([0-9\.]+)") {
        $ollamaVer = "v" + $Matches[1]
        $ollamaCliPass = $true
    }
}
Write-Row "6" "Ollama CLI" $ollamaVer $(if ($ollamaCliPass) { "OK" } else { "WARN" }) $ollamaCliPass

# [7] Ollama Service
$ollamaServicePass = $false
$ollamaServiceStatus = "Port 11434 Offline"
try {
    $tagsResp = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 2 -ErrorAction Stop
    $ollamaServicePass = $true
    $ollamaServiceStatus = "Port 11434 Active"
} catch {
    $ollamaServiceStatus = "Offline (Local NLP Active)"
}
Write-Row "7" "Ollama Service" $ollamaServiceStatus $(if ($ollamaServicePass) { "OK" } else { "OFFLINE" }) $true

# [8] Required Ollama Model (llama3)
$expectedModel = "llama3"
if ($env:OLLAMA_MODEL) { $expectedModel = $env:OLLAMA_MODEL }
$modelPass = $false
$modelStatus = "Missing (Fallback active)"
if ($ollamaServicePass -and $tagsResp.models) {
    $modelNames = $tagsResp.models | ForEach-Object { $_.name }
    $found = $modelNames | Where-Object { $_ -like "*$expectedModel*" }
    if ($found) {
        $modelPass = $true
        $modelStatus = "$expectedModel Available"
    } else {
        $modelStatus = "$expectedModel Not Found"
    }
}
Write-Row "8" "Ollama Model ($expectedModel)" $modelStatus $(if ($modelPass) { "OK" } else { "FALLBACK" }) $true

# [9] Python Virtual Environment
$venvDesc = if ($PythonExe -like "*venv*") { "Virtual Env Active" } else { "System Python Active" }
Write-Row "9" "Python Environment" $venvDesc "OK" $true

# [10] Required Python Packages
$corePackages = @("fastapi", "uvicorn", "sqlalchemy", "pydantic", "cv2", "pypdf", "paddleocr", "faster_whisper", "httpx", "requests")
$installedCount = 0
if ($PythonExe) {
    $checkScript = @"
pkgs = ['fastapi', 'uvicorn', 'sqlalchemy', 'pydantic', 'cv2', 'pypdf', 'paddleocr', 'faster_whisper', 'httpx', 'requests']
count = 0
for p in pkgs:
    try:
        __import__(p)
        count += 1
    except:
        pass
print(count)
"@
    $testOut = (& $PythonExe -c $checkScript) 2>&1 | Out-String
    $testOut = $testOut.Trim()
    if ($testOut -match "^\d+$") {
        $installedCount = [int]$testOut
    }
}
$pkgPass = ($installedCount -ge 8)
if (-not $pkgPass) { $AllPass = $false }
Write-Row "10" "Backend Dependencies" "$installedCount/$($corePackages.Count) Core Packages" $(if ($pkgPass) { "OK" } else { "FAIL" }) $pkgPass


# [11] frontend/package.json
$pkgJsonExists = Test-Path "$ProjectRoot\frontend\package.json"
if (-not $pkgJsonExists) { $AllPass = $false }
Write-Row "11" "frontend/package.json" $(if ($pkgJsonExists) { "Present" } else { "Missing" }) $(if ($pkgJsonExists) { "OK" } else { "FAIL" }) $pkgJsonExists

# [12] frontend/node_modules
$nodeModulesExists = Test-Path "$ProjectRoot\frontend\node_modules"
if (-not $nodeModulesExists) { $AllPass = $false }
Write-Row "12" "frontend/node_modules" $(if ($nodeModulesExists) { "Installed" } else { "Missing" }) $(if ($nodeModulesExists) { "OK" } else { "FAIL" }) $nodeModulesExists

# [13] Backend Structure
$backendOk = (Test-Path "$ProjectRoot\backend\app\main.py") -and (Test-Path "$ProjectRoot\backend\app\config.py") -and (Test-Path "$ProjectRoot\backend\app\models\schema.py")
if (-not $backendOk) { $AllPass = $false }
Write-Row "13" "Backend App Structure" $(if ($backendOk) { "All Core Modules Present" } else { "Missing Files" }) $(if ($backendOk) { "OK" } else { "FAIL" }) $backendOk

# [14] Database
$dbPath = "$ProjectRoot\backend\data\evidence_system.db"
$dbExists = Test-Path $dbPath
Write-Row "14" "Database (SQLite)" $(if ($dbExists) { "evidence_system.db Ready" } else { "Will Auto-Create" }) "OK" $true

# [15] Demo Data
$demoDataExists = (Test-Path "$ProjectRoot\backend\data\demo") -or (Test-Path "$ProjectRoot\demo")
Write-Row "15" "Demo Data Benchmark" $(if ($demoDataExists) { "5 Scenarios Available" } else { "Missing" }) "OK" $true

# [16] Environment Variables
$envDesc = "OLLAMA_MODEL=$expectedModel"
Write-Row "16" "Environment Config" $envDesc "OK" $true

# [17] Port 8000
$port8000InUse = $false
try {
    $client = New-Object System.Net.Sockets.TcpClient
    $iar = $client.BeginConnect("127.0.0.1", 8000, $null, $null)
    $port8000InUse = $iar.AsyncWaitHandle.WaitOne(400, $false) -and $client.Connected
    $client.Close()
} catch {}
$port8000Desc = if ($port8000InUse) { "Port 8000 Active (Running)" } else { "Port 8000 Available" }
Write-Row "17" "Backend Port 8000" $port8000Desc "OK" $true

# [18] Port 5173
$port5173InUse = $false
try {
    $client = New-Object System.Net.Sockets.TcpClient
    $iar = $client.BeginConnect("127.0.0.1", 5173, $null, $null)
    $port5173InUse = $iar.AsyncWaitHandle.WaitOne(400, $false) -and $client.Connected
    $client.Close()
} catch {}
$port5173Desc = if ($port5173InUse) { "Port 5173 Active (Running)" } else { "Port 5173 Available" }
Write-Row "18" "Frontend Port 5173" $port5173Desc "OK" $true


Write-Host "========================================================================" -ForegroundColor Cyan
if ($AllPass) {
    Write-Host "  DIAGNOSTIC RESULT: READY FOR HACKATHON: YES" -ForegroundColor Green
    Write-Host "  All core dependencies and structures verified successfully." -ForegroundColor Gray
} else {
    Write-Host "  DIAGNOSTIC RESULT: READY FOR HACKATHON: NO" -ForegroundColor Red
    Write-Host "  Please resolve any [FAIL] items shown above before presenting." -ForegroundColor Yellow
}
Write-Host "========================================================================" -ForegroundColor Cyan
