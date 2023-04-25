const { contextBridge, ipcRenderer } = require('electron')

// contextBridge.exposeInMainWorld("api", RendererApi);
contextBridge.exposeInMainWorld('myAPI', {
  selectFolder: () => ipcRenderer.invoke('dialog:openDirectory'),
  checkFileExists: (filePath) => ipcRenderer.invoke('checkFileExists', filePath),
  deleteImage: (imgPath) => ipcRenderer.invoke('deleteImage', imgPath),
  saveCSV: (csvPath, csvData) => ipcRenderer.invoke('saveCSV', csvPath, csvData),
  saveCrop: (imgPath, crop) => ipcRenderer.invoke('saveCrop', imgPath, crop),
  clearCache: () => ipcRenderer.invoke('clearCache'),
})
