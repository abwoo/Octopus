# Octopus Dashboard Launcher
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host ">>> Starting Octopus Dashboard..." -ForegroundColor Cyan

# 1. Start Backend API
Write-Host ">>> launching Backend API on http://localhost:8000..." -ForegroundColor Gray
Start-Process python -ArgumentList "api/main.py" -WindowStyle Hidden

# 2. Start Frontend Dev Server
Write-Host ">>> launching Frontend on http://localhost:3000..." -ForegroundColor Gray
Set-Location web
Start-Process npm -ArgumentList "run dev" -WindowStyle Hidden

# 3. Open Browser
Start-Sleep -Seconds 3
Start-Process "http://localhost:3000"

Write-Host ">>> Dashboard launched!" -ForegroundColor Green
Write-Host ">>> Close the terminal windows to stop the services (or kill python/node processes)." -ForegroundColor Yellow

