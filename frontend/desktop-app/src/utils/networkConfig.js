// Network Configuration Utility for Legal Cases Desktop App
// This file helps configure the desktop app to connect to network servers

class NetworkConfig {
    constructor() {
        this.defaultPort = 8000;
        this.defaultHost = 'localhost';
        this.currentConfig = null;
    }

    // Auto-discover server on local network
    async discoverServers() {
        const possibleIPs = this.generateLocalIPRange();
        const servers = [];
        
        console.log('🔍 Scanning for Legal Cases servers on local network...');
        
        const promises = possibleIPs.map(ip => this.testServerConnection(ip));
        const results = await Promise.allSettled(promises);
        
        results.forEach((result, index) => {
            if (result.status === 'fulfilled' && result.value.available) {
                servers.push({
                    ip: possibleIPs[index],
                    url: `http://${possibleIPs[index]}:${this.defaultPort}`,
                    status: result.value.status,
                    responseTime: result.value.responseTime
                });
            }
        });

        console.log(`✅ Found ${servers.length} server(s):`, servers);
        return servers;
    }

    // Generate common local network IP ranges
    generateLocalIPRange() {
        const ips = [];
        
        // Add common router IPs
        ips.push('192.168.1.1', '192.168.0.1', '10.0.0.1');
        
        // Generate 192.168.1.x range (most common)
        for (let i = 2; i <= 50; i++) {
            ips.push(`192.168.1.${i}`);
        }
        
        // Generate 192.168.0.x range
        for (let i = 2; i <= 20; i++) {
            ips.push(`192.168.0.${i}`);
        }
        
        // Generate 10.0.0.x range
        for (let i = 2; i <= 20; i++) {
            ips.push(`10.0.0.${i}`);
        }
        
        // Generate 169.254.x.x range (APIPA/Link-local)
        for (let i = 1; i <= 254; i++) {
            ips.push(`169.254.25.${i}`); // Based on your 169.254.25.11
        }
        
        return ips;
    }

    // Test if server is available at given IP
    async testServerConnection(ip, timeout = 3000) {
        const startTime = Date.now();
        const url = `http://${ip}:${this.defaultPort}/api/v1/info`;
        
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeout);
            
            const response = await fetch(url, { 
                signal: controller.signal,
                mode: 'cors'
            });
            
            clearTimeout(timeoutId);
            
            if (response.ok) {
                const data = await response.json();
                return {
                    available: true,
                    status: response.status,
                    responseTime: Date.now() - startTime,
                    serverInfo: data
                };
            }
        } catch (error) {
            // Connection failed
        }
        
        return {
            available: false,
            responseTime: Date.now() - startTime
        };
    }

    // Save server configuration
    saveConfig(serverUrl) {
        this.currentConfig = {
            serverUrl: serverUrl,
            savedAt: new Date().toISOString()
        };
        
        // Save to localStorage
        if (typeof localStorage !== 'undefined') {
            localStorage.setItem('legalCasesServerConfig', JSON.stringify(this.currentConfig));
        }
        
        console.log('✅ Server configuration saved:', this.currentConfig);
        return this.currentConfig;
    }

    // Load saved configuration
    loadConfig() {
        try {
            if (typeof localStorage !== 'undefined') {
                const saved = localStorage.getItem('legalCasesServerConfig');
                if (saved) {
                    this.currentConfig = JSON.parse(saved);
                    console.log('📋 Loaded server configuration:', this.currentConfig);
                    return this.currentConfig;
                }
            }
        } catch (error) {
            console.warn('Could not load saved configuration:', error);
        }
        return null;
    }

    // Get current API base URL
    getApiBaseUrl() {
        if (this.currentConfig && this.currentConfig.serverUrl) {
            return `${this.currentConfig.serverUrl}/api/v1`;
        }
        return `http://${this.defaultHost}:${this.defaultPort}/api/v1`;
    }

    // Test current configuration
    async testCurrentConfig() {
        const baseUrl = this.getApiBaseUrl();
        const testUrl = baseUrl.replace('/api/v1', '/api/v1/info');
        
        try {
            const response = await fetch(testUrl);
            const data = await response.json();
            
            return {
                success: true,
                status: response.status,
                serverInfo: data,
                url: testUrl
            };
        } catch (error) {
            return {
                success: false,
                error: error.message,
                url: testUrl
            };
        }
    }

    // Manual server configuration
    setManualConfig(ip, port = this.defaultPort) {
        const serverUrl = `http://${ip}:${port}`;
        return this.saveConfig(serverUrl);
    }
}

// Create global instance
const networkConfig = new NetworkConfig();

// Auto-load configuration when module loads
if (typeof window !== 'undefined') {
    networkConfig.loadConfig();
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = networkConfig;
} else if (typeof window !== 'undefined') {
    window.networkConfig = networkConfig;
}

// Usage examples:
/*

// 1. Auto-discover servers
const servers = await networkConfig.discoverServers();
if (servers.length > 0) {
    networkConfig.saveConfig(servers[0].url);
}

// 2. Manual configuration
networkConfig.setManualConfig('169.254.25.11', 8000);

// 3. Test current configuration
const test = await networkConfig.testCurrentConfig();
console.log('Server test:', test);

// 4. Get API base URL for requests
const apiUrl = networkConfig.getApiBaseUrl();
console.log('API URL:', apiUrl);

*/
