# Legal Cases Desktop App - Windows PowerShell Development Script
# This script optimizes the development environment for Windows

Write-Host "Legal Cases Desktop Application - Windows Development Setup" -ForegroundColor Green
Write-Host "=============================================================" -ForegroundColor Green
Write-Host

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js from https://nodejs.org/" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if npm is installed
try {
    $npmVersion = npm --version
    Write-Host "✅ npm found: v$npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ npm not found. Please install npm." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host

# Set environment variables for optimal Windows performance
$env:GENERATE_SOURCEMAP = "false"
$env:NODE_NO_WARNINGS = "1"
$env:NODE_OPTIONS = "--max-old-space-size=4096"

Write-Host "Setting Windows-optimized environment variables..." -ForegroundColor Yellow
Write-Host "  GENERATE_SOURCEMAP=false (faster builds)" -ForegroundColor Gray
Write-Host "  NODE_NO_WARNINGS=1 (cleaner output)" -ForegroundColor Gray
Write-Host "  NODE_OPTIONS=--max-old-space-size=4096 (more memory)" -ForegroundColor Gray
Write-Host

# Install dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "✅ Dependencies already installed" -ForegroundColor Green
}

Write-Host

# Menu for different actions
Write-Host "Choose an action:" -ForegroundColor Cyan
Write-Host "1. Start development server (React + Electron)" -ForegroundColor White
Write-Host "2. Build for Windows production" -ForegroundColor White
Write-Host "3. Run React app only (web browser)" -ForegroundColor White
Write-Host "4. Install/Update dependencies" -ForegroundColor White
Write-Host "5. Exit" -ForegroundColor White
Write-Host

$choice = Read-Host "Enter choice (1-5)"

switch ($choice) {
    "1" {
        Write-Host "🚀 Starting development environment..." -ForegroundColor Green
        npm run electron-dev
    }
    "2" {
        Write-Host "🔨 Building Windows application..." -ForegroundColor Green
        npm run build
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Build completed successfully" -ForegroundColor Green
            npm run electron-pack-win
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Windows installer created in 'dist' folder" -ForegroundColor Green
            }
        }
    }
    "3" {
        Write-Host "🌐 Starting React development server..." -ForegroundColor Green
        npm start
    }
    "4" {
        Write-Host "📦 Updating dependencies..." -ForegroundColor Yellow
        npm install
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Dependencies updated successfully" -ForegroundColor Green
        }
    }
    "5" {
        Write-Host "👋 Goodbye!" -ForegroundColor Green
        exit 0
    }
    default {
        Write-Host "❌ Invalid choice. Please run the script again." -ForegroundColor Red
    }
}

Write-Host
Read-Host "Press Enter to exit"
