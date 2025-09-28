@echo off
REM Legal Cases Management System - Windows Network Setup Script
REM Run as Administrator

echo ========================================
echo Legal Cases Management System
echo Windows Network Configuration
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo [1/6] Configuring Windows Firewall for port 8000...

REM Add inbound rule for port 8000
netsh advfirewall firewall add rule name="Legal Cases API - Port 8000" dir=in action=allow protocol=TCP localport=8000 >nul 2>&1
if %errorlevel% equ 0 (
    echo     ✓ Firewall rule added successfully
) else (
    echo     ⚠ Firewall rule may already exist
)

REM Add outbound rule for port 8000
netsh advfirewall firewall add rule name="Legal Cases API - Port 8000 Out" dir=out action=allow protocol=TCP localport=8000 >nul 2>&1

echo [2/6] Getting network information...

REM Get IP addresses
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set "ip=%%i"
    setlocal enabledelayedexpansion
    set "ip=!ip: =!"
    echo     Local IP: !ip!
    endlocal
)

echo [3/6] Testing port 8000 availability...
netstat -ano | findstr :8000 >nul
if %errorlevel% equ 0 (
    echo     ✓ Port 8000 is in use (server may be running)
    netstat -ano | findstr :8000
) else (
    echo     ⚠ Port 8000 is not in use (server not running?)
)

echo [4/6] Creating startup scripts...

REM Create server startup script
(
echo @echo off
echo echo Starting Legal Cases Management System Server...
echo cd /d "%~dp0backend"
echo echo Server will be available at:
echo for /f "tokens=2 delims=:" %%%%i in ('ipconfig ^| findstr /c:"IPv4 Address"'^) do ^(
echo     set "ip=%%%%i"
echo     setlocal enabledelayedexpansion
echo     set "ip=!ip: =!"
echo     echo   http://!ip!:8000
echo     endlocal
echo ^)
echo echo.
echo echo Starting server...
echo python main.py
echo pause
) > start-legal-cases-server.bat

echo     ✓ Created start-legal-cases-server.bat

REM Create client configuration helper
(
echo @echo off
echo echo Legal Cases Management System - Client Configuration
echo echo ================================================
echo echo.
echo echo Use one of these server URLs in your client applications:
echo echo.
echo for /f "tokens=2 delims=:" %%%%i in ('ipconfig ^| findstr /c:"IPv4 Address"'^) do ^(
echo     set "ip=%%%%i"
echo     setlocal enabledelayedexpansion
echo     set "ip=!ip: =!"
echo     echo   Server URL: http://!ip!:8000
echo     echo   API Base:   http://!ip!:8000/api/v1
echo     echo.
echo     endlocal
echo ^)
echo echo ================================================
echo pause
) > get-server-urls.bat

echo     ✓ Created get-server-urls.bat

echo [5/6] Testing network connectivity...

REM Test if we can reach localhost
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://127.0.0.1:8000' -TimeoutSec 5; Write-Host '     ✓ Local server responding: HTTP' $response.StatusCode } catch { Write-Host '     ✗ Local server not responding:' $_.Exception.Message }"

echo [6/6] Configuration complete!

echo.
echo ========================================
echo Configuration Summary
echo ========================================
echo ✓ Windows Firewall configured for port 8000
echo ✓ Startup scripts created
echo ✓ Network connectivity tested
echo.
echo Next Steps:
echo 1. Start the server using: start-legal-cases-server.bat
echo 2. Get server URLs using: get-server-urls.bat  
echo 3. Configure client apps with the server URLs
echo.
echo Troubleshooting:
echo - If clients still can't connect, temporarily disable Windows Defender Firewall
echo - Ensure all devices are on the same network
echo - Check antivirus software settings
echo.
echo ========================================

pause
