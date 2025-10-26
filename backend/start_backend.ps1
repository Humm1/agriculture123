# AgroShield Backend Startup Script for PowerShell

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "   AgroShield Backend Server Startup" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Get the script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "📍 Current Directory: $PWD" -ForegroundColor Yellow
Write-Host ""

Write-Host "🚀 Starting FastAPI Backend Server..." -ForegroundColor Green
Write-Host "🌐 Server will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Documentation at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Start the server
& "..\.venv\Scripts\python.exe" run_server.py
