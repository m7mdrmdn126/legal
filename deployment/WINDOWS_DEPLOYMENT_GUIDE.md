# Legal Cases Management System - Complete Windows Network Deployment Guide

## Overview
This guide will help you deploy the Legal Cases Management System on a Windows network where:
- **Server Device**: Runs the backend API and database
- **Client Devices**: Run the desktop application connecting to the server

---

## 🖥️ SERVER DEVICE SETUP

### Step 1: Prerequisites
1. **Install Python 3.9+**
   - Download from: https://www.python.org/downloads/windows/
   - ⚠️ **Important**: Check "Add Python to PATH" during installation
   - Verify: Open Command Prompt, type `python --version`

2. **Install Git** (Optional but recommended)
   - Download from: https://git-scm.com/download/win

### Step 2: Network Configuration
1. **Set Static IP Address**
   - Open Control Panel → Network and Internet → Network and Sharing Center
   - Click "Change adapter settings"
   - Right-click your network adapter → Properties
   - Select "Internet Protocol Version 4 (TCP/IPv4)" → Properties
   - Choose "Use the following IP address":
     ```
     IP address: 192.168.1.100 (choose available IP in your network)
     Subnet mask: 255.255.255.0
     Default gateway: 192.168.1.1 (your router's IP)
     DNS servers: 8.8.8.8, 8.8.4.4
     ```

2. **Configure Windows Firewall**
   - **Automatic**: Run the setup script (it configures firewall automatically)
   - **Manual**: Open Windows Firewall → Advanced settings → Inbound Rules → New Rule
     - Rule Type: Port
     - Protocol: TCP
     - Port: 8000
     - Action: Allow the connection
     - Name: "Legal Cases API Server"

### Step 3: Server Installation
1. **Copy application files** to the server device (e.g., `C:\legal-cases-app\`)

2. **Run Initial Setup** (as Administrator)
   ```cmd
   # Method 1: Simple batch file
   Right-click Command Prompt → Run as administrator
   cd C:\legal-cases-app\deployment
   setup-server.bat
   
   # Method 2: PowerShell (more features)
   Right-click PowerShell → Run as administrator
   cd C:\legal-cases-app\deployment
   .\start-server.ps1 -Setup
   ```

3. **Start the Server**
   ```cmd
   # Simple method
   cd C:\legal-cases-app\deployment
   start-server.bat
   
   # PowerShell method
   .\start-server.ps1 -Start
   ```

4. **Verify Server is Running**
   - Open web browser on server
   - Go to: `http://localhost:8000/docs`
   - You should see the API documentation

### Step 4: Note Server IP Address
- The setup script will display the server IP address
- It's also saved in: `C:\legal-cases\server-ip.txt`
- Example: `192.168.1.100`

---

## 💻 CLIENT DEVICES SETUP

### Step 1: Prerequisites (Each Client Device)
1. **Install Node.js**
   - Download from: https://nodejs.org/
   - Choose LTS version
   - Use default installation settings

2. **Copy application files** to each client device

### Step 2: Configure Client
1. **Get Server IP Address** from the server device (e.g., `192.168.1.100`)

2. **Run Client Configuration**
   ```cmd
   # Method 1: Simple batch file
   cd C:\legal-cases-app\deployment
   configure-client.bat 192.168.1.100
   
   # Method 2: PowerShell (more features)
   .\configure-client.ps1 -ServerIP 192.168.1.100
   ```

### Step 3: Install and Run Desktop App
1. **Install Dependencies** (first time only)
   ```cmd
   cd C:\legal-cases-app\frontend\desktop-app
   npm install
   ```

2. **Start Desktop Application**
   ```cmd
   npm run electron-dev
   ```

3. **Create Desktop Shortcut** (Optional)
   - Create a batch file: `start-legal-cases.bat`
   ```cmd
   @echo off
   cd /d "C:\legal-cases-app\frontend\desktop-app"
   npm run electron-dev
   ```
   - Create shortcut to this batch file on desktop

---

## 🚀 QUICK START CHECKLIST

### Server Device:
- [ ] Install Python 3.9+
- [ ] Set static IP address (e.g., 192.168.1.100)
- [ ] Copy application files
- [ ] Run `setup-server.bat` as Administrator
- [ ] Start server with `start-server.bat`
- [ ] Verify at `http://localhost:8000/docs`

### Each Client Device:
- [ ] Install Node.js
- [ ] Copy application files
- [ ] Run `configure-client.bat [SERVER_IP]`
- [ ] Navigate to `frontend\desktop-app`
- [ ] Run `npm install` (first time only)
- [ ] Run `npm run electron-dev`

---

## 🔧 TROUBLESHOOTING

### Server Issues:

**Problem**: Cannot start server
**Solutions**:
- Ensure Python is installed and in PATH
- Run setup as Administrator
- Check if port 8000 is already in use: `netstat -an | findstr :8000`

**Problem**: Clients cannot connect
**Solutions**:
- Verify server IP address: `ipconfig`
- Check Windows Firewall settings
- Test connection: `telnet [SERVER_IP] 8000`

### Client Issues:

**Problem**: "Cannot connect to server"
**Solutions**:
- Verify server is running
- Check server IP address
- Ensure both devices are on same network
- Test with web browser: `http://[SERVER_IP]:8000/docs`

**Problem**: Desktop app won't start
**Solutions**:
- Ensure Node.js is installed
- Run `npm install` in desktop-app directory
- Check for error messages in terminal

---

## 📁 FILE STRUCTURE

```
C:\legal-cases-app\
├── backend\                 # Server code
├── frontend\desktop-app\    # Desktop application
├── database\               # Database files
├── deployment\             # Setup scripts
│   ├── setup-server.bat      # Server setup (simple)
│   ├── start-server.bat      # Start server (simple)
│   ├── start-server.ps1      # PowerShell server script
│   ├── configure-client.bat  # Client config (simple)
│   ├── configure-client.ps1  # PowerShell client script
│   └── windows-server-setup.md
└── README.md
```

---

## 🔒 SECURITY NOTES

1. **Change Default Credentials**
   - Default admin: username=`admin`, password=`admin123`
   - Change immediately after first login

2. **Network Security**
   - Use only on trusted local networks
   - Consider VPN for remote access
   - Regularly backup database files

3. **Firewall Rules**
   - Server: Allow inbound on port 8000 from local network only
   - Clients: No special firewall configuration needed

---

## 📞 SUPPORT

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Ensure network connectivity between devices
4. Check Windows Event Viewer for detailed error messages

For advanced configuration, see the PowerShell scripts which provide more detailed logging and error handling.
