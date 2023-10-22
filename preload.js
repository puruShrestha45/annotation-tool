const { contextBridge, ipcRenderer } = require('electron')

// contextBridge.exposeInMainWorld("api", RendererApi);
contextBridge.exposeInMainWorld('myAPI', {
  selectFolder: () => ipcRenderer.invoke('dialog:openDirectory'),
  checkFileExists: (filePath) => ipcRenderer.invoke('checkFileExists', filePath),
  saveCSV: (csvPath, csvData) => ipcRenderer.invoke('saveCSV', csvPath, csvData),
})
