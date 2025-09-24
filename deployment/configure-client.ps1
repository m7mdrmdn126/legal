# Client Configuration Script for Windows
# This script configures the desktop app to connect to a network server

param(
    [Parameter(Mandatory=$true)]
    [string]$ServerIP,
    [int]$ServerPort = 8000
)

# Script configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir
$DesktopAppDir = Join-Path $ProjectRoot "frontend\desktop-app"
$ApiServiceFile = Join-Path $DesktopAppDir "src\services\api.js"

function Write-Success($message) {
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $message" -ForegroundColor Green
}

function Write-Info($message) {
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $message" -ForegroundColor Cyan
}

function Write-Error($message) {
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] ERROR: $message" -ForegroundColor Red
}

# Validate server IP
function Test-ServerConnection {
    param($ServerIP, $Port)
    
    Write-Info "Testing connection to server..."
    
    try {
        $response = Invoke-WebRequest -Uri "http://${ServerIP}:${Port}/api/v1/info" -TimeoutSec 10 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Success "✓ Server is accessible at http://${ServerIP}:${Port}"
            return $true
        }
    } catch {
        Write-Error "✗ Cannot connect to server at http://${ServerIP}:${Port}"
        Write-Error "Error: $($_.Exception.Message)"
        return $false
    }
}

# Update API service configuration
function Update-ApiConfiguration {
    param($ServerIP, $Port)
    
    Write-Info "Updating API configuration..."
    
    if (!(Test-Path $ApiServiceFile)) {
        Write-Error "API service file not found: $ApiServiceFile"
        return $false
    }
    
    # Read current content
    $content = Get-Content $ApiServiceFile -Raw
    
    # Replace the API base URL
    $oldPattern = "const API_BASE_URL = 'http://localhost:8000/api/v1';"
    $newValue = "const API_BASE_URL = 'http://${ServerIP}:${Port}/api/v1';"
    
    if ($content -match [regex]::Escape($oldPattern)) {
        $content = $content -replace [regex]::Escape($oldPattern), $newValue
        $content | Set-Content $ApiServiceFile -NoNewline
        Write-Success "✓ API configuration updated"
        return $true
    } else {
        Write-Error "Could not find API_BASE_URL pattern in $ApiServiceFile"
        return $false
    }
}

# Create client configuration file
function New-ClientConfigFile {
    param($ServerIP, $Port)
    
    $configDir = Join-Path $DesktopAppDir "config"
    if (!(Test-Path $configDir)) {
        New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    }
    
    $configFile = Join-Path $configDir "server.json"
    
    $config = @{
        server = @{
            ip = $ServerIP
            port = $Port
            url = "http://${ServerIP}:${Port}"
            apiUrl = "http://${ServerIP}:${Port}/api/v1"
        }
        configuredAt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        configuredBy = $env:USERNAME
    }
    
    $config | ConvertTo-Json -Depth 3 | Set-Content $configFile
    Write-Success "✓ Client configuration saved to: $configFile"
}

# Main execution
Write-Success "Legal Cases Management System - Client Configuration"
Write-Success "=================================================="

Write-Info "Configuring client to connect to server: $ServerIP:$ServerPort"

# Test server connection
if (!(Test-ServerConnection $ServerIP $ServerPort)) {
    Write-Error "Cannot proceed with configuration. Please ensure:"
    Write-Error "1. Server is running on $ServerIP"
    Write-Error "2. Port $ServerPort is open"
    Write-Error "3. No firewall is blocking the connection"
    exit 1
}

# Update configuration
if (Update-ApiConfiguration $ServerIP $ServerPort) {
    New-ClientConfigFile $ServerIP $ServerPort
    
    Write-Success "=================================================="
    Write-Success "Client configuration completed successfully!"
    Write-Success "=================================================="
    Write-Info "The desktop app is now configured to connect to:"
    Write-Info "  Server: http://${ServerIP}:${ServerPort}"
    Write-Info ""
    Write-Info "To start the desktop app:"
    Write-Info "  1. Navigate to: $DesktopAppDir"
    Write-Info "  2. Run: npm install (first time only)"
    Write-Info "  3. Run: npm run electron-dev"
} else {
    Write-Error "Configuration failed. Please check the file manually."
    exit 1
}
