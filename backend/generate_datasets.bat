@echo off
REM AgroShield Training Dataset Generator
REM Generates all pretrained datasets for AI models

echo ========================================
echo AgroShield Dataset Generation
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/3] Checking dependencies...
pip show Pillow >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements-datasets.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
) else (
    echo Dependencies OK
)

echo.
echo [2/3] Generating training datasets...
echo This will create ~120MB of synthetic training data
echo.

python generate_training_datasets.py

if errorlevel 1 (
    echo.
    echo ERROR: Dataset generation failed
    pause
    exit /b 1
)

echo.
echo [3/3] Generation complete!
echo.
echo Datasets saved to: training_data/
echo Summary: training_data/dataset_summary.json
echo.
echo ========================================
echo Next Steps:
echo 1. Review TRAINING_DATASETS_README.md
echo 2. Train models using the generated data
echo 3. Replace synthetic data with real images (optional)
echo ========================================
echo.

pause
