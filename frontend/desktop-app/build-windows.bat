@echo off
REM Legal Cases Desktop App - Windows Build Script

echo Building Legal Cases Desktop App for Windows...

REM Check if Node.js and npm are installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Node.js is not installed. Please install Node.js first.
    pause
    exit /b 1
)

where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: npm is not installed. Please install npm first.
    pause
    exit /b 1
)

REM Create simple icon if it doesn't exist
if not exist "build-assets\icon.ico" (
    echo Creating simple app icon...
    if not exist "build-assets" mkdir build-assets
    
    REM Create a simple SVG icon
    (
        echo ^<?xml version="1.0" encoding="UTF-8"?^>
        echo ^<svg width="256" height="256" viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg"^>
        echo   ^<rect width="256" height="256" rx="32" fill="#2563eb"/^>
        echo   ^<text x="128" y="140" font-family="Arial, sans-serif" font-size="180" font-weight="bold" text-anchor="middle" fill="white"^>⚖^</text^>
        echo   ^<text x="128" y="220" font-family="Arial, sans-serif" font-size="24" font-weight="bold" text-anchor="middle" fill="white"^>Legal Cases^</text^>
        echo ^</svg^>
    ) > build-assets\icon.svg
    
    echo Warning: Created SVG icon. For better results, convert to ICO format manually.
)

REM Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
)

REM Build React app
echo Building React application...
npm run build

REM Build Electron app for Windows
echo Building Electron app for Windows...
npm run electron-pack-win

echo Windows build completed!
echo The installer should be in the dist folder
pause
