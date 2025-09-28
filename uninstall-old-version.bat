@echo off
title Legal Cases - Uninstall Helper
color 0C

echo ==========================================
echo   Legal Cases Management System
echo        Uninstall Helper
echo ==========================================
echo.

echo This script will help you uninstall the old version
echo of Legal Cases Management Desktop App.
echo.

echo [METHOD 1] Windows Settings (Recommended)
echo ------------------------------------------
echo 1. Press Windows Key + I
echo 2. Go to Apps ^> Apps ^& features
echo 3. Search for "Legal Cases" or "legal-cases-desktop"
echo 4. Click on the app and select "Uninstall"
echo.

echo [METHOD 2] Control Panel
echo -------------------------
echo 1. Press Windows Key + R
echo 2. Type: appwiz.cpl
echo 3. Press Enter
echo 4. Find "Legal Cases Management" in the list
echo 5. Right-click and select "Uninstall"
echo.

echo [METHOD 3] Manual Removal
echo --------------------------
echo If the app doesn't appear in the above locations,
echo it might be installed as a portable app or in these locations:
echo.
echo Common installation directories:
echo   C:\Program Files\Legal Cases Management\
echo   C:\Program Files (x86)\Legal Cases Management\
echo   C:\Users\%USERNAME%\AppData\Local\Programs\legal-cases-desktop\
echo   %LOCALAPPDATA%\Programs\legal-cases-desktop\
echo.

echo Do you want to check these directories? (Y/N)
set /p checkdirs=

if /i "%checkdirs%"=="y" (
    echo.
    echo Checking common installation directories...
    echo.
    
    if exist "C:\Program Files\Legal Cases Management\" (
        echo ✓ Found: C:\Program Files\Legal Cases Management\
        dir "C:\Program Files\Legal Cases Management\"
        echo.
    )
    
    if exist "C:\Program Files (x86)\Legal Cases Management\" (
        echo ✓ Found: C:\Program Files ^(x86^)\Legal Cases Management\
        dir "C:\Program Files (x86)\Legal Cases Management\"
        echo.
    )
    
    if exist "%LOCALAPPDATA%\Programs\legal-cases-desktop\" (
        echo ✓ Found: %LOCALAPPDATA%\Programs\legal-cases-desktop\
        dir "%LOCALAPPDATA%\Programs\legal-cases-desktop\"
        echo.
    )
    
    echo If you found the app directory above, you can:
    echo 1. Look for uninstall.exe in that directory
    echo 2. Or manually delete the entire folder
)

echo.
echo [CLEAN APP DATA] Optional Cleanup
echo ---------------------------------
echo After uninstalling, you may want to clean app data:
echo.

echo Do you want to clean old app data and settings? (Y/N)
set /p cleandata=

if /i "%cleandata%"=="y" (
    echo Cleaning app data...
    
    if exist "%APPDATA%\legal-cases-desktop\" (
        echo Removing: %APPDATA%\legal-cases-desktop\
        rmdir /s /q "%APPDATA%\legal-cases-desktop\" 2>nul
    )
    
    if exist "%LOCALAPPDATA%\legal-cases-desktop\" (
        echo Removing: %LOCALAPPDATA%\legal-cases-desktop\
        rmdir /s /q "%LOCALAPPDATA%\legal-cases-desktop\" 2>nul
    )
    
    REM Clean temp files
    del "%TEMP%\legal-cases*" /s /q 2>nul
    
    echo ✓ App data cleaned
) else (
    echo App data cleanup skipped
)

echo.
echo ==========================================
echo           Uninstall Complete
echo ==========================================
echo.
echo After uninstalling the old version:
echo.
echo 1. BUILD new version:
echo    - Run: deploy-production.bat
echo    - Or manually: npm run build ^& npm run dist
echo.
echo 2. INSTALL new version:
echo    - Navigate to: frontend\desktop-app\dist\
echo    - Run the new installer
echo.
echo 3. CONFIGURE network:
echo    - Run: setup-windows-network.bat (as Administrator)
echo.
echo 4. START server:
echo    - Run: start-network-server.bat
echo.
echo ==========================================

pause
