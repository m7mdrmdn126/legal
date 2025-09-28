@echo off
setlocal EnableDelayedExpansion
REM Legal Cases Server Startup Script with Network CORS Support

echo ==========================================
echo Legal Cases Server - Network Startup
echo ==========================================
echo.

REM Set environment variables for network access
set HOST=0.0.0.0
set PORT=8000
set DEBUG=true
set CORS_ORIGINS=http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000,http://127.0.0.1:8080,http://169.254.25.11:3000,http://169.254.25.11:8080,http://10.79.245.12:3000,http://10.79.245.12:8080

echo Server Configuration:
echo Host: %HOST%
echo Port: %PORT%
echo CORS Origins: Local network access enabled
echo.

REM Change to backend directory
cd /d "%~dp0backend"

REM Check if Python is available
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python not found! Please install Python 3.9+
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements
echo [INFO] Installing/updating dependencies...
pip install -r requirements.txt

echo.
echo [INFO] Starting server with network CORS support...
echo Server will be accessible at:
echo - Local: http://localhost:8000
echo - Network: http://169.254.25.11:8000
echo - API Docs: http://169.254.25.11:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server with network configuration
uvicorn main:app --host %HOST% --port %PORT% --reload

pause
