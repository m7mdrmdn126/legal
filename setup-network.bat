@echo off
setlocal EnableDelayedExpansion
REM Legal Cases Management System - Windows Network Setup and Test Script

echo ==========================================
echo Legal Cases Server Network Setup (Windows)
echo ==========================================
echo.

REM Get server IP address
echo [INFO] Detecting available IP addresses...
echo Available network interfaces:
ipconfig | findstr /c:"IPv4 Address"
echo.

REM Try to get the main network IP (not localhost or auto-config)
set SERVER_IP=
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set TEMP_IP=%%i
    set TEMP_IP=!TEMP_IP: =!
    REM Skip localhost and auto-config IPs
    if not "!TEMP_IP!"=="127.0.0.1" (
        if not "!TEMP_IP:~0,7!"=="169.254" (
            if not defined SERVER_IP set SERVER_IP=!TEMP_IP!
        )
    )
)

REM If no suitable IP found, get the first available IP
if "%SERVER_IP%"=="" (
    for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
        set SERVER_IP=%%i
        set SERVER_IP=!SERVER_IP: =!
        goto :ip_found
    )
    :ip_found
)

REM Allow user to override IP if auto-detection is wrong
if "%SERVER_IP%"=="" (
    echo [ERROR] Could not detect server IP address
    echo Please run 'ipconfig' manually to find your IP address
    pause
    exit /b 1
)

echo Auto-detected IP: %SERVER_IP%
echo.
set /p USER_IP="Enter server IP address (or press Enter to use %SERVER_IP%): "
if not "%USER_IP%"=="" set SERVER_IP=%USER_IP%

echo Using server IP: %SERVER_IP%
echo.

REM Check if server is running
echo [INFO] Checking if server is running on port 8000...
netstat -an | findstr :8000 >nul 2>&1
if %errorLevel% equ 0 (
    echo [SUCCESS] Server is listening on port 8000
    
    REM Check if listening on all interfaces
    netstat -an | findstr 0.0.0.0:8000 >nul 2>&1
    if %errorLevel% equ 0 (
        echo [SUCCESS] Server is listening on all interfaces (0.0.0.0:8000)
    ) else (
        echo [WARNING] Server might not be listening on all interfaces
        echo Make sure server is started with: uvicorn main:app --host 0.0.0.0 --port 8000
    )
) else (
    echo [ERROR] Server is NOT listening on port 8000
    echo Please start the server first:
    echo cd backend ^&^& uvicorn main:app --host 0.0.0.0 --port 8000
    pause
    exit /b 1
)

echo.

REM Configure Windows Firewall
echo [INFO] Configuring Windows Firewall rules...
netsh advfirewall firewall add rule name="Legal Cases API Server" dir=in action=allow protocol=TCP localport=8000 >nul 2>&1
if %errorLevel% equ 0 (
    echo [SUCCESS] Windows Firewall rule added for port 8000
) else (
    echo [WARNING] Could not add firewall rule (may already exist or need admin rights)
    echo Run as Administrator to configure firewall automatically
)

echo.

REM Test local connectivity
echo [INFO] Testing local server connectivity...

REM Test localhost
curl -s --max-time 5 http://localhost:8000/api/v1/info >nul 2>&1
if %errorLevel% equ 0 (
    echo [SUCCESS] Local API access working (localhost:8000)
) else (
    echo [ERROR] Local API access failed (localhost:8000)
)

REM Test network IP
curl -s --max-time 5 http://%SERVER_IP%:8000/api/v1/info >nul 2>&1
if %errorLevel% equ 0 (
    echo [SUCCESS] Network API access working (%SERVER_IP%:8000)
) else (
    echo [ERROR] Network API access failed (%SERVER_IP%:8000)
    echo [WARNING] This means other devices won't be able to connect!
)

echo.

REM Network information
echo [INFO] Network configuration summary:
echo Server listening on: 0.0.0.0:8000
echo Server IP address: %SERVER_IP%
echo Local access URL: http://localhost:8000
echo Network access URL: http://%SERVER_IP%:8000
echo API documentation: http://%SERVER_IP%:8000/docs

echo.

REM Client configuration
echo [INFO] Client device configuration:
echo Edit the .env file on each client device:
echo SERVER_IP=%SERVER_IP%
echo SERVER_PORT=8000

echo.

REM Test commands for client devices
echo [INFO] Test commands for CLIENT devices:
echo 1. Test connectivity:
echo    ping %SERVER_IP%
echo.
echo 2. Test port access:
echo    telnet %SERVER_IP% 8000
echo.
echo 3. Test API access:
echo    curl http://%SERVER_IP%:8000/api/v1/info
echo.
echo 4. Test in web browser:
echo    http://%SERVER_IP%:8000/docs

echo.

REM Save configuration for reference
set CONFIG_FILE=%USERPROFILE%\legal-cases-server-config.txt
echo Legal Cases Management Server Configuration > "%CONFIG_FILE%"
echo ========================================== >> "%CONFIG_FILE%"
echo Generated: %DATE% %TIME% >> "%CONFIG_FILE%"
echo. >> "%CONFIG_FILE%"
echo Server IP: %SERVER_IP% >> "%CONFIG_FILE%"
echo Server Port: 8000 >> "%CONFIG_FILE%"
echo Network URL: http://%SERVER_IP%:8000 >> "%CONFIG_FILE%"
echo API Docs: http://%SERVER_IP%:8000/docs >> "%CONFIG_FILE%"
echo. >> "%CONFIG_FILE%"
echo Client Configuration: >> "%CONFIG_FILE%"
echo SERVER_IP=%SERVER_IP% >> "%CONFIG_FILE%"
echo SERVER_PORT=8000 >> "%CONFIG_FILE%"
echo. >> "%CONFIG_FILE%"
echo Test Commands (run on client devices): >> "%CONFIG_FILE%"
echo ping %SERVER_IP% >> "%CONFIG_FILE%"
echo curl http://%SERVER_IP%:8000/api/v1/info >> "%CONFIG_FILE%"
echo. >> "%CONFIG_FILE%"
echo Firewall: Port 8000 allowed for local networks >> "%CONFIG_FILE%"

echo ==========================================
echo [SUCCESS] Network setup completed!
echo ==========================================
echo [SUCCESS] Configuration saved to: %CONFIG_FILE%
echo.
pause
