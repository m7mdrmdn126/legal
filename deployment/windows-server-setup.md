# Legal Cases Management System - Windows Server Setup Guide

## Prerequisites

### 1. Install Python
- Download Python 3.9+ from https://www.python.org/downloads/windows/
- During installation, check "Add Python to PATH"
- Verify installation: Open Command Prompt and run `python --version`

### 2. Install Git (Optional)
- Download from https://git-scm.com/download/win
- Use default settings during installation

### 3. Network Configuration

#### Find Server IP Address
```powershell
# Open PowerShell as Administrator and run:
ipconfig
# Look for "IPv4 Address" in your active network adapter
# Example: 192.168.1.100
```

#### Configure Static IP (Recommended)
1. Open "Network and Sharing Center"
2. Click "Change adapter settings"
3. Right-click your network adapter → Properties
4. Select "Internet Protocol Version 4 (TCP/IPv4)" → Properties
5. Choose "Use the following IP address":
   - IP address: 192.168.1.100 (choose available IP in your network)
   - Subnet mask: 255.255.255.0
   - Default gateway: 192.168.1.1 (your router's IP)
   - DNS servers: 8.8.8.8, 8.8.4.4

### 4. Windows Firewall Configuration

#### Option 1: Using Windows Firewall GUI
1. Open "Windows Defender Firewall with Advanced Security"
2. Click "Inbound Rules" → "New Rule"
3. Choose "Port" → "TCP" → Specific local ports: 8000
4. Allow the connection
5. Apply to all profiles
6. Name: "Legal Cases API Server"

#### Option 2: Using PowerShell (Run as Administrator)
```powershell
# Allow inbound connections on port 8000
New-NetFirewallRule -DisplayName "Legal Cases API Server" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow

# Verify the rule was created
Get-NetFirewallRule -DisplayName "Legal Cases API Server"
```

## Directory Structure
The server will create these directories:
- `C:\legal-cases\database\` - Database files
- `C:\legal-cases\logs\` - Log files  
- `C:\legal-cases\backups\` - Backup files
