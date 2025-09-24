# Legal Cases Management System - Windows Service Installer
# This script installs the server as a Windows Service using NSSM

param(
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$Start,
    [switch]$Stop,
    [switch]$Status,
    [switch]$Help
)

# Configuration
$ServiceName = "LegalCasesServer"
$ServiceDisplayName = "Legal Cases Management Server"
$ServiceDescription = "Legal Cases Management System API Server"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir
$BackendDir = Join-Path $ProjectRoot "backend"
$NssmPath = Join-Path $ScriptDir "nssm.exe"

function Write-Success($message) {
    Write-Host "[SUCCESS] $message" -ForegroundColor Green
}

function Write-Error($message) {
    Write-Host "[ERROR] $message" -ForegroundColor Red
}

function Write-Info($message) {
    Write-Host "[INFO] $message" -ForegroundColor Cyan
}

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-ServiceExists {
    $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    return $null -ne $service
}

function Install-NSSM {
    if (!(Test-Path $NssmPath)) {
        Write-Info "Downloading NSSM (Non-Sucking Service Manager)..."
        
        $nssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
        $tempZip = Join-Path $env:TEMP "nssm.zip"
        $tempDir = Join-Path $env:TEMP "nssm"
        
        try {
            Invoke-WebRequest -Uri $nssmUrl -OutFile $tempZip
            Expand-Archive -Path $tempZip -DestinationPath $tempDir -Force
            
            # Copy appropriate NSSM executable
            $nssmExe = if ([Environment]::Is64BitOperatingSystem) {
                Join-Path $tempDir "nssm-2.24\win64\nssm.exe"
            } else {
                Join-Path $tempDir "nssm-2.24\win32\nssm.exe"
            }
            
            Copy-Item $nssmExe $NssmPath
            Write-Success "NSSM downloaded and installed"
            
            # Cleanup
            Remove-Item $tempZip -Force
            Remove-Item $tempDir -Recurse -Force
        } catch {
            Write-Error "Failed to download NSSM: $($_.Exception.Message)"
            return $false
        }
    }
    return $true
}

function Install-Service {
    if (!(Test-Administrator)) {
        Write-Error "Administrator privileges required for service installation"
        return $false
    }
    
    if (Test-ServiceExists) {
        Write-Error "Service '$ServiceName' already exists. Uninstall first."
        return $false
    }
    
    if (!(Install-NSSM)) {
        return $false
    }
    
    Write-Info "Installing Legal Cases Management Server as Windows Service..."
    
    # Prepare paths
    $pythonExe = Join-Path $BackendDir "venv\Scripts\python.exe"
    $uvicornModule = "uvicorn"
    $appModule = "main:app"
    $workingDir = $BackendDir
    
    # Install service
    & $NssmPath install $ServiceName $pythonExe "-m" $uvicornModule $appModule "--host" "0.0.0.0" "--port" "8000"
    
    if ($LASTEXITCODE -eq 0) {
        # Configure service
        & $NssmPath set $ServiceName DisplayName $ServiceDisplayName
        & $NssmPath set $ServiceName Description $ServiceDescription
        & $NssmPath set $ServiceName AppDirectory $workingDir
        & $NssmPath set $ServiceName Start SERVICE_AUTO_START
        
        # Set environment variables
        $envFile = Join-Path $ProjectRoot "deployment\.env.production.windows"
        if (Test-Path $envFile) {
            $envVars = @()
            Get-Content $envFile | ForEach-Object {
                if ($_ -match '^([^=]+)=(.*)$') {
                    $envVars += "$($matches[1])=$($matches[2])"
                }
            }
            if ($envVars.Count -gt 0) {
                & $NssmPath set $ServiceName AppEnvironmentExtra ($envVars -join "`0")
            }
        }
        
        Write-Success "Service '$ServiceName' installed successfully"
        Write-Info "Use 'services.msc' to manage the service or use this script with -Start"
        return $true
    } else {
        Write-Error "Failed to install service"
        return $false
    }
}

