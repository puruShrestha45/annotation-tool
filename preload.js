const { contextBridge, ipcRenderer } = require('electron')

// contextBridge.exposeInMainWorld("api", RendererApi);
contextBridge.exposeInMainWorld('myAPI', {
  selectFolder: () => ipcRenderer.invoke('dialog:openDirectory'),
  checkFileExists: (filePath) => ipcRenderer.invoke('checkFileExists', filePath),
  deleteImage: (imageDir, imageName) => ipcRenderer.invoke('deleteImage', imageDir, imageName),
  saveCSV: (csvPath, csvData) => ipcRenderer.invoke('saveCSV', csvPath, csvData),
  saveCrop: (imageDir, imageName, crop) => ipcRenderer.invoke('saveCrop', imageDir, imageName, crop),
  clearCache: () => ipcRenderer.invoke('clearCache'),
})
