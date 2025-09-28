@echo off
REM Fix Electron Installation Issues on Windows

echo ==========================================
echo Fixing Electron Installation on Windows
echo ==========================================
echo.

REM Change to desktop app directory
cd /d "%~dp0frontend\desktop-app"

echo [INFO] Current directory: %CD%
echo.

echo [STEP 1] Cleaning up corrupted installation...
echo Removing node_modules...
if exist "node_modules" (
    rmdir /s /q "node_modules"
    echo [SUCCESS] Removed node_modules directory
) else (
    echo [INFO] node_modules directory not found
)

echo.
echo Removing package-lock.json...
if exist "package-lock.json" (
    del "package-lock.json"
    echo [SUCCESS] Removed package-lock.json
) else (
    echo [INFO] package-lock.json not found
)

echo.
echo [STEP 2] Clearing npm cache...
npm cache clean --force
if %errorLevel% equ 0 (
    echo [SUCCESS] npm cache cleared
) else (
    echo [WARNING] npm cache clean failed
)

echo.
echo [STEP 3] Installing dependencies with specific Electron version...
echo This may take several minutes...

REM Install with specific flags for Windows
npm install --no-optional --no-shrinkwrap --no-package-lock
if %errorLevel% neq 0 (
    echo [ERROR] npm install failed
    echo Trying alternative installation method...
    
    REM Try with different approach
    npm install --cache-min 86400 --no-optional
    if %errorLevel% neq 0 (
        echo [ERROR] Alternative installation also failed
        echo Please check your internet connection and try manually:
        echo 1. cd frontend\desktop-app
        echo 2. npm install
        pause
        exit /b 1
    )
)

echo.
echo [STEP 4] Installing Electron separately...
npm install electron@latest --save-dev
if %errorLevel% equ 0 (
    echo [SUCCESS] Electron installed successfully
) else (
    echo [ERROR] Electron installation failed
    echo Trying global installation...
    npm install -g electron
)

echo.
echo [STEP 5] Verifying installation...
node -e "console.log('Node.js version:', process.version)"
npm list electron
if %errorLevel% equ 0 (
    echo [SUCCESS] Electron verification passed
) else (
    echo [WARNING] Electron verification failed, but installation might still work
)

echo.
echo [STEP 6] Testing Electron...
echo Attempting to start the application...
npm run electron-dev

echo.
echo ==========================================
echo If the issue persists, try these manual steps:
echo ==========================================
echo 1. Close all Node.js/Electron processes
echo 2. Delete the entire legal-main folder
echo 3. Re-extract from ZIP or re-clone from GitHub
echo 4. Run this script again
echo.
echo Alternative: Use the pre-built installer instead
echo Check the deployment folder for setup-client.bat
echo.
pause
