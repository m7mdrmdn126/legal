@echo off
setlocal EnableDelayedExpansion
REM Legal Cases Management System - Windows Network Setup (Simple Version)

echo ==========================================
echo Legal Cases Server Network Setup (Windows)
echo ==========================================
echo.

REM Set the working IP address directly
set SERVER_IP=169.254.25.11
set SERVER_PORT=8000

echo Using server configuration:
echo IP Address: %SERVER_IP%
echo Port: %SERVER_PORT%
echo Full URL: http://%SERVER_IP%:%SERVER_PORT%
echo.

REM Check if server is running
echo [INFO] Checking if server is running on port %SERVER_PORT%...

REM First check if anything is listening on port 8000
netstat -an | findstr :%SERVER_PORT% >nul 2>&1
set PORT_CHECK=%errorLevel%

if %PORT_CHECK% equ 0 (
    echo [SUCCESS] Server is listening on port %SERVER_PORT%
    
    REM Check if listening on all interfaces
    netstat -an | findstr "0.0.0.0:%SERVER_PORT%" >nul 2>&1
    set ALL_INTERFACES=%errorLevel%
    
    if !ALL_INTERFACES! equ 0 (
        echo [SUCCESS] Server is listening on all interfaces (0.0.0.0:%SERVER_PORT%)
    ) else (
        echo [WARNING] Server might not be listening on all interfaces
        echo Current listening addresses:
        netstat -an | findstr :%SERVER_PORT%
        echo.
        echo Make sure server is started with: uvicorn main:app --host 0.0.0.0 --port %SERVER_PORT%
    )
    
    REM Continue with the rest of the script
    goto :continue_setup
    
) else (
    echo [ERROR] Server is NOT listening on port %SERVER_PORT%
    echo Please start the server first:
    echo cd backend ^&^& uvicorn main:app --host 0.0.0.0 --port %SERVER_PORT%
    echo.
    echo Or use the deployment script: deployment\setup-server.bat
    pause
    exit /b 1
)

:continue_setup

echo.

REM Configure Windows Firewall
echo [INFO] Configuring Windows Firewall rules...
netsh advfirewall firewall delete rule name="Legal Cases API Server" >nul 2>&1
netsh advfirewall firewall add rule name="Legal Cases API Server" dir=in action=allow protocol=TCP localport=%SERVER_PORT% >nul 2>&1
if %errorLevel% equ 0 (
    echo [SUCCESS] Windows Firewall rule added for port %SERVER_PORT%
) else (
    echo [WARNING] Could not add firewall rule - run as Administrator for automatic setup
    echo Manual firewall setup:
    echo 1. Open Windows Defender Firewall
    echo 2. Click "Advanced settings"
    echo 3. Add new "Inbound Rule"
    echo 4. Allow TCP port %SERVER_PORT%
    echo 5. Apply to all networks
)

echo.

REM Test connectivity
echo [INFO] Testing server connectivity...

REM Test with curl if available
where curl >nul 2>&1
if %errorLevel% equ 0 (
    echo Testing API endpoint...
    curl -s --max-time 10 http://%SERVER_IP%:%SERVER_PORT%/api/v1/info >nul 2>&1
    if !errorLevel! equ 0 (
        echo [SUCCESS] API is accessible at http://%SERVER_IP%:%SERVER_PORT%
    ) else (
        echo [WARNING] API test failed - but server might still be working
    )
) else (
    echo [INFO] curl not available - skipping API test
)

echo.

REM Network information summary
echo ==========================================
echo NETWORK CONFIGURATION SUMMARY
echo ==========================================
echo Server URL: http://%SERVER_IP%:%SERVER_PORT%
echo API Documentation: http://%SERVER_IP%:%SERVER_PORT%/docs
echo Health Check: http://%SERVER_IP%:%SERVER_PORT%/api/v1/info
echo.
echo Server Status: Running on all interfaces (0.0.0.0:%SERVER_PORT%)
echo Firewall: Port %SERVER_PORT% configured for incoming connections
echo.

REM Client configuration instructions
echo ==========================================
echo CLIENT DEVICE CONFIGURATION
echo ==========================================
echo For each client device that will use the desktop app:
echo.
echo 1. Create/edit .env file in the desktop app folder:
echo    SERVER_IP=%SERVER_IP%
echo    SERVER_PORT=%SERVER_PORT%
echo.
echo 2. Test connectivity from client device:
echo    ping %SERVER_IP%
echo    telnet %SERVER_IP% %SERVER_PORT%
echo.
echo 3. Test in web browser on client device:
echo    http://%SERVER_IP%:%SERVER_PORT%/docs
echo.

REM Save configuration
set CONFIG_FILE=%~dp0server-config.txt
echo Legal Cases Management Server Configuration > "%CONFIG_FILE%"
echo Generated: %DATE% %TIME% >> "%CONFIG_FILE%"
echo. >> "%CONFIG_FILE%"
echo Server IP: %SERVER_IP% >> "%CONFIG_FILE%"
echo Server Port: %SERVER_PORT% >> "%CONFIG_FILE%"
echo Server URL: http://%SERVER_IP%:%SERVER_PORT% >> "%CONFIG_FILE%"
echo API Docs: http://%SERVER_IP%:%SERVER_PORT%/docs >> "%CONFIG_FILE%"
echo. >> "%CONFIG_FILE%"
echo Client .env Configuration: >> "%CONFIG_FILE%"
echo SERVER_IP=%SERVER_IP% >> "%CONFIG_FILE%"
echo SERVER_PORT=%SERVER_PORT% >> "%CONFIG_FILE%"
echo. >> "%CONFIG_FILE%"
echo Test Commands for Client Devices: >> "%CONFIG_FILE%"
echo ping %SERVER_IP% >> "%CONFIG_FILE%"
echo telnet %SERVER_IP% %SERVER_PORT% >> "%CONFIG_FILE%"
echo curl http://%SERVER_IP%:%SERVER_PORT%/api/v1/info >> "%CONFIG_FILE%"
echo Browser: http://%SERVER_IP%:%SERVER_PORT%/docs >> "%CONFIG_FILE%"

echo ==========================================
echo [SUCCESS] Setup completed!
echo ==========================================
echo Configuration saved to: %CONFIG_FILE%
echo.
echo Next steps:
echo 1. Configure client devices with SERVER_IP=%SERVER_IP%
echo 2. Test connectivity from each client device
echo 3. Run desktop app on client devices
echo.
pause
