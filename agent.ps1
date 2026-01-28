# Octopus CLI Wrapper
# ====================
# Wraps python cli/main.py for easy access

$ErrorActionPreference = "Stop"
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptPath

python cli/main.py $args
