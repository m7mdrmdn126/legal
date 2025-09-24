@echo off
REM Legal Cases Management System - Client Configuration (Simple Batch)
REM This script configures the desktop app to connect to a network server

if "%1"=="" (
    echo ERROR: Server IP address is required!
    echo Usage: configure-client.bat [SERVER_IP] [PORT]
    echo Example: configure-client.bat 192.168.1.100
    echo Example: configure-client.bat 192.168.1.100 8000
    pause
    exit /b 1
)

set SERVER_IP=%1
set SERVER_PORT=%2
if "%SERVER_PORT%"=="" set SERVER_PORT=8000

echo ===============================================
echo Legal Cases Client Configuration
echo ===============================================
echo Server IP: %SERVER_IP%
echo Server Port: %SERVER_PORT%
echo.

REM Test server connection
echo Testing connection to server...
powershell -Command "try { Invoke-WebRequest -Uri 'http://%SERVER_IP%:%SERVER_PORT%/api/v1/info' -TimeoutSec 5 -UseBasicParsing | Out-Null; Write-Host 'Server is accessible' } catch { Write-Host 'Cannot connect to server'; exit 1 }"

if %errorLevel% neq 0 (
    echo ERROR: Cannot connect to server at http://%SERVER_IP%:%SERVER_PORT%
    echo Please ensure:
    echo 1. Server is running on %SERVER_IP%
    echo 2. Port %SERVER_PORT% is open
    echo 3. No firewall is blocking the connection
    pause
    exit /b 1
)

REM Update API configuration file
set API_FILE="%~dp0\..\frontend\desktop-app\src\services\api.js"

if not exist %API_FILE% (
    echo ERROR: API service file not found!
    echo Expected location: %API_FILE%
    pause
    exit /b 1
)

echo Updating API configuration...

REM Create temporary PowerShell script to update the file
echo $content = Get-Content '%API_FILE%' -Raw > temp_update.ps1
echo $content = $content -replace "const API_BASE_URL = 'http://localhost:8000/api/v1';", "const API_BASE_URL = 'http://%SERVER_IP%:%SERVER_PORT%/api/v1';" >> temp_update.ps1
echo $content ^| Set-Content '%API_FILE%' -NoNewline >> temp_update.ps1

powershell -ExecutionPolicy Bypass -File temp_update.ps1
del temp_update.ps1

echo.
echo ===============================================
echo Configuration completed successfully!
echo ===============================================
echo The desktop app is now configured to connect to:
echo   Server: http://%SERVER_IP%:%SERVER_PORT%
echo.
echo To start the desktop app:
echo   1. Navigate to: frontend\desktop-app
echo   2. Run: npm install (first time only)
echo   3. Run: npm run electron-dev
echo.
pause
