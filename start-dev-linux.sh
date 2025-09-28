#!/bin/bash
# Legal Cases Management System - Linux Development Setup

echo "=========================================="
echo "   Legal Cases Management System"
echo "      Linux Development Setup"  
echo "=========================================="
echo

# Check if we're in the right directory
if [ ! -d "frontend/desktop-app" ]; then
    echo "ERROR: Please run this script from the app root directory"
    echo "Current directory: $(pwd)"
    echo "Expected: Contains 'frontend/desktop-app' folder"
    exit 1
fi

echo "[1/4] Checking Node.js and npm..."
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js not found. Please install Node.js first."
    echo "Install with: sudo apt install nodejs npm"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "ERROR: npm not found. Please install npm first."
    echo "Install with: sudo apt install npm"
    exit 1
fi

echo "Node.js version: $(node --version)"
echo "npm version: $(npm --version)"

echo
echo "[2/4] Installing frontend dependencies..."
cd frontend/desktop-app

# Install dependencies
npm install
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed successfully"

echo
echo "[3/4] Checking backend server..."
if pgrep -f "python.*main.py" > /dev/null; then
    echo "✓ Backend server appears to be running"
else
    echo "⚠️  Backend server not detected"
    echo "   To start backend server:"
    echo "   cd ../../backend && python3 main.py"
fi

echo
echo "[4/4] Starting Electron development environment..."
echo
echo "Starting React development server and Electron..."
echo "This will open the desktop application window."
echo

# Start the development environment
npm run electron-dev

echo
echo "Development session ended."
