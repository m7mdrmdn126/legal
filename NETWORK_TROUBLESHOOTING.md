# Legal Cases Management System - Network Connectivity Troubleshooting Guide

## 🔧 Problem: Other devices can't connect to server on local network

### Overview
You have:
- **Server device** running backend on `0.0.0.0:8000`
- **Switch/Local network** connecting multiple devices
- **Client devices** that can't reach the server

---

## 🔍 Step-by-Step Troubleshooting

### **Step 1: Verify Server is Running Correctly**

On the **server device**, run these commands:

```bash
# Check if server is listening on all interfaces
sudo netstat -tuln | grep :8000
# Should show: 0.0.0.0:8000 LISTEN

# Alternative command
sudo ss -tuln | grep :8000

# Check if process is running
ps aux | grep uvicorn
```

**Expected output:**
```
tcp    0    0  0.0.0.0:8000    0.0.0.0:*    LISTEN
```

### **Step 2: Find Server's IP Address**

On the **server device**:

```bash
# Get server's IP address
ip addr show
# Look for the IP in your network range (e.g., 192.168.1.x)

# Or use simpler command
hostname -I
```

**Note the server IP** (e.g., `192.168.1.100`)

### **Step 3: Test Local Server Access**

On the **server device**, test if it can access itself:

```bash
# Test API locally
curl http://localhost:8000/api/v1/info
curl http://127.0.0.1:8000/api/v1/info

# Test with actual IP address
curl http://[YOUR_SERVER_IP]:8000/api/v1/info
# Replace [YOUR_SERVER_IP] with actual IP like 192.168.1.100
```

### **Step 4: Check Firewall Settings**

#### **Linux Server (Ubuntu/Debian):**

```bash
# Check UFW status
sudo ufw status

# If UFW is active, allow port 8000
sudo ufw allow 8000/tcp
sudo ufw allow from 192.168.1.0/24 to any port 8000

# If using iptables directly
sudo iptables -L | grep 8000

# Add rule if needed
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
```

#### **Windows Server:**

```powershell
# Check Windows Firewall
Get-NetFirewallRule | Where-Object {$_.LocalPort -eq 8000}

# Add firewall rule
New-NetFirewallRule -DisplayName "Legal Cases API" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

### **Step 5: Test from Client Device**

On a **client device** (different computer):

```bash
# Test basic connectivity
ping [SERVER_IP]
# Replace [SERVER_IP] with server's actual IP

# Test port connectivity
telnet [SERVER_IP] 8000
# Or use nc (netcat)
nc -zv [SERVER_IP] 8000

# Test API endpoint
curl http://[SERVER_IP]:8000/api/v1/info
```

---

## 🛠️ Common Solutions

### **Solution 1: Fix Backend Configuration**

Update your backend startup to ensure it's binding to all interfaces:

**File: `backend/main.py`** - Add at the end:

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Listen on all interfaces
        port=8000,
        reload=False,    # Disable in production
        access_log=True
    )
```

**Start server with explicit binding:**

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### **Solution 2: Network Configuration Script**

Create this script on your **server device**:

```bash
#!/bin/bash
# Legal Cases Server Network Setup

echo "=== Legal Cases Server Network Configuration ==="

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')
echo "Server IP Address: $SERVER_IP"

# Check if server is running
if netstat -tuln | grep -q ":8000.*LISTEN"; then
    echo "✅ Server is listening on port 8000"
else
    echo "❌ Server is NOT listening on port 8000"
    echo "Start the server first!"
    exit 1
fi

# Configure firewall
echo "Configuring firewall..."
sudo ufw allow 8000/tcp
sudo ufw allow from 192.168.0.0/16 to any port 8000
sudo ufw allow from 10.0.0.0/8 to any port 8000

# Test local connectivity
echo "Testing local connectivity..."
if curl -s http://localhost:8000/api/v1/info > /dev/null; then
    echo "✅ Local API access working"
else
    echo "❌ Local API access failed"
fi

echo ""
echo "=== Client Configuration ==="
echo "Configure clients to connect to: http://$SERVER_IP:8000"
echo "Edit client .env file:"
echo "SERVER_IP=$SERVER_IP"
echo "SERVER_PORT=8000"
echo ""
echo "Test from client device:"
echo "curl http://$SERVER_IP:8000/api/v1/info"
```

