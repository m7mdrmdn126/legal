const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  getServerConfig: () => ipcRenderer.invoke('get-server-config'),
  getAppConfig: () => ipcRenderer.invoke('get-app-config')
});
