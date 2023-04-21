const { app, BrowserWindow, dialog, ipcMain } = require("electron");
const path = require("path");
const { readdir, unlink } = require("node:fs/promises");
const dfd = require("danfojs-node");
const fs = require("fs");

try {
  require("electron-reloader")(module);
} catch (_) {}

function createWindow() {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
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
      // get list of images in the directory
      let imageList = await readdir(folderPath);

      imageList = imageList.filter(
        (file) => file.endsWith(".jpg") || file.endsWith(".png")
      );

      return { folderPath, imageList };
    }
  });

  //return images in the directory
  ipcMain.handle("getImages", async (event, dir) => {
    let images = [];
    images = readdir(dir)
      .then((files) => {
        images = files.filter(
          (file) => file.endsWith(".jpg") || file.endsWith(".png")
        );
        return images;
      })
      .catch((err) => {
        console.log(err);
      });
    return images;
  });

  ipcMain.handle("saveCSV", async (event, csvPath, csvData) => {
    let df = new dfd.DataFrame(csvData);
    dfd.toCSV(df, { filePath: csvPath });
  });

  ipcMain.handle("deleteImage", async (event, imgPath) => {
    unlink(imgPath, (err) => {
      if (err) {
        console.log(err);
        throw err;
      }
    });
  });

  win.loadFile("index.html");
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
