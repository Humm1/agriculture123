# Start AgroShield Frontend with Web Support
# This script ensures correct directory and starts with cleared cache

Write-Host "========================================" -ForegroundColor Green
Write-Host "  Starting AgroShield Frontend (Web)" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

$appDir = "C:\Users\Codeternal\Desktop\agroshield\frontend\agroshield-app"

Write-Host "Navigating to: $appDir" -ForegroundColor Cyan
Set-Location $appDir

Write-Host "Current Directory: $(Get-Location)" -ForegroundColor Cyan
Write-Host ""

Write-Host "Starting Expo with cleared cache..." -ForegroundColor Yellow
Write-Host ""

npx expo start -c --web

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Server stopped" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
