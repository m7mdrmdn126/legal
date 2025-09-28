const { app, BrowserWindow } = require('electron');
const path = require('path');
const fs = require('fs');

let mainWindow;

function createDebugWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: false,
      allowRunningInsecureContent: true,
      preload: path.join(__dirname, 'public/preload.js')
    },
    show: false
  });

  // Log all paths and environment info
  console.log('=== DEBUG INFORMATION ===');
  console.log('Process platform:', process.platform);
  console.log('Process arch:', process.arch);
  console.log('App path:', app.getAppPath());
  console.log('Process resourcesPath:', process.resourcesPath);
  console.log('Process execPath:', process.execPath);
  console.log('__dirname:', __dirname);
  console.log('Process cwd:', process.cwd());
  
  // Check if build files exist
  const buildPath = path.join(__dirname, 'build');
  const indexPath = path.join(buildPath, 'index.html');
  
  console.log('Build path exists:', fs.existsSync(buildPath));
  console.log('Index.html exists:', fs.existsSync(indexPath));
  
  if (fs.existsSync(buildPath)) {
    console.log('Build directory contents:', fs.readdirSync(buildPath));
  }
  
  // Try to load the app
  const startUrl = `file://${indexPath}`;
  console.log('Loading URL:', startUrl);
  
  mainWindow.loadURL(startUrl);
  
  // Always show dev tools for debugging
  mainWindow.webContents.openDevTools();
  
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });
  
  // Log all console messages from renderer
  mainWindow.webContents.on('console-message', (event, level, message, line, sourceId) => {
    console.log(`[RENDERER ${level.toUpperCase()}]`, message);
    if (line) console.log(`  at ${sourceId}:${line}`);
  });
  
  // Log navigation events
  mainWindow.webContents.on('did-start-loading', () => {
    console.log('Started loading');
  });
  
  mainWindow.webContents.on('did-stop-loading', () => {
    console.log('Stopped loading');
  });
  
  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription, validatedURL) => {
    console.error('Failed to load:', errorCode, errorDescription, validatedURL);
  });
  
  mainWindow.webContents.on('did-finish-load', () => {
    console.log('Finished loading');
  });
}

app.whenReady().then(() => {
  createDebugWindow();
});

app.on('window-all-closed', () => {
  app.quit();
});
