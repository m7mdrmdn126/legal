@echo off
REM Legal Cases Management System - Build Desktop Application for Windows

echo ===============================================
echo Building Legal Cases Desktop Application
echo ===============================================

REM Change to desktop app directory
cd /d "%~dp0\..\frontend\desktop-app"

if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
    if %errorLevel% neq 0 (
        echo ERROR: Failed to install dependencies!
        pause
        exit /b 1
    )
)

echo Building application...
call npm run build-windows

if %errorLevel% equ 0 (
    echo.
    echo ===============================================
    echo Build completed successfully!
    echo ===============================================
    echo.
    echo The installer is located in:
    echo   frontend\desktop-app\dist\
    echo.
    echo Files created:
    dir dist\*.exe 2>nul
    echo.
    echo To distribute the application:
    echo 1. Copy the installer (.exe) to target devices
    echo 2. Edit the .env file to configure server IP
    echo 3. Install and run the application
    echo.
) else (
    echo.
    echo ===============================================
    echo Build failed!
    echo ===============================================
    echo Please check the error messages above.
)

pause
