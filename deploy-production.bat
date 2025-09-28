@echo off
title Legal Cases - Production Deployment Helper
color 0B

echo ==========================================
echo   Legal Cases Management System
echo     Production Deployment Helper
echo ==========================================
echo.

REM Check if running from correct directory
if not exist "backend" (
    echo ERROR: Please run this script from the app root directory
    echo Current directory: %CD%
    echo Expected: Contains 'backend' and 'frontend' folders
    pause
    exit /b 1
)

echo [STEP 1] Checking environment...
echo Current directory: %CD%
echo.

REM Check if git is available
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Git not found in PATH. Please update code manually.
) else (
    echo Git available: 
    git --version
)

echo.
echo [STEP 2] Do you want to pull the latest code? (Y/N)
set /p pullcode=
if /i "%pullcode%"=="y" (
    echo Pulling latest code...
    git pull origin main
    if %errorlevel% neq 0 (
        echo ERROR: Failed to pull code. Please check git status.
        pause
        exit /b 1
    )
    echo ✓ Code updated successfully
) else (
    echo Skipping code update
)

echo.
echo [STEP 3] Backend Dependencies Check
echo Checking Python and dependencies...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found! Please install Python first.
    pause
    exit /b 1
)

echo Python found:
python --version

cd backend

REM Check if virtual environment exists
if exist ".venv" (
    echo Found virtual environment, activating...
    call .venv\Scripts\activate.bat
)

echo Installing/updating dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo ✓ Backend dependencies ready

cd ..

echo.
echo [STEP 4] Network Configuration
echo.
echo IMPORTANT: Network setup requires Administrator privileges
echo This will configure Windows Firewall for port 8000
echo.
echo Do you want to run network setup now? (Y/N)
echo (If you choose No, run 'setup-windows-network.bat' as Administrator later)
set /p setupnet=

if /i "%setupnet%"=="y" (
    echo Checking administrator privileges...
    net session >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERROR: Administrator privileges required!
        echo Please:
        echo 1. Close this window
        echo 2. Right-click Command Prompt
        echo 3. Select 'Run as administrator'
        echo 4. Run: setup-windows-network.bat
        pause
        exit /b 1
    )
    
    echo Running network setup...
    call setup-windows-network.bat
    echo ✓ Network configuration complete
) else (
    echo ⚠ Network setup skipped - run 'setup-windows-network.bat' as Administrator later
)

echo.
echo [STEP 5] Frontend Build Process
echo.
echo Do you want to build the desktop app installer? (Y/N)
set /p buildapp=

if /i "%buildapp%"=="y" (
    echo Building desktop application...
    
    cd frontend\desktop-app
    
    echo Checking Node.js...
    node --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERROR: Node.js not found! Please install Node.js first.
        pause
        exit /b 1
    )
    
    echo Node.js found:
    node --version
    
    echo Installing dependencies...
    npm install
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install npm dependencies
        pause
        exit /b 1
    )
    
    echo Building production app...
    npm run build
    if %errorlevel% neq 0 (
        echo ERROR: Build failed
        pause
        exit /b 1
    )
    
    echo Creating installer...
    npm run dist
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create installer
        pause
        exit /b 1
    )
    
    echo ✓ Desktop app built successfully!
    echo Installer location: frontend\desktop-app\dist\
    
    cd ..\..
) else (
    echo Desktop app build skipped
)

echo.
echo ==========================================
echo    Deployment Summary
echo ==========================================
echo.
echo ✓ Code updated (if selected)
echo ✓ Backend dependencies ready  
echo ✓ Network setup (if run as Admin)
echo ✓ Desktop app built (if selected)
echo.
echo NEXT STEPS:
echo.
echo 1. UNINSTALL old desktop app version:
echo    - Go to Settings ^> Apps ^> Apps ^& features
echo    - Find 'Legal Cases Management' and uninstall
echo.
echo 2. INSTALL new version:
echo    - Navigate to: frontend\desktop-app\dist\
echo    - Run the installer (.exe file)
echo.
echo 3. START the server:
echo    - Run: start-network-server.bat
echo.
echo 4. CONFIGURE client apps:
echo    - Open desktop app ^> Settings
echo    - Enter server IP: [Your server IP]
echo    - Port: 8000
echo    - Test connection
echo.
echo 5. GET server URLs:
echo    - Run: get-server-urls.bat
echo.
echo ==========================================

echo.
echo Do you want to start the server now? (Y/N)
set /p startserver=
if /i "%startserver%"=="y" (
    echo Starting Legal Cases server...
    start-network-server.bat
) else (
    echo Server not started. Run 'start-network-server.bat' when ready.
)

echo.
echo Deployment helper complete!
pause
