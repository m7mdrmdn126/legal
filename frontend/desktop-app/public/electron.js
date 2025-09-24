const { app, BrowserWindow, Menu, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const isDev = require('electron-is-dev');

let mainWindow;
let cachedConfig = null;

// Configuration functions
function loadConfiguration() {
  // Return cached config if available
  if (cachedConfig) {
    return cachedConfig;
  }
  try {
    // Multiple possible configuration file locations
    const configPaths = [];
    
    if (isDev) {
      // Development paths
      configPaths.push(path.join(__dirname, '..', '.env'));
      configPaths.push(path.join(process.cwd(), '.env'));
    } else {
      // Production paths
      configPaths.push(path.join(process.resourcesPath, '.env'));
      configPaths.push(path.join(path.dirname(process.execPath), '.env'));
      configPaths.push(path.join(app.getPath('userData'), '.env'));
    }
    
    let configContent = null;
    let usedPath = null;
    
    // Try to find and read configuration file
    for (const configPath of configPaths) {
      if (fs.existsSync(configPath)) {
        try {
          configContent = fs.readFileSync(configPath, 'utf8');
          usedPath = configPath;
          if (isDev) {
            console.log('Configuration loaded from:', configPath);
          }
          break;
        } catch (error) {
          if (isDev) {
            console.warn('Could not read config file:', configPath, error.message);
          }
        }
      }
    }
    
    if (configContent) {
      const config = {};
      
      configContent.split('\n').forEach(line => {
        // Skip comments and empty lines
        line = line.trim();
        if (line && !line.startsWith('#')) {
          const equalIndex = line.indexOf('=');
          if (equalIndex > 0) {
            const key = line.substring(0, equalIndex).trim();
            const value = line.substring(equalIndex + 1).trim();
            config[key] = value;
          }
        }
      });
      
      cachedConfig = {
        serverIp: config.SERVER_IP || 'localhost',
        serverPort: config.SERVER_PORT || '8000',
        appName: config.APP_NAME || 'Legal Cases Management',
        autoConnect: config.AUTO_CONNECT !== 'false', // Default to true
        configPath: usedPath
      };
      
      return cachedConfig;
    } else {
      // Create default configuration file in user data directory
      const defaultConfigPath = path.join(app.getPath('userData'), '.env');
      const defaultConfig = `# Legal Cases Management System - Client Configuration
# Edit this file to configure the server connection

# Server Configuration
SERVER_IP=localhost
SERVER_PORT=8000

# Application Settings
APP_NAME=Legal Cases Management
APP_VERSION=1.0.0

# Auto-connect settings
AUTO_CONNECT=true
SHOW_SERVER_CONFIG=true`;

      try {
        fs.writeFileSync(defaultConfigPath, defaultConfig, 'utf8');
        if (isDev) {
          console.log('Created default configuration file:', defaultConfigPath);
        }
      } catch (error) {
        if (isDev) {
          console.warn('Could not create default configuration file:', error.message);
        }
      }
    }
  } catch (error) {
    console.error('Error loading configuration:', error);
  }
  
  // Default configuration
  cachedConfig = {
    serverIp: 'localhost',
    serverPort: '8000',
    appName: 'Legal Cases Management',
    autoConnect: true,
    configPath: null
  };
  
  return cachedConfig;
}

function getServerUrl() {
  const config = loadConfiguration();
  return `http://${config.serverIp}:${config.serverPort}/api/v1`;
}

// IPC handlers for renderer process
ipcMain.handle('get-server-config', () => {
  return getServerUrl();
});

ipcMain.handle('get-app-config', () => {
  return loadConfiguration();
});

function createWindow() {
  const config = loadConfiguration();
  
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    title: config.appName,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      webSecurity: true,
      preload: path.join(__dirname, 'preload.js'),
      // Fix for SharedImageManager errors
      offscreen: false,
      backgroundThrottling: false
    },
    icon: path.join(__dirname, 'favicon.ico'),
    show: false,
    titleBarStyle: 'default'
  });

  // Load the app
  const startUrl = isDev 
    ? 'http://localhost:3000' 
    : `file://${path.join(__dirname, '../build/index.html')}`;
  
  mainWindow.loadURL(startUrl);

  // Show window when ready to prevent visual flash
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    
    // Focus on window (in case of reopening)
    if (isDev) {
      mainWindow.webContents.openDevTools();
    }
  });

  // Emitted when the window is closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    require('electron').shell.openExternal(url);
    return { action: 'deny' };
  });
}

// Disable hardware acceleration to fix SharedImageManager errors
app.disableHardwareAcceleration();

// Add command line switches to reduce warnings
app.commandLine.appendSwitch('--disable-web-security');
app.commandLine.appendSwitch('--disable-features', 'VizDisplayCompositor');

// This method will be called when Electron has finished initialization
app.whenReady().then(() => {
  createWindow();

  // Set application menu
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Exit',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
});

// Quit when all windows are closed
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// Security: Prevent new window creation
app.on('web-contents-created', (event, contents) => {
  contents.on('new-window', (event, navigationUrl) => {
    event.preventDefault();
    require('electron').shell.openExternal(navigationUrl);
  });
});
