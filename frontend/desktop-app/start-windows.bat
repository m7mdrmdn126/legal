@echo off
REM Windows startup script for the Legal Cases Desktop App

echo Starting Legal Cases Desktop Application...
echo.

REM Set environment variables for Windows
set GENERATE_SOURCEMAP=false
set NODE_NO_WARNINGS=1

echo Installing dependencies if needed...
if not exist "node_modules" (
    echo Installing npm packages...
    npm install
)

echo.
echo Starting development server and Electron...
npm run electron-dev

pause
