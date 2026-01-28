# Octopus Installer
# =================
# Installs Octopus v0.1 environment

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Octopus v0.1 Installer               " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Python
Write-Host "[1/5] Checking Python..." -ForegroundColor Yellow
try {
    $pyVer = python --version 2>&1
    if ($pyVer -match "3\.1[0-9]") {
        Write-Host "[OK] Found $pyVer" -ForegroundColor Green
    }
    else {
        Write-Host "[ERROR] Python 3.10+ required. Found: $pyVer" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "[ERROR] Python not found in PATH" -ForegroundColor Red
    exit 1
}

# 2. Clone/Pull Repository
Write-Host "[2/5] Setting up Octopus..." -ForegroundColor Yellow
if (Test-Path "Octopus") {
    Write-Host "[INFO] Updating existing repository..." -ForegroundColor Blue
    Set-Location Octopus
    git pull
}
else {
    git clone https://github.com/abwoo/Octopus.git
    Set-Location Octopus
}

# 3. Install Dependencies
Write-Host "[3/5] Installing dependencies..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    python -m pip install -r requirements.txt -q
    Write-Host "[OK] Dependencies installed" -ForegroundColor Green
}
else {
    python -m pip install pyautogui pynput pyyaml click -q
    Write-Host "[OK] Default dependencies installed" -ForegroundColor Green
}

# 4. Initialize Directories
Write-Host "[4/5] Initializing workspace..." -ForegroundColor Yellow
$dirs = @("workspace", "logs", "config")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# 5. Create Config
if (-not (Test-Path "config/config.yaml")) {
    @"
adapter: mock
workspace: workspace
log_file: logs/actions.log
action_interval_ms: 300
"@ | Out-File -FilePath "config/config.yaml" -Encoding utf8
}
Write-Host "[OK] Workspace initialized" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Installation Complete!               " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Usage:" -ForegroundColor White
Write-Host "  .\run.ps1                 # Start Agent" -ForegroundColor Gray
Write-Host "  .\agent.ps1 version       # Check version" -ForegroundColor Gray
Write-Host "  .\agent.ps1 status        # Check status" -ForegroundColor Gray
Write-Host ""
