# Legal Cases Management System - Desktop Application Configuration Guide

## 📱 Desktop Application Setup

### Overview
The desktop application is now compiled as a standalone executable that users can install and run like any other desktop application. No need for development environments or command-line tools.

---

## 🏗️ Building the Desktop Application

### Prerequisites
- **Node.js 16+**: Download from [nodejs.org](https://nodejs.org/)
- **Git** (optional): For version control

### Build Process

#### Method 1: Simple Batch File (Windows)
```cmd
cd deployment
build-desktop-app.bat
```

#### Method 2: PowerShell Script (Advanced)
```powershell
# Build for Windows
.\build-desktop-app.ps1 -Platform windows

# Build for Linux
.\build-desktop-app.ps1 -Platform linux

# Build for macOS  
.\build-desktop-app.ps1 -Platform mac
```

### Build Output
After successful build, you'll find the installer in:
```
frontend/desktop-app/dist/
├── Legal Cases Management Setup.exe    # Windows installer
├── Legal Cases Management.AppImage     # Linux AppImage
└── Legal Cases Management.dmg          # macOS installer
```

---

## 📦 Distribution and Installation

### 1. Distribute the Installer
- Copy the appropriate installer file to each client device
- **Windows**: `Legal Cases Management Setup.exe`
- **Linux**: `Legal Cases Management.AppImage`
- **macOS**: `Legal Cases Management.dmg`

### 2. Install on Client Devices

#### Windows Installation
1. Double-click `Legal Cases Management Setup.exe`
2. Follow installation wizard
3. Choose installation directory (or use default)
4. Application will be installed with desktop shortcut

#### Linux Installation
1. Make AppImage executable: `chmod +x Legal\ Cases\ Management.AppImage`
2. Run: `./Legal\ Cases\ Management.AppImage`
3. Or integrate with system using AppImageLauncher

#### macOS Installation
1. Double-click `Legal Cases Management.dmg`
2. Drag application to Applications folder
3. Run from Applications or Launchpad

---

## ⚙️ Client Configuration

### Configuration File Location
After installation, find the `.env` file in:

#### Windows:
```
C:\Users\[username]\AppData\Local\Programs\Legal Cases Management\.env
```

#### Linux:
```
~/.config/Legal Cases Management/.env
```

#### macOS:
```
~/Library/Application Support/Legal Cases Management/.env
```

### Configuration Template
Edit the `.env` file with your server details:

```bash
# Legal Cases Management System - Client Configuration
# Edit this file to configure the server connection

# Server Configuration
# Replace with your server's IP address
SERVER_IP=192.168.1.100
SERVER_PORT=8000

# Application Settings
APP_NAME=Legal Cases Management
APP_VERSION=1.0.0

# Auto-connect settings
AUTO_CONNECT=true
SHOW_SERVER_CONFIG=true
```

### Quick Configuration Script
For Windows clients, create this batch file to quickly configure multiple devices:

**configure-app.bat:**
```batch
@echo off
set /p SERVER_IP="Enter server IP address: "

set CONFIG_FILE="%LOCALAPPDATA%\Programs\Legal Cases Management\.env"

echo # Legal Cases Management System - Client Configuration > %CONFIG_FILE%
echo SERVER_IP=%SERVER_IP% >> %CONFIG_FILE%
echo SERVER_PORT=8000 >> %CONFIG_FILE%
echo APP_NAME=Legal Cases Management >> %CONFIG_FILE%
echo AUTO_CONNECT=true >> %CONFIG_FILE%

echo Configuration updated successfully!
echo Server IP set to: %SERVER_IP%
pause
```

---

## 🚀 Usage Instructions for End Users

### Installation Steps:
1. **Install** the application using the provided installer
2. **Locate** the `.env` configuration file
3. **Edit** the SERVER_IP to match your server's IP address
4. **Save** the configuration file
5. **Launch** the application from desktop shortcut or start menu

### First Time Setup:
1. Double-click the desktop icon "Legal Cases Management"
2. If connection fails, check the server IP in configuration
3. Login with your credentials (default: admin/admin123)
4. Change password on first login

### Troubleshooting:
- **Cannot connect**: Verify server IP in .env file
- **Application won't start**: Check if server is running
- **Login fails**: Verify server is accessible from client device

---

## 🔧 Advanced Configuration Options

### Environment Variables
```bash
# Server Configuration
SERVER_IP=192.168.1.100          # Server IP address
SERVER_PORT=8000                 # Server port (usually 8000)

# Application Behavior
AUTO_CONNECT=true                # Auto-connect on startup
SHOW_SERVER_CONFIG=true          # Show server config in UI
APP_NAME=Legal Cases Management  # Application display name

# Performance Settings
CACHE_ENABLED=true               # Enable local caching
TIMEOUT_SECONDS=30               # Request timeout
RETRY_ATTEMPTS=3                 # Connection retry attempts

# UI Settings
THEME=auto                       # UI theme (light/dark/auto)
LANGUAGE=ar                      # Interface language
```

### Multiple Server Support
For environments with multiple servers, you can create different configuration files:

**Production server (.env.prod):**
```bash
SERVER_IP=192.168.1.100
SERVER_PORT=8000
```

**Test server (.env.test):**
```bash
SERVER_IP=192.168.1.200
SERVER_PORT=8000
```

---

## 📋 Deployment Checklist

### Build Phase:
- [ ] Install Node.js on build machine
- [ ] Clone/copy project files
- [ ] Run build script for target platform
- [ ] Test built application locally
- [ ] Prepare distribution files

### Distribution Phase:
- [ ] Copy installer to client devices
- [ ] Install application on each device
- [ ] Configure server IP in .env file
- [ ] Test connection to server
- [ ] Create desktop shortcuts if needed

### User Training:
- [ ] Provide login credentials
- [ ] Show how to access configuration file
- [ ] Demonstrate basic application usage
- [ ] Provide troubleshooting contact information

---

## 🔒 Security Considerations

### Client Security:
- Configuration file contains server connection details
- No sensitive data stored locally by default
- Application validates server certificates
- Automatic logout after inactivity

### Network Security:
- All communication encrypted via HTTPS (if configured)
- Server IP should be on trusted network
- Consider VPN for remote access
- Regular security updates recommended

### Access Control:
- Each user requires valid credentials
- Session tokens expire automatically
- Failed login attempts are logged
- Administrative functions require admin privileges
