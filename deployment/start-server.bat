@echo off
REM Legal Cases Management System - Windows Server Startup (Simple Batch)
REM This is a simple batch file for users who prefer not to use PowerShell

echo ===============================================
echo Legal Cases Management System - Server Start
echo ===============================================

REM Change to the backend directory
cd /d "%~dp0\..\backend"

if not exist "venv" (
    echo ERROR: Virtual environment not found!
    echo Please run the setup first using PowerShell:
    echo    start-server.ps1 -Setup
    pause
    exit /b 1
)

REM Check if .env.production.windows exists
set ENV_FILE="%~dp0\.env.production.windows"
if not exist %ENV_FILE% (
    echo WARNING: Production environment file not found
    echo Using default settings...
)

echo Starting server...
echo Press Ctrl+C to stop the server
echo.

REM Activate virtual environment and start server
call venv\Scripts\activate.bat

REM Set environment variables if file exists
if exist %ENV_FILE% (
    for /f "usebackq tokens=1,2 delims==" %%a in (%ENV_FILE%) do (
        if not "%%a"=="" if not "%%b"=="" set %%a=%%b
    )
)

REM Start the server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level info

pause
