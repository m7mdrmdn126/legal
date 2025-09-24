@echo off
REM Legal Cases Management System - Clean Development Start (Windows)
REM This script starts the application with reduced console noise

echo Starting Legal Cases Management System...
echo ========================================

REM Suppress Node.js deprecation warnings
set NODE_NO_WARNINGS=1
set NODE_OPTIONS=--no-deprecation --no-warnings

REM Start the application
npm run electron-dev
