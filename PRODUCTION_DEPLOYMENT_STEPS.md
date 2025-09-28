# Legal Cases Management System - Production Deployment Steps

## 📋 Complete Deployment Process for Windows Server

### **Phase 1: Prepare Windows Server Environment**

#### Step 1: Pull Latest Code
```cmd
# Navigate to your project directory
cd C:\path\to\legal_cases\app-v2

# Pull latest changes from repository
git pull origin main

# Verify all new files are present
dir setup-windows-network.bat
dir start-network-server.bat
dir NETWORK_DEPLOYMENT_SOLUTION.md
```

#### Step 2: Update Backend Dependencies
```cmd
# Navigate to backend directory
cd backend

# Activate virtual environment (if using one)
# .venv\Scripts\activate

# Install/update any new dependencies
pip install -r requirements.txt

# Test backend server
python main.py
```

### **Phase 2: Uninstall Old Production App**

#### Step 3: Uninstall Previous Desktop App Version
```cmd
# Method 1: Windows Settings
# Go to Settings > Apps > Apps & features
# Find "Legal Cases Management" or similar name
# Click Uninstall

# Method 2: Control Panel
# Control Panel > Programs > Programs and Features
# Find your app and uninstall

# Method 3: Check if there's an uninstaller
# Look in: C:\Program Files\Legal Cases Management\uninstall.exe
# Or: C:\Users\%USERNAME%\AppData\Local\Programs\legal-cases-desktop\
```

#### Step 4: Clean App Data (Optional but Recommended)
```cmd
# Remove old configuration files
del "%APPDATA%\legal-cases-desktop\*.*" /s /q
del "%LOCALAPPDATA%\legal-cases-desktop\*.*" /s /q

# Clear old cache
del "%TEMP%\legal-cases*" /s /q
```

### **Phase 3: Configure Network Environment**

#### Step 5: Setup Windows Network Configuration
```cmd
# IMPORTANT: Run Command Prompt as Administrator
# Right-click Command Prompt > Run as administrator

# Navigate to project directory
cd C:\path\to\legal_cases\app-v2

# Run network setup script
setup-windows-network.bat

# This will:
# - Configure Windows Firewall for port 8000
# - Create helper scripts
# - Test network connectivity
```

#### Step 6: Verify Network Configuration
```cmd
# Check firewall rules
netsh advfirewall firewall show rule name="Legal Cases API*"

# Test port availability
netstat -ano | findstr :8000

# Get server IP addresses
ipconfig
```

### **Phase 4: Build New Production App**

#### Step 7: Update Frontend Configuration
```cmd
# Navigate to frontend desktop app directory
cd frontend\desktop-app

# Install/update dependencies
npm install

# The new network configuration components are now included:
# - src/utils/networkConfig.js
# - src/components/ServerConnectionSettings.js
```

#### Step 8: Build New Production App
```cmd
# Build the Electron desktop app
npm run build

# Package for Windows
npm run dist

# This creates the installer in: dist/
# Look for: legal-cases-desktop Setup 1.0.0.exe (or similar)
```

### **Phase 5: Deploy and Test**

#### Step 9: Install New Production App
```cmd
# Navigate to dist directory
cd dist

# Run the installer
"legal-cases-desktop Setup 1.0.0.exe"

# Follow installation wizard
# Choose installation directory
# Create desktop shortcuts if desired
```

#### Step 10: Configure Server Connection
```cmd
# Start the backend server first
cd C:\path\to\legal_cases\app-v2
start-network-server.bat

# Launch the desktop app
# Go to Settings/Preferences
# You should now see "Server Connection Settings"
# Enter your server IP: 169.254.25.11
# Port: 8000
# Test connection
```

### **Phase 6: Network Deployment**

#### Step 11: Deploy to Client Machines
```cmd
# Copy the installer to client machines
# Install on each client machine
# Configure server connection on each client:
# Server IP: 169.254.25.11 (your Windows server IP)
# Port: 8000
```

## 🔧 **Alternative: Quick Update Without Full Reinstall**

If you want to avoid full reinstallation, you can try updating in-place:

### Option A: Portable App Update
```cmd
# If using portable version:
# 1. Close the app
# 2. Backup current app folder
# 3. Replace app files with new build
# 4. Restart app
```

### Option B: Development Mode Update
```cmd
# Run in development mode with latest code:
cd frontend\desktop-app
npm start

# This runs the latest version without rebuilding installer
```

## 📝 **Production Checklist**

### Server Setup:
- [ ] Code pulled and updated
- [ ] Backend dependencies installed
- [ ] Network setup script executed (as Administrator)
- [ ] Windows Firewall configured
- [ ] Server starts successfully on 0.0.0.0:8000

### Desktop App:
- [ ] Old version uninstalled
- [ ] New version built and installed
- [ ] Server connection settings configured
- [ ] Connection test successful
- [ ] App functions properly

### Network:
- [ ] All client machines can ping server
- [ ] Port 8000 accessible from clients
- [ ] API endpoints responding from network
- [ ] Multiple clients can connect simultaneously

## 🚨 **Important Notes**

1. **Run as Administrator**: The network setup MUST be run as Administrator for firewall configuration

2. **Firewall Critical**: Without proper firewall configuration, network access will fail

3. **Server IP**: Note your actual server IP address (currently 169.254.25.11) and use it in all client configurations

4. **Backup**: Always backup your database before major updates:
   ```cmd
   copy database\legal_cases.db database\legal_cases_backup_%date%.db
   ```

5. **Testing**: Test with one client first before deploying to all machines

## 🎯 **Expected Results**

After following these steps:
- ✅ Server accessible from all network devices
- ✅ Desktop apps can connect to network server
- ✅ Multiple users can use the system simultaneously  
- ✅ All API endpoints work across network
- ✅ Real-time updates work for all connected clients
