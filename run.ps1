# Octopus Agent Launcher
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host ">>> Starting Octopus Agent..." -ForegroundColor Cyan
python cli/main.py run
