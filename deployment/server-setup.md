# Server Device Network Setup Guide

## 1. Network Configuration

### Find Server IP Address
```bash
# Get the server's IP address on the local network
ip addr show
# or
ifconfig
# Look for the IP address in your local network range (e.g., 192.168.1.x, 10.0.0.x)
```

### Configure Static IP (Recommended)
```bash
# Edit network configuration (Ubuntu/Debian)
sudo nano /etc/netplan/01-netcfg.yaml

# Example configuration:
network:
  version: 2
  ethernets:
    eth0:  # or your network interface name
      dhcp4: false
      addresses:
        - 192.168.1.100/24  # Choose an available IP in your network
      gateway4: 192.168.1.1  # Your router's IP
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4

# Apply configuration
sudo netplan apply
```

## 2. Firewall Configuration

```bash
# Install and configure UFW (Uncomplicated Firewall)
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 8000/tcp  # FastAPI server port
sudo ufw allow from 192.168.1.0/24 to any port 8000  # Allow only local network
sudo ufw status
```

## 3. System Prerequisites

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv git -y

# Install Node.js (if needed for deployment tools)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```
