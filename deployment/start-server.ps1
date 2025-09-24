# Legal Cases Management System - Windows Server Startup Script
# Run this script as Administrator

param(
    [switch]$Setup,
    [switch]$Start,
    [switch]$Help
)

# Script configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir
$BackendDir = Join-Path $ProjectRoot "backend"
$DatabaseDir = Join-Path $ProjectRoot "database"
$ServerDataDir = "C:\legal-cases"

# Color functions
function Write-Success($message) {
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $message" -ForegroundColor Green
}

function Write-Warning($message) {
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] WARNING: $message" -ForegroundColor Yellow
}

function Write-Error($message) {
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] ERROR: $message" -ForegroundColor Red
}

function Write-Info($message) {
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $message" -ForegroundColor Cyan
}

# Check if running as Administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Create necessary directories
function New-ServerDirectories {
    Write-Info "Creating necessary directories..."
    
    $directories = @(
        "$ServerDataDir\database",
        "$ServerDataDir\logs", 
        "$ServerDataDir\backups"
    )
    
    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Success "Created directory: $dir"
        }
    }
}

# Check dependencies
function Test-Dependencies {
    Write-Info "Checking dependencies..."
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Success "Python found: $pythonVersion"
    } catch {
        Write-Error "Python is not installed or not in PATH"
        Write-Info "Please install Python 3.9+ from https://www.python.org/downloads/windows/"
        exit 1
    }
    
    # Check pip
    try {
        $pipVersion = pip --version 2>&1
        Write-Success "Pip found: $pipVersion"
    } catch {
        Write-Error "Pip is not available"
        exit 1
    }
}

# Install Python packages
function Install-Packages {
    Write-Info "Installing Python packages..."
    
    Set-Location $BackendDir
    
    # Create virtual environment if it doesn't exist
    if (!(Test-Path "venv")) {
        python -m venv venv
        Write-Success "Created virtual environment"
    }
    
    # Activate virtual environment and install packages
    & ".\venv\Scripts\Activate.ps1"
    
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    
    Write-Success "Python packages installed"
}

# Setup database
function Initialize-Database {
    Write-Info "Setting up database..."
    
    Set-Location $BackendDir
    & ".\venv\Scripts\Activate.ps1"
    
    # Copy database to production location if needed
    $prodDb = "$ServerDataDir\database\legal_cases.db"
    $sourceDb = "$DatabaseDir\legal_cases.db"
    
    if ((Test-Path $sourceDb) -and !(Test-Path $prodDb)) {
        Copy-Item $sourceDb $prodDb
        Write-Success "Database copied to production location"
    } elseif (!(Test-Path $prodDb)) {
        # Create initial database
        python -c "
import sys
sys.path.insert(0, '.')
from config.database import init_db
init_db()
"
        Write-Success "Initial database created"
    }
    
    Write-Success "Database setup complete"
}

# Get network configuration
function Get-NetworkInfo {
    Write-Info "Network configuration:"
    
    # Get primary network adapter IP
    $networkAdapter = Get-NetAdapter | Where-Object {$_.Status -eq "Up" -and $_.Virtual -eq $false} | Select-Object -First 1
    $ipAddress = Get-NetIPAddress -InterfaceIndex $networkAdapter.InterfaceIndex -AddressFamily IPv4 | Where-Object {$_.PrefixOrigin -eq "Manual" -or $_.PrefixOrigin -eq "Dhcp"} | Select-Object -First 1
    
    $serverIP = $ipAddress.IPAddress
    
    Write-Host "  Network Adapter: $($networkAdapter.Name)"
    Write-Host "  Server IP: $serverIP"
    Write-Host "  Server will be accessible at: http://${serverIP}:8000"
    Write-Host ""
    
    # Save server IP to file for client configuration
    $serverIP | Out-File "$ServerDataDir\server-ip.txt" -Encoding UTF8
    Write-Success "Server IP saved to $ServerDataDir\server-ip.txt"
    
    return $serverIP
}

# Load environment variables from file
function Import-EnvironmentFile($filePath) {
    if (Test-Path $filePath) {
        Get-Content $filePath | ForEach-Object {
            if ($_ -match '^([^=]+)=(.*)$') {
                [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
            }
        }
        Write-Success "Loaded environment variables from $filePath"
    }
}

# Start the server
function Start-Server {
    Write-Info "Starting Legal Cases Management Server..."
    
    Set-Location $BackendDir
    & ".\venv\Scripts\Activate.ps1"
    
    # Load production environment
    $envFile = "$ProjectRoot\deployment\.env.production.windows"
    Import-EnvironmentFile $envFile
    
    $host = [Environment]::GetEnvironmentVariable("HOST") ?? "0.0.0.0"
    $port = [Environment]::GetEnvironmentVariable("PORT") ?? "8000"
    
    Write-Success "Server starting on ${host}:${port}..."
    Write-Info "Press Ctrl+C to stop the server"
    Write-Host ""
    
    # Start server with uvicorn
    python -m uvicorn main:app --host $host --port $port --reload --log-level info
}

# Setup function
function Invoke-Setup {
    if (!(Test-Administrator)) {
        Write-Error "This script must be run as Administrator for initial setup"
        Write-Info "Right-click PowerShell and select 'Run as Administrator'"
        exit 1
    }
    
    Write-Success "Legal Cases Management System - Windows Server Setup"
    Write-Success "======================================================"
    
    New-ServerDirectories
    Test-Dependencies
    Install-Packages
    Initialize-Database
    $serverIP = Get-NetworkInfo
    
    Write-Success "Server setup complete!"
    Write-Success "======================================================"
    Write-Info "Next steps:"
    Write-Info "1. Configure client devices to connect to: http://${serverIP}:8000"
    Write-Info "2. Run: .\start-server.ps1 -Start (to start the server)"
    Write-Info "3. Or run: .\start-server.bat (simple batch file)"
}

# Start function
function Invoke-Start {
    Write-Success "Legal Cases Management System - Server Start"
    Write-Success "============================================"
    
    if (!(Test-Path $BackendDir)) {
        Write-Error "Backend directory not found. Please run setup first: .\start-server.ps1 -Setup"
        exit 1
    }
    
    Start-Server
}

# Help function
function Show-Help {
    Write-Host @"
Legal Cases Management System - Windows Server Script

USAGE:
    .\start-server.ps1 -Setup    # Initial setup (run as Administrator)
    .\start-server.ps1 -Start    # Start the server
    .\start-server.ps1 -Help     # Show this help

EXAMPLES:
    # First time setup (run as Administrator)
    .\start-server.ps1 -Setup

    # Start server (can be run as regular user)
    .\start-server.ps1 -Start

REQUIREMENTS:
    - Windows 10/11 or Windows Server
    - Python 3.9 or higher installed
    - Network connectivity between server and client devices

NOTES:
    - Setup must be run as Administrator
    - Server can be started as regular user after setup
    - Default server port is 8000
    - Firewall rules will be configured during setup
"@
}

# Main execution logic
if ($Setup) {
    Invoke-Setup
} elseif ($Start) {
    Invoke-Start
} elseif ($Help) {
    Show-Help
} else {
    Write-Info "Legal Cases Management System - Windows Server"
    Write-Info "Use -Help for usage information"
    Write-Info "Quick start: .\start-server.ps1 -Setup (first time, as Admin)"
    Write-Info "             .\start-server.ps1 -Start (to start server)"
}