### **Solution 3: CORS Configuration**

Update CORS settings in `backend/config/settings.py`:

```python
# CORS settings - allow all local network ranges
cors_origins: List[str] = [
    "http://localhost:3000",
    "http://localhost:8080", 
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
    # Allow all local network ranges
    "http://192.168.*:*",
    "http://10.*:*", 
    "http://172.16.*:*",
    "http://172.17.*:*",
    "http://172.18.*:*",
    "http://172.19.*:*",
    "http://172.20.*:*",
    "http://172.21.*:*",
    "http://172.22.*:*",
    "http://172.23.*:*",
    "http://172.24.*:*",
    "http://172.25.*:*",
    "http://172.26.*:*",
    "http://172.27.*:*",
    "http://172.28.*:*",
    "http://172.29.*:*",
    "http://172.30.*:*",
    "http://172.31.*:*"
]
```

**Or use wildcard CORS for local network (development only):**

```python
# In backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local network
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

## 🔧 Quick Fix Commands

### **Server Side:**

```bash
# 1. Stop current server
# Press Ctrl+C to stop

# 2. Start with explicit network binding  
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000

# 3. In another terminal, configure firewall
sudo ufw allow 8000/tcp
sudo ufw allow from 192.168.1.0/24 to any port 8000

# 4. Check server is accessible
curl http://$(hostname -I | awk '{print $1}'):8000/api/v1/info
```

### **Client Side:**

```bash
# 1. Find server IP (ask server admin or check router)
# 2. Test connectivity
ping [SERVER_IP]
telnet [SERVER_IP] 8000

# 3. Test API
curl http://[SERVER_IP]:8000/api/v1/info

# 4. Update client .env file
echo "SERVER_IP=[SERVER_IP]" > .env
echo "SERVER_PORT=8000" >> .env
```

---

## 🚨 Common Issues & Solutions

### **Issue 1: "Connection Refused"**
**Cause**: Server not listening on 0.0.0.0 or firewall blocking
**Solution**: Restart server with `--host 0.0.0.0` and configure firewall

### **Issue 2: "Connection Timeout"**
**Cause**: Network/firewall issue
**Solution**: Check firewall rules and network connectivity

### **Issue 3: "CORS Error"**  
**Cause**: CORS policy blocking cross-origin requests
**Solution**: Update CORS settings to allow local network

### **Issue 4: "Server IP Unknown"**
**Cause**: Don't know server's IP address
**Solution**: Run `hostname -I` on server or check router admin panel

---

## 📋 Network Setup Checklist

### **Server Device:**
- [ ] Server running with `--host 0.0.0.0`
- [ ] Port 8000 accessible locally (`curl localhost:8000/api/v1/info`)
- [ ] Firewall allows port 8000
- [ ] Server IP address known (e.g., 192.168.1.100)
- [ ] CORS configured for local network

### **Network:**
- [ ] All devices on same subnet/switch
- [ ] Network switch/router working properly
- [ ] No network isolation between devices

### **Client Devices:**
- [ ] Can ping server IP address
- [ ] Can connect to port 8000 (`telnet server-ip 8000`)
- [ ] .env file configured with correct server IP
- [ ] Desktop app updated with server configuration

---

## 🎯 Quick Test Commands

**On Server:**
```bash
# Get server IP and test local access
SERVER_IP=$(hostname -I | awk '{print $1}')
echo "Server IP: $SERVER_IP"
curl http://$SERVER_IP:8000/api/v1/info
```

**On Client:**
```bash
# Replace 192.168.1.100 with your server IP
SERVER_IP="192.168.1.100"
ping -c 3 $SERVER_IP
curl http://$SERVER_IP:8000/api/v1/info
```

Use this guide to systematically identify and fix the network connectivity issue! 🔧
