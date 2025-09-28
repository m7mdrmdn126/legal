// Debug script to test Electron app loading
const { app, BrowserWindow } = require('electron');
const path = require('path');
const fs = require('fs');

let mainWindow;

function createDebugWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      webSecurity: false
    },
    show: true
  });

  // Test different loading paths
  const buildPath = path.join(__dirname, 'build', 'index.html');
  console.log('Build path exists:', fs.existsSync(buildPath));
  console.log('Build path:', buildPath);
  
  if (fs.existsSync(buildPath)) {
    const fileUrl = `file://${buildPath}`;
    console.log('Loading URL:', fileUrl);
    mainWindow.loadURL(fileUrl);
  } else {
    console.error('Build directory not found!');
    // Load a simple HTML for testing
    mainWindow.loadURL('data:text/html,<h1>Build directory not found</h1><p>Path: ' + buildPath + '</p>');
  }

  // Open DevTools for debugging
  mainWindow.webContents.openDevTools();
  
  // Log all console messages from renderer
  mainWindow.webContents.on('console-message', (event, level, message, line, sourceId) => {
    console.log(`[${level}] ${message} (${sourceId}:${line})`);
  });

  // Log load failures
  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription, validatedURL) => {
    console.error('Load failed:', errorCode, errorDescription, validatedURL);
  });
}

app.whenReady().then(createDebugWindow);

app.on('window-all-closed', () => {
  app.quit();
});
