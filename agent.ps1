# Octopus CLI Wrapper
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

python cli/main.py $args
