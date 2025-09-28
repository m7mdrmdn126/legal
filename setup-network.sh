#!/bin/bash
# Legal Cases Management System - Network Setup and Test Script

echo "=========================================="
echo "Legal Cases Server Network Setup"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# Get server IP address
print_info "Detecting server IP address..."
SERVER_IP=$(hostname -I | awk '{print $1}')
if [ -z "$SERVER_IP" ]; then
    SERVER_IP=$(ip route get 8.8.8.8 | awk -F"src " 'NR==1{split($2,a," ");print a[1]}')
fi

echo "Server IP Address: $SERVER_IP"
echo ""

# Check if server is running
print_info "Checking if server is running on port 8000..."
if netstat -tuln 2>/dev/null | grep -q ":8000.*LISTEN"; then
    print_success "Server is listening on port 8000"
    
    # Check if listening on all interfaces
    if netstat -tuln 2>/dev/null | grep -q "0.0.0.0:8000"; then
        print_success "Server is listening on all interfaces (0.0.0.0:8000)"
    else
        print_warning "Server might not be listening on all interfaces"
        print_info "Make sure server is started with: uvicorn main:app --host 0.0.0.0 --port 8000"
    fi
else
    print_error "Server is NOT listening on port 8000"
    print_info "Please start the server first:"
    print_info "cd backend && uvicorn main:app --host 0.0.0.0 --port 8000"
    exit 1
fi

echo ""

# Configure firewall
print_info "Configuring firewall rules..."

# Check if UFW is installed and active
if command -v ufw >/dev/null 2>&1; then
    if sudo ufw status | grep -q "Status: active"; then
        print_info "UFW firewall is active, adding rules..."
        sudo ufw allow 8000/tcp >/dev/null 2>&1
        sudo ufw allow from 192.168.0.0/16 to any port 8000 >/dev/null 2>&1
        sudo ufw allow from 10.0.0.0/8 to any port 8000 >/dev/null 2>&1
        sudo ufw allow from 172.16.0.0/12 to any port 8000 >/dev/null 2>&1
        print_success "Firewall rules added for port 8000"
    else
        print_info "UFW firewall is not active"
    fi
else
    print_info "UFW not installed, checking iptables..."
    # Add basic iptables rule if needed
    if command -v iptables >/dev/null 2>&1; then
        sudo iptables -C INPUT -p tcp --dport 8000 -j ACCEPT 2>/dev/null || \
        sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
        print_success "Iptables rule added for port 8000"
    fi
fi

echo ""

# Test local connectivity
print_info "Testing local server connectivity..."

if curl -s --max-time 5 http://localhost:8000/api/v1/info >/dev/null 2>&1; then
    print_success "Local API access working (localhost:8000)"
else
    print_error "Local API access failed (localhost:8000)"
fi

if curl -s --max-time 5 http://$SERVER_IP:8000/api/v1/info >/dev/null 2>&1; then
    print_success "Network API access working ($SERVER_IP:8000)"
else
    print_error "Network API access failed ($SERVER_IP:8000)"
    print_warning "This means other devices won't be able to connect!"
fi

echo ""

# Network information
print_info "Network configuration summary:"
echo "Server listening on: 0.0.0.0:8000"
echo "Server IP address: $SERVER_IP"
echo "Local access URL: http://localhost:8000"
echo "Network access URL: http://$SERVER_IP:8000"
echo "API documentation: http://$SERVER_IP:8000/docs"

echo ""

# Client configuration
print_info "Client device configuration:"
echo "Edit the .env file on each client device:"
echo "SERVER_IP=$SERVER_IP"
echo "SERVER_PORT=8000"

echo ""

# Test commands for client devices
print_info "Test commands for CLIENT devices:"
echo "1. Test connectivity:"
echo "   ping $SERVER_IP"
echo ""
echo "2. Test port access:"
echo "   telnet $SERVER_IP 8000"
echo "   (or: nc -zv $SERVER_IP 8000)"
echo ""
echo "3. Test API access:"
echo "   curl http://$SERVER_IP:8000/api/v1/info"
echo ""
echo "4. Test in web browser:"
echo "   http://$SERVER_IP:8000/docs"

echo ""
echo "=========================================="
print_success "Network setup completed!"
echo "=========================================="

# Save configuration for reference
CONFIG_FILE="$HOME/legal-cases-server-config.txt"
cat > "$CONFIG_FILE" << EOF
Legal Cases Management Server Configuration
==========================================
Generated: $(date)

Server IP: $SERVER_IP
Server Port: 8000
Network URL: http://$SERVER_IP:8000
API Docs: http://$SERVER_IP:8000/docs

Client Configuration:
SERVER_IP=$SERVER_IP
SERVER_PORT=8000

Test Commands (run on client devices):
ping $SERVER_IP
curl http://$SERVER_IP:8000/api/v1/info

Firewall: Port 8000 allowed for local networks
EOF

print_success "Configuration saved to: $CONFIG_FILE"
