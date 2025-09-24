# Legal Cases Management System - Network Deployment

This guide provides complete instructions for deploying the Legal Cases Management System in a networked environment where multiple client devices connect to a centralized server.

## 📋 Deployment Overview

### Architecture
- **Server Device**: Runs the FastAPI backend and SQLite database
- **Client Devices**: Run the Electron desktop application
- **Network**: All devices connected via switch/router on same LAN

### Supported Platforms
- **Server**: Windows 10/11, Windows Server, Ubuntu/Debian Linux
- **Clients**: Windows 10/11, macOS, Linux

---

## 🖥️ SERVER SETUP

### Windows Server Setup

#### Quick Start (Recommended for most users)
1. **Copy** the application folder to your server device
2. **Right-click** Command Prompt → "Run as Administrator"
3. **Navigate** to the deployment folder:
   ```cmd
   cd C:\path\to\legal-cases-app\deployment
   ```
4. **Run setup**:
   ```cmd
   setup-server.bat
   ```
5. **Start server**:
   ```cmd
   start-server.bat
   ```

#### Advanced Setup (PowerShell with more features)
```powershell
# Run PowerShell as Administrator
.\start-server.ps1 -Setup    # Initial setup
.\start-server.ps1 -Start    # Start server
```

#### Windows Service Installation (For automatic startup)
```powershell
# Install as Windows Service
.\service-manager.ps1 -Install

# Start service
.\service-manager.ps1 -Start
```

### Linux Server Setup

#### Ubuntu/Debian
```bash
# Make script executable
chmod +x deployment/start-server.sh

# Run setup and start server
./deployment/start-server.sh
```

### Verify Server Installation
1. Open web browser on server
2. Navigate to: `http://localhost:8000/docs`
3. You should see the FastAPI documentation interface

---

## 💻 CLIENT SETUP

