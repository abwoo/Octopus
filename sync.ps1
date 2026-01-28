param (
    [string]$Message = "style: auto-sync from Antigravity"
)

Write-Host ">>> Synchronizing changes to GitHub..." -ForegroundColor Cyan

# Check for changes
$status = git status --porcelain
if (-not $status) {
    Write-Host ">>> No changes to sync." -ForegroundColor Yellow
    exit 0
}

# Add, Commit, Push
git add .
git commit -m $Message
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ">>> Synchronization successful!" -ForegroundColor Green
}
else {
    Write-Host ">>> Synchronization failed. Please check your Git configuration and connection." -ForegroundColor Red
    exit 1
}
