@echo off
echo Building Legal Cases Desktop App for Windows...

:: Set environment variables for build
set GENERATE_SOURCEMAP=false
set PUBLIC_URL=./

:: Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

:: Install dependencies if needed
echo Installing dependencies...
call npm install

:: Build React app
echo Building React application...
call npm run build

:: Check if build was successful
if not exist build\index.html (
    echo ERROR: React build failed!
    pause
    exit /b 1
)

:: Build Electron app for Windows
echo Building Electron app for Windows...
call npm run electron-pack-win

:: Check if Electron build was successful
if exist dist (
    echo.
    echo ✅ Build completed successfully!
    echo Built files are in the 'dist' directory
    echo.
    dir dist
) else (
    echo.
    echo ❌ Electron build failed!
    echo.
)

echo.
echo To debug the built app, run:
echo electron debug-build.js
echo.
pause
