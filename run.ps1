# Octopus Run Script
# ==================
# Starts the Agent in execution mode

$ErrorActionPreference = "Stop"
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptPath

Write-Host "Starting Octopus Agent..." -ForegroundColor Cyan
Write-Host "Press Ctrl+Alt+Q to emergency stop" -ForegroundColor Yellow

python cli/main.py run
