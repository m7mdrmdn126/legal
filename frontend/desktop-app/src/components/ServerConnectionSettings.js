import React, { useState, useEffect } from 'react';
import '../utils/networkConfig.js';

const ServerConnectionSettings = ({ onConnectionChange }) => {
    const [serverIP, setServerIP] = useState('');
    const [serverPort, setServerPort] = useState('8000');
    const [connectionStatus, setConnectionStatus] = useState('unknown');
    const [discoveredServers, setDiscoveredServers] = useState([]);
    const [isScanning, setIsScanning] = useState(false);
    const [serverInfo, setServerInfo] = useState(null);

    // Load saved configuration on component mount
    useEffect(() => {
        const config = window.networkConfig?.loadConfig();
        if (config && config.serverUrl) {
            const url = new URL(config.serverUrl);
            setServerIP(url.hostname);
            setServerPort(url.port || '8000');
            testConnection(url.hostname, url.port || '8000');
        }
    }, []);

    // Test server connection
    const testConnection = async (ip = serverIP, port = serverPort) => {
        if (!ip) return;
        
        setConnectionStatus('testing');
        try {
            window.networkConfig.setManualConfig(ip, parseInt(port));
            const result = await window.networkConfig.testCurrentConfig();
            
            if (result.success) {
                setConnectionStatus('connected');
                setServerInfo(result.serverInfo);
                if (onConnectionChange) {
                    onConnectionChange(true, `http://${ip}:${port}`);
                }
            } else {
                setConnectionStatus('failed');
                setServerInfo(null);
                if (onConnectionChange) {
                    onConnectionChange(false, null);
                }
            }
        } catch (error) {
            setConnectionStatus('failed');
            setServerInfo(null);
            if (onConnectionChange) {
                onConnectionChange(false, null);
            }
        }
    };

    // Auto-discover servers on network
    const discoverServers = async () => {
        setIsScanning(true);
        try {
            const servers = await window.networkConfig.discoverServers();
            setDiscoveredServers(servers);
            
            // Auto-select first discovered server
            if (servers.length > 0) {
                const url = new URL(servers[0].url);
                setServerIP(url.hostname);
                setServerPort(url.port);
                window.networkConfig.saveConfig(servers[0].url);
                await testConnection(url.hostname, url.port);
            }
        } catch (error) {
            console.error('Server discovery failed:', error);
        } finally {
            setIsScanning(false);
        }
    };

    // Select a discovered server
    const selectServer = async (server) => {
        const url = new URL(server.url);
        setServerIP(url.hostname);
        setServerPort(url.port);
        window.networkConfig.saveConfig(server.url);
        await testConnection(url.hostname, url.port);
    };

    const getStatusIcon = () => {
        switch (connectionStatus) {
            case 'connected': return '✅';
            case 'failed': return '❌';
            case 'testing': return '🔄';
            default: return '⚪';
        }
    };

    const getStatusText = () => {
        switch (connectionStatus) {
            case 'connected': return 'متصل';
            case 'failed': return 'فشل الاتصال';
            case 'testing': return 'جاري الاختبار...';
            default: return 'غير محدد';
        }
    };

    const getStatusColor = () => {
        switch (connectionStatus) {
            case 'connected': return '#4CAF50';
            case 'failed': return '#f44336';
            case 'testing': return '#ff9800';
            default: return '#9e9e9e';
        }
    };

    return (
        <div style={{ padding: '20px', backgroundColor: '#f5f5f5', borderRadius: '8px', margin: '20px 0' }}>
            <h3 style={{ marginBottom: '20px', color: '#333' }}>
                🌐 إعدادات اتصال الخادم
            </h3>

            {/* Current Connection Status */}
            <div style={{ 
                padding: '15px', 
                backgroundColor: 'white', 
                borderRadius: '6px', 
                marginBottom: '20px',
                border: `2px solid ${getStatusColor()}`
            }}>
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}>
                    <span style={{ fontSize: '20px', marginLeft: '10px' }}>{getStatusIcon()}</span>
                    <strong>حالة الاتصال: </strong>
                    <span style={{ color: getStatusColor(), marginRight: '10px' }}>{getStatusText()}</span>
                </div>
                
                {serverInfo && (
                    <div style={{ fontSize: '12px', color: '#666' }}>
                        <div>اسم الخدمة: {serverInfo.name}</div>
                        <div>الإصدار: {serverInfo.version}</div>
                    </div>
                )}
            </div>

            {/* Manual Configuration */}
            <div style={{ backgroundColor: 'white', padding: '15px', borderRadius: '6px', marginBottom: '20px' }}>
                <h4>إعداد يدوي</h4>
                
                <div style={{ display: 'flex', gap: '10px', marginBottom: '15px', alignItems: 'center' }}>
                    <div>
                        <label style={{ display: 'block', marginBottom: '5px' }}>عنوان IP للخادم:</label>
                        <input
                            type="text"
                            value={serverIP}
                            onChange={(e) => setServerIP(e.target.value)}
                            placeholder="مثال: 192.168.1.100"
                            style={{ 
                                padding: '8px', 
                                border: '1px solid #ddd', 
                                borderRadius: '4px',
                                width: '150px'
                            }}
                        />
                    </div>
                    
                    <div>
                        <label style={{ display: 'block', marginBottom: '5px' }}>المنفذ:</label>
                        <input
                            type="number"
                            value={serverPort}
                            onChange={(e) => setServerPort(e.target.value)}
                            placeholder="8000"
                            style={{ 
                                padding: '8px', 
                                border: '1px solid #ddd', 
                                borderRadius: '4px',
                                width: '80px'
                            }}
                        />
                    </div>
                    
                    <div style={{ marginTop: '20px' }}>
                        <button
                            onClick={() => testConnection()}
                            disabled={!serverIP || connectionStatus === 'testing'}
                            style={{
                                padding: '10px 15px',
                                backgroundColor: '#2196F3',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer'
                            }}
                        >
                            اختبار الاتصال
                        </button>
                    </div>
                </div>
            </div>

            {/* Auto Discovery */}
            <div style={{ backgroundColor: 'white', padding: '15px', borderRadius: '6px' }}>
                <h4>البحث التلقائي عن الخوادم</h4>
                
                <button
                    onClick={discoverServers}
                    disabled={isScanning}
                    style={{
                        padding: '10px 15px',
                        backgroundColor: '#4CAF50',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        marginBottom: '15px'
                    }}
                >
                    {isScanning ? '🔍 جاري البحث...' : '🔍 البحث عن خوادم'}
                </button>

                {discoveredServers.length > 0 && (
                    <div>
                        <h5>الخوادم المكتشفة:</h5>
                        {discoveredServers.map((server, index) => (
                            <div
                                key={index}
                                style={{
                                    padding: '10px',
                                    backgroundColor: '#e3f2fd',
                                    borderRadius: '4px',
                                    marginBottom: '5px',
                                    cursor: 'pointer',
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center'
                                }}
                                onClick={() => selectServer(server)}
                            >
                                <div>
                                    <strong>{server.ip}</strong>
                                    <span style={{ marginRight: '10px', fontSize: '12px', color: '#666' }}>
                                        ({server.responseTime}ms)
                                    </span>
                                </div>
                                <button
                                    style={{
                                        padding: '5px 10px',
                                        backgroundColor: '#2196F3',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '3px',
                                        fontSize: '12px'
                                    }}
                                >
                                    استخدام
                                </button>
                            </div>
                        ))}
                    </div>
                )}

                {isScanning && (
                    <div style={{ textAlign: 'center', color: '#666' }}>
                        🔍 جاري البحث في الشبكة المحلية...
                    </div>
                )}
            </div>

            {/* Connection Help */}
            <div style={{ 
                backgroundColor: '#fff3e0', 
                padding: '15px', 
                borderRadius: '6px', 
                marginTop: '15px',
                fontSize: '12px',
                color: '#e65100'
            }}>
                <strong>💡 نصائح الاتصال:</strong>
                <ul style={{ margin: '5px 0 0 20px' }}>
                    <li>تأكد أن الخادم يعمل على الجهاز المضيف</li>
                    <li>تأكد أن جميع الأجهزة متصلة بنفس الشبكة</li>
                    <li>أضف استثناء للمنفذ 8000 في جدار الحماية</li>
                    <li>جرب عنوان IP الظاهر في سجلات الخادم</li>
                </ul>
            </div>
        </div>
    );
};

export default ServerConnectionSettings;
