# Octopus Dashboard Launcher
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host ">>> Cleaning up existing Octopus processes..." -ForegroundColor Gray
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*api/main.py*" } | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process node -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*vite*" } | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host ">>> Starting Octopus Dashboard..." -ForegroundColor Cyan

# 1. Start Backend API
Write-Host ">>> launching Backend API on http://localhost:8000..." -ForegroundColor Gray
Start-Process python -ArgumentList "api/main.py" -WindowStyle Hidden

# 2. Wait for API to start
Write-Host ">>> Waiting for API to be ready..." -ForegroundColor Gray
$maxRetries = 10
while ($maxRetries -gt 0) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/status" -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) { break }
    }
    catch { }
    Start-Sleep -Seconds 1
    $maxRetries--
}

# 3. Start Frontend Dev Server
Write-Host ">>> launching Frontend on http://localhost:3000..." -ForegroundColor Gray
Set-Location web
Start-Process npm.cmd -ArgumentList "run dev" -NoNewWindow -WindowStyle Hidden

# 4. Wait for Frontend
Start-Sleep -Seconds 3

# 5. Open Browser
Write-Host ">>> Dashboard ready! Opening browser..." -ForegroundColor Green
Start-Process "http://localhost:3000"

Write-Host ">>> Dashboard launched!" -ForegroundColor Green
Write-Host ">>> Close this terminal window to stop (or kill processes manually)." -ForegroundColor Yellow

