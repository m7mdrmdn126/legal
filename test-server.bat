@echo off
setlocal EnableDelayedExpansion
REM Quick Server Test - Legal Cases Management System

echo ==========================================
echo Quick Server Network Test
echo ==========================================
echo.

set SERVER_IP=169.254.25.11
set SERVER_PORT=8000

echo Testing server at: http://%SERVER_IP%:%SERVER_PORT%
echo.

REM Show current listening ports
echo [INFO] Current network listeners on port %SERVER_PORT%:
netstat -an | findstr :%SERVER_PORT%
echo.

REM Test with PowerShell if available (more reliable than curl on Windows)
where powershell >nul 2>&1
if %errorLevel% equ 0 (
    echo [INFO] Testing connectivity with PowerShell...
    powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://%SERVER_IP%:%SERVER_PORT%/api/v1/info' -TimeoutSec 10 -UseBasicParsing; Write-Host '[SUCCESS] Server responded with status:' $response.StatusCode } catch { Write-Host '[ERROR] Connection failed:' $_.Exception.Message }"
) else (
    echo [INFO] PowerShell not available
)

echo.

REM Test with telnet if available
where telnet >nul 2>&1
if %errorLevel% equ 0 (
    echo [INFO] Testing port connectivity...
    echo Testing connection to %SERVER_IP%:%SERVER_PORT%
    echo This will timeout in 5 seconds if connection fails...
    timeout /t 1 >nul
    telnet %SERVER_IP% %SERVER_PORT%
) else (
    echo [INFO] Telnet not available - install with: dism /online /Enable-Feature /FeatureName:TelnetClient
)

echo.

REM Network diagnostics
echo [INFO] Network diagnostics:
echo Ping test to %SERVER_IP%:
ping -n 2 %SERVER_IP%

echo.
echo [INFO] Route to server:
tracert -h 5 %SERVER_IP%

echo.
echo ==========================================
echo Manual Test Commands:
echo ==========================================
echo 1. Open web browser and go to:
echo    http://%SERVER_IP%:%SERVER_PORT%/docs
echo.
echo 2. Test API with PowerShell:
echo    Invoke-WebRequest -Uri "http://%SERVER_IP%:%SERVER_PORT%/api/v1/info"
echo.
echo 3. Test with curl (if installed):
echo    curl http://%SERVER_IP%:%SERVER_PORT%/api/v1/info
echo.
pause
