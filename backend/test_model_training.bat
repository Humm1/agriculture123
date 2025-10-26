@echo off
REM Test Model Training System
REM This script tests all model training endpoints

echo ===============================================================
echo AgroShield Model Training System Test
echo ===============================================================

REM Check if server is running
echo.
echo 1. Checking if backend server is running...
curl -s http://localhost:8000/api/model-training/health > nul 2>&1
if %errorlevel% neq 0 (
    echo    [ERROR] Backend server is not running!
    echo    Please start the server first: python run_server.py
    pause
    exit /b 1
)
echo    [OK] Backend server is running

REM Test data stats
echo.
echo 2. Checking training data availability...
curl -s http://localhost:8000/api/model-training/data-stats
echo.

REM Test data distribution
echo.
echo 3. Checking data distribution...
curl -s http://localhost:8000/api/model-training/data-distribution
echo.

REM Test model performance
echo.
echo 4. Checking model performance metrics...
curl -s http://localhost:8000/api/model-training/model-performance
echo.

REM Ask user if they want to start training
echo.
echo ===============================================================
set /p train="Do you want to start training? (y/n): "
if /i not "%train%"=="y" (
    echo.
    echo Test completed without training.
    pause
    exit /b 0
)

REM Ask which model to train
echo.
echo Select model to train:
echo 1. Pest Detection
echo 2. Disease Detection
echo 3. Storage Assessment
echo 4. All Models
echo.
set /p model_choice="Enter your choice (1-4): "

if "%model_choice%"=="1" set model_type=pest
if "%model_choice%"=="2" set model_type=disease
if "%model_choice%"=="3" set model_type=storage
if "%model_choice%"=="4" set model_type=all

if not defined model_type (
    echo Invalid choice!
    pause
    exit /b 1
)

REM Start training
echo.
echo 5. Starting training for %model_type%...
curl -X POST "http://localhost:8000/api/model-training/train" ^
  -H "Content-Type: application/json" ^
  -d "{\"model_type\": \"%model_type%\", \"epochs\": 10, \"min_samples_per_class\": 5}"
echo.

REM Monitor training
echo.
echo 6. Training started! Monitoring progress...
echo    Press Ctrl+C to stop monitoring
echo.

:monitor_loop
timeout /t 5 /nobreak > nul
curl -s http://localhost:8000/api/model-training/training-status
echo.
echo    Checking again in 5 seconds...
echo.
goto monitor_loop

pause
