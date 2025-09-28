# Fix Electron Installation Issues on Windows (PowerShell)
# Run this as Administrator for best results

Write-Host "==========================================" -ForegroundColor Green
Write-Host "Fixing Electron Installation on Windows" -ForegroundColor Green  
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Change to desktop app directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$desktopAppPath = Join-Path $scriptPath "frontend\desktop-app"

if (Test-Path $desktopAppPath) {
    Set-Location $desktopAppPath
    Write-Host "[INFO] Changed to: $desktopAppPath" -ForegroundColor Cyan
} else {
    Write-Host "[ERROR] Desktop app directory not found: $desktopAppPath" -ForegroundColor Red
    Write-Host "Make sure you're running this from the project root directory" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Step 1: Clean installation
Write-Host "[STEP 1] Cleaning up corrupted installation..." -ForegroundColor Yellow

if (Test-Path "node_modules") {
    Write-Host "Removing node_modules directory..." -ForegroundColor Cyan
    Remove-Item -Recurse -Force "node_modules" -ErrorAction SilentlyContinue
    Write-Host "[SUCCESS] Removed node_modules directory" -ForegroundColor Green
} else {
    Write-Host "[INFO] node_modules directory not found" -ForegroundColor Cyan
}

if (Test-Path "package-lock.json") {
    Remove-Item "package-lock.json" -ErrorAction SilentlyContinue
    Write-Host "[SUCCESS] Removed package-lock.json" -ForegroundColor Green
}

# Step 2: Clear caches
Write-Host ""
Write-Host "[STEP 2] Clearing caches..." -ForegroundColor Yellow

try {
    npm cache clean --force
    Write-Host "[SUCCESS] npm cache cleared" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] npm cache clean failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Clear Windows temp files related to npm/electron
$tempPaths = @(
    "$env:APPDATA\npm-cache",
    "$env:LOCALAPPDATA\electron",
    "$env:LOCALAPPDATA\electron-builder"
)

foreach ($path in $tempPaths) {
    if (Test-Path $path) {
        try {
            Remove-Item -Recurse -Force $path -ErrorAction SilentlyContinue
            Write-Host "[INFO] Cleared cache: $path" -ForegroundColor Cyan
        } catch {
            Write-Host "[WARNING] Could not clear: $path" -ForegroundColor Yellow
        }
    }
}

# Step 3: Install with Windows-specific settings
Write-Host ""
Write-Host "[STEP 3] Installing dependencies..." -ForegroundColor Yellow
Write-Host "This may take several minutes..." -ForegroundColor Cyan

# Set npm configuration for Windows
npm config set target_platform win32
npm config set target_arch x64
npm config set python python
npm config set msvs_version 2019

try {
    # Install dependencies with Windows-friendly options
    npm install --no-optional --no-shrinkwrap
    Write-Host "[SUCCESS] Dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Initial installation failed, trying alternative method..." -ForegroundColor Red
    
    try {
        # Alternative installation
        npm install --force --no-optional
        Write-Host "[SUCCESS] Alternative installation succeeded" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] All installation methods failed" -ForegroundColor Red
        Write-Host "Please check your internet connection and Node.js installation" -ForegroundColor Yellow
        Read-Host "Press Enter to continue with Electron-specific installation"
    }
}

# Step 4: Install Electron specifically
Write-Host ""
Write-Host "[STEP 4] Installing Electron specifically..." -ForegroundColor Yellow

try {
    npm install electron@latest --save-dev --no-optional
    Write-Host "[SUCCESS] Electron installed successfully" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Electron installation failed, trying global installation..." -ForegroundColor Red
    
    try {
        npm install -g electron
        Write-Host "[SUCCESS] Electron installed globally" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Global Electron installation also failed" -ForegroundColor Red
    }
}

# Step 5: Verify installation
Write-Host ""
Write-Host "[STEP 5] Verifying installation..." -ForegroundColor Yellow

Write-Host "Node.js version:" -ForegroundColor Cyan
node --version

Write-Host "npm version:" -ForegroundColor Cyan  
npm --version

Write-Host "Checking Electron..." -ForegroundColor Cyan
try {
    npm list electron
    Write-Host "[SUCCESS] Electron verification passed" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] Electron verification failed" -ForegroundColor Yellow
}

# Step 6: Test the application
Write-Host ""
Write-Host "[STEP 6] Testing application startup..." -ForegroundColor Yellow
Write-Host "Attempting to start the desktop application..." -ForegroundColor Cyan

try {
    # Try to start the application
    Start-Process "npm" -ArgumentList "run", "electron-dev" -NoNewWindow -Wait
} catch {
    Write-Host "[ERROR] Application startup failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Troubleshooting Complete" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

Write-Host ""
Write-Host "If issues persist, try these solutions:" -ForegroundColor Yellow
Write-Host "1. Run PowerShell as Administrator and retry" -ForegroundColor Cyan
Write-Host "2. Install Visual Studio Build Tools:" -ForegroundColor Cyan
Write-Host "   https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor Cyan
Write-Host "3. Install Python 3.x if not already installed" -ForegroundColor Cyan
Write-Host "4. Use Windows Subsystem for Linux (WSL)" -ForegroundColor Cyan
Write-Host "5. Use the pre-built installer in deployment/ folder" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to exit"
