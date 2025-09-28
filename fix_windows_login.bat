@echo off
title Legal Cases - Emergency Fix for Windows
color 0A

echo.
echo ========================================
echo   LEGAL CASES - EMERGENCY WINDOWS FIX
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo.
    pause
    exit /b 1
)

echo ✅ Python found
echo.

echo Navigating to backend directory...
if not exist "backend" (
    echo ❌ ERROR: backend directory not found!
    echo Please run this from the project root directory
    echo.
    pause
    exit /b 1
)

cd backend

echo.
echo Setting up virtual environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing/Upgrading dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo   RUNNING EMERGENCY PASSWORD RESET
echo ========================================
echo.

python emergency_reset.py

echo.
echo ========================================
echo   STARTING THE SERVER
echo ========================================
echo.

echo Starting backend server...
echo ✅ Server will start at http://localhost:8000
echo ✅ Use credentials: admin / admin123
echo.

python main.py

pause
