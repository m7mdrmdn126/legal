@echo off
REM Legal Cases Management System - Windows Server Setup (Simple Batch)
REM Run this as Administrator for initial setup

echo ===============================================
echo Legal Cases Management System - Setup
echo ===============================================

REM Check if running as Administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo Right-click Command Prompt and select "Run as administrator"
    pause
    exit /b 1
)

echo Creating directories...
if not exist "C:\legal-cases\database" mkdir "C:\legal-cases\database"
if not exist "C:\legal-cases\logs" mkdir "C:\legal-cases\logs"
if not exist "C:\legal-cases\backups" mkdir "C:\legal-cases\backups"

echo Checking Python installation...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python from: https://www.python.org/downloads/windows/
    pause
    exit /b 1
)

echo Configuring Windows Firewall...
netsh advfirewall firewall add rule name="Legal Cases API Server" dir=in action=allow protocol=TCP localport=8000

echo Setting up Python environment...
cd /d "%~dp0\..\backend"

REM Create virtual environment
if not exist "venv" (
    python -m venv venv
    echo Created virtual environment
)

REM Install packages
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ===============================================
echo Setup completed successfully!
echo ===============================================
echo.
echo Next steps:
echo 1. Run start-server.bat to start the server
echo 2. Configure client devices to connect to this server
echo 3. The server will be accessible on port 8000
echo.

REM Get IP address
echo Your server IP address:
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do echo %%a

echo.
pause
