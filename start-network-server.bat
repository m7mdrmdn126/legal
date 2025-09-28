@echo off
title Legal Cases Management System - Network Server
color 0A

echo ==========================================
echo    Legal Cases Management System
echo         Network Server Startup
echo ==========================================
echo.

REM Get current directory
cd /d "%~dp0"

REM Check if backend directory exists
if not exist "backend" (
    echo ERROR: Backend directory not found!
    echo Make sure you're running this from the app root directory.
    pause
    exit /b 1
)

echo [1/4] Checking network configuration...

REM Get local IP addresses
echo Your server will be available at:
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set "ip=%%i"
    setlocal enabledelayedexpansion
    set "ip=!ip: =!"
    echo   http://!ip!:8000
    endlocal
)
echo   http://127.0.0.1:8000 (local only)
echo.

echo [2/4] Checking port availability...
netstat -ano | findstr :8000 >nul
if %errorlevel% equ 0 (
    echo WARNING: Port 8000 is already in use!
    echo If you have another server running, stop it first.
    echo Current processes using port 8000:
    netstat -ano | findstr :8000
    echo.
    echo Do you want to continue anyway? (Y/N)
    set /p choice=
    if /i not "!choice!"=="y" (
        echo Server startup cancelled.
        pause
        exit /b 1
    )
)

echo [3/4] Starting Legal Cases Management Server...
echo.
echo Server Configuration:
echo   Host: 0.0.0.0 (all network interfaces)
echo   Port: 8000
echo   Environment: Production
echo.
echo Starting server... (Press Ctrl+C to stop)
echo ==========================================

cd backend

REM Start the server
python main.py

echo.
echo ==========================================
echo Server stopped.
echo ==========================================
pause
