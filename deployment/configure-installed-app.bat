@echo off
REM Legal Cases Management System - Quick Client Configuration
REM This script configures the desktop application after installation

echo ===============================================
echo Legal Cases Client Configuration
echo ===============================================
echo.

REM Get server IP from user
set /p SERVER_IP="Enter server IP address (e.g., 192.168.1.100): "

if "%SERVER_IP%"=="" (
    echo ERROR: Server IP address is required!
    pause
    exit /b 1
)

REM Find configuration file location
set CONFIG_FILE="%LOCALAPPDATA%\Programs\Legal Cases Management\.env"

REM Alternative locations to check
if not exist %CONFIG_FILE% (
    set CONFIG_FILE="%PROGRAMFILES%\Legal Cases Management\.env"
)

if not exist %CONFIG_FILE% (
    set CONFIG_FILE="%PROGRAMFILES(X86)%\Legal Cases Management\.env"
)

REM Create configuration file
echo Creating configuration file...
echo # Legal Cases Management System - Client Configuration > %CONFIG_FILE%
echo # Edit this file to configure the server connection >> %CONFIG_FILE%
echo. >> %CONFIG_FILE%
echo # Server Configuration >> %CONFIG_FILE%
echo SERVER_IP=%SERVER_IP% >> %CONFIG_FILE%
echo SERVER_PORT=8000 >> %CONFIG_FILE%
echo. >> %CONFIG_FILE%
echo # Application Settings >> %CONFIG_FILE%
echo APP_NAME=Legal Cases Management >> %CONFIG_FILE%
echo APP_VERSION=1.0.0 >> %CONFIG_FILE%
echo. >> %CONFIG_FILE%
echo # Auto-connect settings >> %CONFIG_FILE%
echo AUTO_CONNECT=true >> %CONFIG_FILE%
echo SHOW_SERVER_CONFIG=true >> %CONFIG_FILE%

if exist %CONFIG_FILE% (
    echo.
    echo ===============================================
    echo Configuration completed successfully!
    echo ===============================================
    echo.
    echo Configuration saved to:
    echo   %CONFIG_FILE%
    echo.
    echo Server IP: %SERVER_IP%
    echo Server Port: 8000
    echo.
    echo You can now launch the Legal Cases Management application.
    echo.
) else (
    echo.
    echo ERROR: Could not create configuration file!
    echo.
    echo Please manually create the .env file in the application directory
    echo and add the following content:
    echo.
    echo SERVER_IP=%SERVER_IP%
    echo SERVER_PORT=8000
    echo APP_NAME=Legal Cases Management
    echo AUTO_CONNECT=true
    echo.
)

pause
