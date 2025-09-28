# Legal Cases Management System - Network Deployment Solution

## 🔍 Problem Analysis

Based on your network test results, I can see that:

✅ **What's Working:**
- Your FastAPI server is running on port 8000 (PID 87680/94872)
- Server is binding to `0.0.0.0:8000` (listening on all interfaces)
- Local connections work (127.0.0.1)
- Some network connections work (169.254.25.11 visible in logs)
- Ping to server IP works from other devices

❌ **The Issue:**
- Other devices on the network cannot access the API endpoints
- This is likely a **Windows Firewall** blocking issue

## 🛠️ Complete Solution

### **Step 1: Fix Windows Firewall (CRITICAL)**

Run the provided scripts **as Administrator**:

#### Option A: Automated Setup (Recommended)
```cmd
# Right-click Command Prompt -> Run as Administrator
setup-windows-network.bat
```

#### Option B: PowerShell (Advanced)
```powershell
# Right-click PowerShell -> Run as Administrator
.\setup-windows-network.ps1
```

#### Option C: Manual Firewall Configuration
```cmd
# Run as Administrator
netsh advfirewall firewall add rule name="Legal Cases API" dir=in action=allow protocol=TCP localport=8000
netsh advfirewall firewall add rule name="Legal Cases API Out" dir=out action=allow protocol=TCP localport=8000
```

### **Step 2: Verify Server Configuration**

Your server is correctly configured, but let's ensure it stays that way:

```python
# backend/main.py should have:
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # ✅ Correct - listens on all interfaces
        port=8000,
        reload=False,    # Disable in production
        access_log=True
    )
```

### **Step 3: Update Desktop App Configuration**

1. **Add the ServerConnectionSettings component** to your settings page
2. **Update the API service** to use network configuration

**In `src/pages/SettingsPreferences.js`:**
```javascript
import ServerConnectionSettings from '../components/ServerConnectionSettings';

// Add this component to your settings page:
<ServerConnectionSettings onConnectionChange={(connected, url) => {
    if (connected) {
        console.log('Connected to server:', url);
        // Update API base URL globally
    }
}} />
```

### **Step 4: Test Network Connectivity**

#### From Server Machine (Windows):
```cmd
# Check if port is listening
netstat -ano | findstr :8000

# Get your IP addresses
ipconfig

# Test local API
curl http://127.0.0.1:8000/api/v1/info
curl http://169.254.25.11:8000/api/v1/info
```

#### From Client Machine:
```cmd
# Test connectivity
ping 169.254.25.11
telnet 169.254.25.11 8000

# Test API (if curl available)
curl http://169.254.25.11:8000/api/v1/info
```

### **Step 5: Configure Desktop App for Network**

Based on your IP `169.254.25.11`, configure the desktop app:

1. **Run the desktop app**
2. **Go to Settings**
3. **Use the Server Connection Settings component**
4. **Enter server IP:** `169.254.25.11`
5. **Port:** `8000`
6. **Test Connection**

## 🚀 Network Deployment Checklist

### Server Setup (Windows Machine):
- [ ] Server running on `0.0.0.0:8000`
- [ ] Windows Firewall configured for port 8000
- [ ] Antivirus exceptions added (if needed)
- [ ] Server IP noted: `169.254.25.11`

### Client Setup (Other Machines):
- [ ] Desktop app installed
- [ ] Server connection configured: `http://169.254.25.11:8000`
- [ ] Network connectivity tested
- [ ] API endpoints accessible

### Network Infrastructure:
- [ ] All devices on same switch/network
- [ ] No router blocking between devices
- [ ] DHCP/static IP configured properly

## 🔧 Troubleshooting Guide

### If clients still can't connect:

#### **Windows Firewall Issues:**
```cmd
# Temporarily disable to test (NOT recommended for production)
netsh advfirewall set allprofiles state off

# Test connection, then re-enable:
netsh advfirewall set allprofiles state on
```

#### **Antivirus Software:**
- Add exception for Python/uvicorn process
- Add exception for port 8000
- Temporarily disable real-time protection to test

#### **Network Issues:**
```cmd
# Check routing table
route print

# Check network adapter configuration
ipconfig /all

# Test basic connectivity
ping <client-ip>
```

#### **Application Issues:**
```cmd
# Restart server with verbose logging
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --log-level debug
```

## 📋 Server URLs for Client Configuration

Based on your network, use these URLs in your desktop apps:

- **Primary:** `http://169.254.25.11:8000`
- **API Base:** `http://169.254.25.11:8000/api/v1`

## 🏃 Quick Start Commands

### On Server (Windows):
```cmd
# 1. Configure firewall (as Admin)
setup-windows-network.bat

# 2. Start server
cd backend
python main.py

# 3. Get server URLs
get-server-urls.bat
```

### On Clients:
1. Install desktop app
2. Open Settings → Server Connection
3. Enter: `169.254.25.11:8000`
4. Click "Test Connection"
5. Save configuration

## 📞 Support Information

Your network configuration:
- **Server IP:** 169.254.25.11 (APIPA/Link-local)
- **Port:** 8000
- **Network Type:** Switch-based local network
- **OS:** Windows (server)

This APIPA address suggests you might not have DHCP configured. Consider:
1. Setting up DHCP on your router/switch
2. Or configuring static IPs in the 192.168.x.x range
3. Current setup will work but APIPA can be less reliable
