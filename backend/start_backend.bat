@echo off
REM AgroShield Backend Startup Script for Windows
REM Run this file to start the backend server

echo ======================================================================
echo    AgroShield Backend Server Startup
echo ======================================================================
echo.

cd /d "%~dp0"
echo Current Directory: %CD%
echo.

echo Starting FastAPI Backend Server...
echo Server will be available at: http://localhost:8000
echo API Documentation at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ======================================================================
echo.

REM Start the server using the virtual environment Python
..\..venv\Scripts\python.exe run_server.py

pause
