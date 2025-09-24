# Legal Cases Management System - Build Desktop Application (PowerShell)

param(
    [string]$Platform = "windows",
    [switch]$Help
)

# Configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir
$DesktopAppDir = Join-Path $ProjectRoot "frontend\desktop-app"

function Write-Success($message) {
    Write-Host "[SUCCESS] $message" -ForegroundColor Green
}

function Write-Error($message) {
    Write-Host "[ERROR] $message" -ForegroundColor Red
}

function Write-Info($message) {
    Write-Host "[INFO] $message" -ForegroundColor Cyan
}

function Test-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    # Check Node.js
    try {
        $nodeVersion = node --version 2>$null
        Write-Success "Node.js found: $nodeVersion"
    } catch {
        Write-Error "Node.js is not installed"
        Write-Info "Download from: https://nodejs.org/"
        return $false
    }
    
    # Check npm
    try {
        $npmVersion = npm --version 2>$null
        Write-Success "npm found: $npmVersion"
    } catch {
        Write-Error "npm is not available"
        return $false
    }
    
    return $true
}

function Install-Dependencies {
    Write-Info "Installing dependencies..."
    
    Set-Location $DesktopAppDir
    
    if (!(Test-Path "node_modules")) {
        npm install
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to install dependencies"
            return $false
        }
        Write-Success "Dependencies installed"
    } else {
        Write-Info "Dependencies already installed"
    }
    
    return $true
}

function Build-Application {
    param($Platform)
    
    Write-Info "Building application for $Platform..."
    
    Set-Location $DesktopAppDir
    
    switch ($Platform.ToLower()) {
        "windows" { 
            npm run build-windows 
            $expectedFile = "dist\*.exe"
        }
        "linux" { 
            npm run build-linux 
            $expectedFile = "dist\*.AppImage"
        }
        "mac" { 
            npm run build-mac 
            $expectedFile = "dist\*.dmg"
        }
        default { 
            Write-Error "Unsupported platform: $Platform"
            return $false
        }
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Build completed successfully!"
        
        # Show built files
        $distFiles = Get-ChildItem -Path "dist" -File | Where-Object { $_.Name -match '\.(exe|AppImage|dmg)$' }
        if ($distFiles) {
            Write-Info "Built files:"
            $distFiles | ForEach-Object { Write-Host "  - $($_.Name) ($([math]::Round($_.Length/1MB, 2)) MB)" }
        }
        
        return $true
    } else {
        Write-Error "Build failed"
        return $false
    }
}

function Show-PostBuildInstructions {
    param($Platform)
    
    Write-Success "==============================================="
    Write-Success "Build Instructions Complete!"
    Write-Success "==============================================="
    Write-Info ""
    Write-Info "Next steps:"
    Write-Info "1. Distribute the installer to client devices"
    Write-Info "2. On each client device:"
    Write-Info "   - Install the application"
    Write-Info "   - Edit the .env file in the installation directory"
    Write-Info "   - Set SERVER_IP to your server's IP address"
    Write-Info "   - Run the application"
    Write-Info ""
    Write-Info "Installation directory (typical):"
    
    switch ($Platform.ToLower()) {
        "windows" { 
            Write-Info "  C:\Users\[username]\AppData\Local\Programs\Legal Cases Management\"
        }
        "linux" { 
            Write-Info "  /home/[username]/Applications/"
        }
        "mac" { 
            Write-Info "  /Applications/Legal Cases Management.app/"
        }
    }
    
    Write-Info ""
    Write-Info "Example .env file content:"
    Write-Info "  SERVER_IP=192.168.1.100"
    Write-Info "  SERVER_PORT=8000"
    Write-Info ""
}

function Show-Help {
    Write-Host @"
Legal Cases Management System - Desktop Application Builder

USAGE:
    .\build-desktop-app.ps1 [options]

OPTIONS:
    -Platform <platform>    Target platform (windows, linux, mac) [default: windows]
    -Help                   Show this help message

EXAMPLES:
    # Build for Windows
    .\build-desktop-app.ps1 -Platform windows

    # Build for Linux
    .\build-desktop-app.ps1 -Platform linux

    # Build for macOS
    .\build-desktop-app.ps1 -Platform mac

REQUIREMENTS:
    - Node.js 16 or higher
    - Internet connection for dependencies
    - Sufficient disk space for build output

OUTPUT:
    The built application will be in: frontend\desktop-app\dist\

NOTES:
    - First build may take longer due to dependency downloads
    - Cross-platform builds may require additional setup
    - Edit .env file after installation to configure server connection
"@
}

# Main execution
if ($Help) {
    Show-Help
    exit 0
}

Write-Success "Legal Cases Management System - Desktop Application Builder"
Write-Success "============================================================="
Write-Info "Target Platform: $Platform"
Write-Info ""

if (!(Test-Prerequisites)) {
    exit 1
}

if (!(Install-Dependencies)) {
    exit 1
}

if (Build-Application $Platform) {
    Show-PostBuildInstructions $Platform
} else {
    Write-Error "Build process failed"
    exit 1
}
