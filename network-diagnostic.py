#!/usr/bin/env python3
"""
Network Diagnostic Tool for Legal Cases Management System
Helps diagnose and fix network connectivity issues
"""
import socket
import subprocess
import sys
import requests
import platform
from typing import List, Dict
import json

class NetworkDiagnostic:
    def __init__(self):
        self.server_port = 8000
        self.api_endpoints = [
            "/",
            "/api/v1/info", 
            "/api/v1/auth/login"
        ]
        
    def get_local_ip_addresses(self) -> List[str]:
        """Get all local IP addresses"""
        ips = []
        try:
            # Get hostname IP
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            ips.append(local_ip)
            
            # Get all network interfaces
            if platform.system() == "Windows":
                result = subprocess.run(['ipconfig'], capture_output=True, text=True, shell=True)
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'IPv4 Address' in line or 'IP Address' in line:
                        ip = line.split(':')[-1].strip()
                        if ip and ip not in ips and not ip.startswith('127.'):
                            ips.append(ip)
            else:
                # Linux/Unix
                result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
                for ip in result.stdout.split():
                    if ip not in ips and not ip.startswith('127.'):
                        ips.append(ip)
                        
        except Exception as e:
            print(f"Error getting IP addresses: {e}")
            
        return ips
    
    def check_port_listening(self, ip: str, port: int) -> bool:
        """Check if port is listening on specific IP"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def test_api_endpoint(self, ip: str, endpoint: str) -> Dict:
        """Test API endpoint accessibility"""
        url = f"http://{ip}:{self.server_port}{endpoint}"
        try:
            response = requests.get(url, timeout=5)
            return {
                "url": url,
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "error": None
            }
        except Exception as e:
            return {
                "url": url,
                "status_code": None,
                "success": False,
                "error": str(e)
            }
    
    def check_firewall_windows(self) -> List[str]:
        """Check Windows firewall rules for port 8000"""
        suggestions = []
        try:
            # Check if port 8000 is allowed
            result = subprocess.run([
                'netsh', 'advfirewall', 'firewall', 'show', 'rule', 
                'name=all', 'dir=in', 'type=allow'
            ], capture_output=True, text=True, shell=True)
            
            if '8000' not in result.stdout:
                suggestions.append("Port 8000 may be blocked by Windows Firewall")
                suggestions.append("Run as Administrator: netsh advfirewall firewall add rule name=\"Legal Cases API\" dir=in action=allow protocol=TCP localport=8000")
                
        except Exception as e:
            suggestions.append(f"Could not check firewall: {e}")
            
        return suggestions
    
    def run_diagnostic(self):
        """Run complete network diagnostic"""
        print("🔍 Legal Cases Network Diagnostic Tool")
        print("=" * 50)
        
        # Get IP addresses
        ips = self.get_local_ip_addresses()
        print(f"📍 Found IP addresses: {', '.join(ips)}")
        
        # Check if server is running on any IP
        print(f"\n🚀 Checking if server is running on port {self.server_port}:")
        server_running = False
        
        for ip in ['127.0.0.1', '0.0.0.0'] + ips:
            is_listening = self.check_port_listening(ip, self.server_port)
            status = "✅ LISTENING" if is_listening else "❌ NOT LISTENING"
            print(f"   {ip}:{self.server_port} - {status}")
            if is_listening:
                server_running = True
        
        if not server_running:
            print("\n❌ Server is not running! Start the server first:")
            print("   cd backend && python main.py")
            return
        
        # Test API endpoints
        print(f"\n🌐 Testing API endpoints:")
        for ip in ['127.0.0.1'] + ips:
            print(f"\n   Testing on {ip}:")
            for endpoint in self.api_endpoints:
                result = self.test_api_endpoint(ip, endpoint)
                status = "✅" if result["success"] else "❌"
                print(f"     {status} {result['url']} - {result.get('status_code', 'ERROR')}")
                if result["error"]:
                    print(f"       Error: {result['error']}")
        
        # Platform specific checks
        if platform.system() == "Windows":
            print(f"\n🛡️ Windows Firewall Check:")
            firewall_suggestions = self.check_firewall_windows()
            for suggestion in firewall_suggestions:
                print(f"   ⚠️ {suggestion}")
        
        # Network suggestions
        print(f"\n💡 Network Access URLs:")
        for ip in ips:
            if ip != '127.0.0.1':
                print(f"   🌐 http://{ip}:{self.server_port}")
                print(f"   📱 Use this URL in your desktop app: http://{ip}:{self.server_port}")
        
        # Troubleshooting steps
        print(f"\n🔧 If other devices still can't connect:")
        print("   1. Disable Windows Defender Firewall temporarily to test")
        print("   2. Check if antivirus is blocking the connection")
        print("   3. Ensure all devices are on the same network/subnet")
        print("   4. Try connecting from another device using: telnet <server_ip> 8000")
        print("   5. Check router/switch configuration")
        
        print(f"\n📋 Server Configuration Summary:")
        print(f"   - Server IPs: {', '.join(ips)}")
        print(f"   - Port: {self.server_port}")
        print(f"   - Status: {'Running' if server_running else 'Not Running'}")

if __name__ == "__main__":
    try:
        diagnostic = NetworkDiagnostic()
        diagnostic.run_diagnostic()
    except KeyboardInterrupt:
        print("\n\n👋 Diagnostic cancelled by user")
    except Exception as e:
        print(f"\n❌ Diagnostic error: {e}")
        print("Make sure you have the required dependencies: pip install requests")