### Prerequisites (All Client Devices)
- **Node.js 16+**: Download from [nodejs.org](https://nodejs.org/)

### Windows Client Configuration

#### Method 1: Simple Batch Script
```cmd
cd C:\path\to\legal-cases-app\deployment
configure-client.bat [SERVER_IP]

# Example:
configure-client.bat 192.168.1.100
```

#### Method 2: PowerShell Script
```powershell
.\configure-client.ps1 -ServerIP 192.168.1.100 -ServerPort 8000
```

### Install and Run Desktop App
```cmd
# Navigate to desktop app directory
cd frontend\desktop-app

# Install dependencies (first time only)
npm install

# Start application
npm run electron-dev
```

---

## 🔧 CONFIGURATION FILES

### Server Configuration

#### Environment Files
- **Windows**: `deployment\.env.production.windows`
- **Linux**: `deployment\.env.production`

#### Key Settings
```bash
# Network settings
HOST=0.0.0.0              # Listen on all interfaces
PORT=8000                  # Server port

# CORS settings (add your client IPs)
CORS_ORIGINS=http://192.168.1.101:*,http://192.168.1.102:*

# Database location
DATABASE_PATH=C:\legal-cases\database\legal_cases.db
```

### Client Configuration

The client configuration is automatically updated by the configuration scripts. The main file modified is:
- `frontend/desktop-app/src/services/api.js`

---

## 📁 DIRECTORY STRUCTURE

### Server Directories (Created automatically)
```
Windows:
C:\legal-cases\
├── database\      # Database files
├── logs\         # Server logs
└── backups\      # Database backups

Linux:
/opt/legal-cases/
├── database\
├── logs\
└── backups\
```

### Application Structure
```
legal-cases-app\
├── backend\              # Server code
│   ├── main.py
│   ├── requirements.txt
│   └── venv\            # Python virtual environment
├── frontend\
│   └── desktop-app\     # Electron application
├── database\            # Database files
└── deployment\          # Setup scripts
    ├── start-server.bat        # Windows server (simple)
    ├── start-server.ps1        # Windows server (advanced)
    ├── setup-server.bat        # Windows setup (simple)
    ├── configure-client.bat    # Windows client config
    ├── configure-client.ps1    # Windows client config (advanced)
    ├── service-manager.ps1     # Windows service manager
    └── start-server.sh         # Linux server script
```

---

## 🌐 NETWORK CONFIGURATION

### Server Network Setup

1. **Assign Static IP** (Recommended)
   - Choose an available IP in your network range
   - Example: `192.168.1.100`

2. **Configure Firewall**
   - Allow inbound connections on port 8000
   - Scripts handle this automatically on Windows

3. **Test Connectivity**
   ```cmd
   # From any client device
   telnet [SERVER_IP] 8000
   
   # Or use web browser
   http://[SERVER_IP]:8000/docs
   ```

### Client Network Requirements
- Must be on same LAN as server
- No special firewall configuration needed
- Outbound connections to server port 8000

---

## 🚀 QUICK DEPLOYMENT CHECKLIST

### Server Device:
- [ ] Install Python 3.9+ (Windows) or ensure it's available (Linux)
- [ ] Set static IP address (recommended)
- [ ] Copy application files to server
- [ ] Run server setup script as Administrator/root
- [ ] Start server
- [ ] Verify server accessibility at `http://[SERVER_IP]:8000/docs`
- [ ] Note server IP address for client configuration

### Each Client Device:
- [ ] Install Node.js 16+
- [ ] Copy application files
- [ ] Run client configuration script with server IP
- [ ] Install desktop app dependencies (`npm install`)
- [ ] Start desktop application (`npm run electron-dev`)

---

## 🔍 TROUBLESHOOTING

### Server Issues

**Cannot start server**
- Verify Python is installed and in PATH
- Ensure port 8000 is not in use: `netstat -an | findstr :8000` (Windows) or `netstat -an | grep :8000` (Linux)
- Check firewall settings

**Clients cannot connect**
- Verify server IP address
- Test connectivity: `telnet [SERVER_IP] 8000`
- Check firewall rules on server
- Ensure both devices are on same network

### Client Issues

**Desktop app won't start**
- Verify Node.js is installed: `node --version`
- Run `npm install` in desktop-app directory
- Check for error messages in terminal

**"Cannot connect to server" error**
- Verify server is running
- Check server IP configuration in client
- Test server accessibility in web browser

### Common Network Issues

**Different subnets**
- Ensure server and clients are on same network segment
- Check router/switch configuration

**Corporate networks**
- May require IT department assistance for firewall rules
- Consider using VPN for remote access

---

## 🔒 SECURITY CONSIDERATIONS

### Default Credentials
- **Username**: `admin`
- **Password**: `admin123`
- **⚠️ Change immediately** after first login

### Network Security
- Deploy only on trusted networks
- Consider VPN for remote access
- Regular database backups are essential

### Firewall Configuration
- Server: Allow inbound on port 8000 from local network only
- Clients: No special configuration needed

---

## 📞 GETTING HELP

### Log Files
- **Windows Server**: `C:\legal-cases\logs\app.log`
- **Linux Server**: `/opt/legal-cases/logs/app.log`
- **Windows Event Viewer**: Look for service-related events

### Common Commands

**Check server status:**
```bash
# Linux
sudo systemctl status legal-cases  # if installed as service
ps aux | grep uvicorn              # if running manually

# Windows
sc query LegalCasesServer         # if installed as service
tasklist | findstr python         # if running manually
```

**View server logs:**
```bash
# Linux
tail -f /opt/legal-cases/logs/app.log

# Windows
type C:\legal-cases\logs\app.log
```

### Support Checklist
1. Verify all prerequisites are installed
2. Check network connectivity between devices
3. Review log files for error messages
4. Test server accessibility via web browser
5. Confirm firewall settings

---

## 📈 PERFORMANCE OPTIMIZATION

### Server Performance
- Use SSD storage for database files
- Ensure adequate RAM (minimum 4GB recommended)
- Consider database optimization for large datasets

### Network Performance
- Use wired connections when possible
- Ensure adequate network bandwidth
- Monitor network latency between devices

### Client Performance
- Keep desktop applications updated
- Monitor system resources during usage
- Consider hardware requirements for multiple concurrent users