function Uninstall-Service {
    if (!(Test-Administrator)) {
        Write-Error "Administrator privileges required for service uninstallation"
        return $false
    }
    
    if (!(Test-ServiceExists)) {
        Write-Error "Service '$ServiceName' does not exist"
        return $false
    }
    
    Write-Info "Stopping and uninstalling service..."
    
    # Stop service if running
    Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
    
    # Remove service
    & $NssmPath remove $ServiceName confirm
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Service '$ServiceName' uninstalled successfully"
        return $true
    } else {
        Write-Error "Failed to uninstall service"
        return $false
    }
}

function Start-LegalCasesService {
    if (!(Test-ServiceExists)) {
        Write-Error "Service '$ServiceName' is not installed"
        return $false
    }
    
    Write-Info "Starting Legal Cases Management Server..."
    Start-Service -Name $ServiceName
    
    if ((Get-Service -Name $ServiceName).Status -eq 'Running') {
        Write-Success "Service started successfully"
        return $true
    } else {
        Write-Error "Failed to start service"
        return $false
    }
}

function Stop-LegalCasesService {
    if (!(Test-ServiceExists)) {
        Write-Error "Service '$ServiceName' is not installed"
        return $false
    }
    
    Write-Info "Stopping Legal Cases Management Server..."
    Stop-Service -Name $ServiceName -Force
    
    if ((Get-Service -Name $ServiceName).Status -eq 'Stopped') {
        Write-Success "Service stopped successfully"
        return $true
    } else {
        Write-Error "Failed to stop service"
        return $false
    }
}

function Get-ServiceStatus {
    if (Test-ServiceExists) {
        $service = Get-Service -Name $ServiceName
        Write-Info "Service Status: $($service.Status)"
        Write-Info "Service Name: $($service.Name)"
        Write-Info "Display Name: $($service.DisplayName)"
        
        if ($service.Status -eq 'Running') {
            Write-Success "Legal Cases Management Server is running"
        } else {
            Write-Info "Legal Cases Management Server is not running"
        }
    } else {
        Write-Info "Service '$ServiceName' is not installed"
    }
}

function Show-Help {
    Write-Host @"
Legal Cases Management System - Windows Service Manager

USAGE:
    .\service-manager.ps1 -Install     # Install as Windows Service (requires Admin)
    .\service-manager.ps1 -Uninstall   # Uninstall Windows Service (requires Admin)
    .\service-manager.ps1 -Start       # Start the service
    .\service-manager.ps1 -Stop        # Stop the service
    .\service-manager.ps1 -Status      # Show service status
    .\service-manager.ps1 -Help        # Show this help

EXAMPLES:
    # Install service (run as Administrator)
    .\service-manager.ps1 -Install

    # Start service
    .\service-manager.ps1 -Start

    # Check status
    .\service-manager.ps1 -Status

    # Stop service
    .\service-manager.ps1 -Stop

NOTES:
    - Installation and uninstallation require Administrator privileges
    - The service will automatically start with Windows after installation
    - Use Windows Services Manager (services.msc) for additional configuration
    - Service logs can be found in Windows Event Viewer

REQUIREMENTS:
    - Windows 10/11 or Windows Server
    - Legal Cases Management System already set up
    - Administrator privileges for install/uninstall operations
"@
}

# Main execution
if ($Install) {
    Install-Service
} elseif ($Uninstall) {
    Uninstall-Service
} elseif ($Start) {
    Start-LegalCasesService
} elseif ($Stop) {
    Stop-LegalCasesService
} elseif ($Status) {
    Get-ServiceStatus
} elseif ($Help) {
    Show-Help
} else {
    Write-Info "Legal Cases Management System - Service Manager"
    Write-Info "Use -Help for usage information"
    Write-Info ""
    Get-ServiceStatus
}
