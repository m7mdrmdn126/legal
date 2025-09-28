# Legal Cases Management System - Windows Network Setup PowerShell Script
# Run as Administrator

param(
    [switch]$Force,
    [int]$Port = 8000
)

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as administrator'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Legal Cases Management System" -ForegroundColor Green
Write-Host "Windows Network Configuration" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host

# Function to test port connectivity
function Test-Port {
    param($ComputerName, $Port)
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $tcpClient.Connect($ComputerName, $Port)
        $tcpClient.Close()
        return $true
    }
    catch {
        return $false
    }
}

# Function to get local IP addresses
function Get-LocalIPs {
    $ips = @()
    $adapters = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { 
        $_.IPAddress -ne '127.0.0.1' -and 
        $_.PrefixOrigin -eq 'Dhcp' -or $_.PrefixOrigin -eq 'Manual' 
    }
    
    foreach ($adapter in $adapters) {
        $ips += $adapter.IPAddress
    }
    return $ips
}

Write-Host "[1/7] Configuring Windows Firewall..." -ForegroundColor Yellow

# Remove existing rules if they exist
try {
    Remove-NetFirewallRule -DisplayName "Legal Cases API*" -ErrorAction SilentlyContinue
    Write-Host "    Removed existing firewall rules" -ForegroundColor Gray
} catch {
    # Rules don't exist, that's fine
}

# Add new firewall rules
try {
    New-NetFirewallRule -DisplayName "Legal Cases API - Inbound" -Direction Inbound -Protocol TCP -LocalPort $Port -Action Allow | Out-Null
    New-NetFirewallRule -DisplayName "Legal Cases API - Outbound" -Direction Outbound -Protocol TCP -LocalPort $Port -Action Allow | Out-Null
    Write-Host "    ✓ Firewall rules configured for port $Port" -ForegroundColor Green
} catch {
    Write-Host "    ✗ Failed to configure firewall rules: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "[2/7] Getting network information..." -ForegroundColor Yellow

$localIPs = Get-LocalIPs
Write-Host "    Local IP addresses found:" -ForegroundColor Gray
foreach ($ip in $localIPs) {
    Write-Host "      $ip" -ForegroundColor White
}

Write-Host "[3/7] Checking port availability..." -ForegroundColor Yellow

$portInUse = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "    ✓ Port $Port is in use (PID: $($portInUse.OwningProcess))" -ForegroundColor Green
    $process = Get-Process -Id $portInUse.OwningProcess -ErrorAction SilentlyContinue
    if ($process) {
        Write-Host "      Process: $($process.ProcessName)" -ForegroundColor Gray
    }
} else {
    Write-Host "    ⚠ Port $Port is not in use (server may not be running)" -ForegroundColor Yellow
}

Write-Host "[4/7] Testing local server connectivity..." -ForegroundColor Yellow

$localServerRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:$Port" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "    ✓ Local server responding: HTTP $($response.StatusCode)" -ForegroundColor Green
    $localServerRunning = $true
} catch {
    Write-Host "    ✗ Local server not responding: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "[5/7] Testing API endpoints..." -ForegroundColor Yellow

if ($localServerRunning) {
    $endpoints = @("/", "/api/v1/info")
    foreach ($endpoint in $endpoints) {
        try {
            $response = Invoke-WebRequest -Uri "http://127.0.0.1:$Port$endpoint" -TimeoutSec 5 -ErrorAction Stop
            Write-Host "    ✓ $endpoint - HTTP $($response.StatusCode)" -ForegroundColor Green
        } catch {
            Write-Host "    ✗ $endpoint - Error: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

Write-Host "[6/7] Creating helper scripts..." -ForegroundColor Yellow

# Create server startup script
$startScript = @"
@echo off
title Legal Cases Management System Server
echo ========================================
echo Legal Cases Management System Server
echo ========================================
echo.

cd /d "%~dp0backend"

echo Server will be available at:
"@ + $(foreach ($ip in $localIPs) { "echo   http://$ip`:$Port`n" }) + @"

echo.
echo Starting server...
echo Press Ctrl+C to stop the server
echo.

python main.py

echo.
echo Server stopped.
pause
"@

$startScript | Out-File -FilePath "start-legal-cases-server.bat" -Encoding ASCII
Write-Host "    ✓ Created start-legal-cases-server.bat" -ForegroundColor Green

# Create client configuration helper
$configScript = @"
@echo off
title Legal Cases - Server URLs
echo ========================================
echo Legal Cases Management System
echo Client Configuration Helper
echo ========================================
echo.
echo Configure your client applications with these URLs:
echo.
"@ + $(foreach ($ip in $localIPs) { "echo   Server: http://$ip`:$Port`necho   API:    http://$ip`:$Port/api/v1`necho.`n" }) + @"
echo ========================================
echo.
echo Copy one of the 'Server' URLs above and paste it into your
echo desktop application's server configuration.
echo.
pause
"@

$configScript | Out-File -FilePath "get-server-urls.bat" -Encoding ASCII
Write-Host "    ✓ Created get-server-urls.bat" -ForegroundColor Green

Write-Host "[7/7] Network diagnostic complete!" -ForegroundColor Yellow

Write-Host
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configuration Summary" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "✓ Windows Firewall configured" -ForegroundColor Green
Write-Host "✓ Helper scripts created" -ForegroundColor Green
Write-Host "✓ Network diagnostic completed" -ForegroundColor Green

Write-Host
Write-Host "Network Configuration:" -ForegroundColor White
Write-Host "  Port: $Port" -ForegroundColor Gray
Write-Host "  Server Status: $(if($localServerRunning) { 'Running' } else { 'Not Running' })" -ForegroundColor Gray
Write-Host "  IP Addresses:" -ForegroundColor Gray
foreach ($ip in $localIPs) {
    Write-Host "    http://$ip`:$Port" -ForegroundColor White
}

Write-Host
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Start the server: .\start-legal-cases-server.bat" -ForegroundColor White
Write-Host "2. Get server URLs: .\get-server-urls.bat" -ForegroundColor White
Write-Host "3. Configure clients with the server URLs" -ForegroundColor White

Write-Host
Write-Host "Troubleshooting:" -ForegroundColor Yellow
if (-not $localServerRunning) {
    Write-Host "• Server is not running - start it first!" -ForegroundColor Red
}
Write-Host "• If clients can't connect, try disabling Windows Defender Firewall temporarily" -ForegroundColor White
Write-Host "• Ensure all devices are on the same network/subnet" -ForegroundColor White
Write-Host "• Check antivirus software settings" -ForegroundColor White
Write-Host "• Test from client: telnet <server_ip> $Port" -ForegroundColor White

Write-Host
Write-Host "========================================" -ForegroundColor Cyan

Read-Host "Press Enter to exit"
