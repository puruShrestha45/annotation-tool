const { app, BrowserWindow, dialog, ipcMain, session } = require("electron");
const path = require("path");
const { readdir, unlink } = require("node:fs/promises");
const fs = require("fs");
const Papa = require('papaparse');

try {
  require("electron-reloader")(module);
} catch (_) {}


function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 850,
    webPreferences: {
      nodeIntegration: true,
      preload: path.join(__dirname, "preload.js"),
      enableRemoteModule: true,
      nodeIntegrationInWorker: true,
      nodeIntegrationInSubFrames: true,
    },
  });

  ipcMain.handle("dialog:openDirectory", async () => {
    const { canceled, filePaths } = await dialog.showOpenDialog(win, {
      properties: ["openDirectory"],
    });

    if (canceled) {
      return;
    } else {
      folderPath = filePaths[0];

      const folderName = path.basename(folderPath)
      const csvPath = path.join(folderPath, folderName + '.csv')
      let csvData;
      //read csv
      // Read CSV file

      // Get list of images in the directory
      imageList = await fs.promises.readdir(folderPath);
      imageList = imageList.filter(
        (file) => file.endsWith(".jpg") || file.endsWith(".png")
      );

      try {
        const data = await fs.promises.readFile(csvPath, 'utf8');
        // Parse the CSV data using PapaParse
        Papa.parse(data, {
          header: true, // Treat the first row as header
          skipEmptyLines: true,
          dynamicTyping: false,
          transform: (value, header) => {
            if (header === 'isInvalid' || header === 'isNepali') {
              return value === 'true';
            }else if (header === 'text') {
              return value || ''; 
            }
            return value;
          },
          complete: (results) => {
            loadedCSVData = results.data
          },
        })
      }
      catch (err) {
        console.error('Error reading the CSV file:', err);
        // Create default dataset
        loadedCSVData = imageList.map(image => ({
          image,
          text: '',
          isNepali: false,
          isInvalid: false,
        }));
      }

      return { folderPath, folderName, imageList, loadedCSVData, csvPath };
    }
  });


  ipcMain.handle("checkFileExists", async (event, filePath) => {
    return fs.existsSync(filePath);
  });

  ipcMain.handle("saveCSV", async (event, csvPath, csvData) => {
    const data = Papa.unparse(csvData);
    fs.writeFile(csvPath, data, (err) => {
      if (err) {
        console.error('Error writing CSV file:', err);
      } else {
        console.log("saved to ", csvPath);
      }
    });
  });

  ipcMain.handle("deleteImage", async (event, imageDir, imageName) => {
    const imgPath = path.join(imageDir, imageName)
    console.log(imgPath);
    backupImage(imageDir, imageName);
    unlink(imgPath, (err) => {
      if (err) {
        console.log(err);
        throw err;
      }
    });
  });


  win.loadFile("src/index.html");
}

app.whenReady().then(() => {
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
