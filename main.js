const { app, BrowserWindow, dialog, ipcMain, session } = require("electron");
const path = require("path");
const { readdir, unlink } = require("node:fs/promises");
const dfd = require("danfojs-node");
const fs = require("fs");
const sharp = require("sharp");
const { log } = require("console");

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

  ipcMain.handle("checkFileExists", async (event, filePath) => {
    return fs.existsSync(filePath);
  });

  ipcMain.handle("saveCSV", async (event, csvPath, csvData) => {
    let df = new dfd.DataFrame(csvData);
    dfd.toCSV(df, { filePath: csvPath });
  });

  ipcMain.handle("deleteImage", async (event, imgPath) => {
    backupImage(imgPath);
    unlink(imgPath, (err) => {
      if (err) {
        console.log(err);
        throw err;
      }
    });
  });

  ipcMain.handle("saveCrop", async (event, imgPath, cropData) => {
    const image = sharp(imgPath);

    // save original image as a backup. store it in backup folder
    backupImage(imgPath);

    image
      .extract({
        left: cropData.x,
        top: cropData.y,
        width: cropData.width,
        height: cropData.height,
      })
      .toBuffer()
      .then(function (data) {
        fs.writeFileSync(imgPath, data);
        console.log("Image cropped and saved");
      })
      .catch(function (err) {
        console.log(err);
      });
  });

  ipcMain.handle("clearCache", async (event) => {
    console.log("clearing cache");
    // webContents.getFocusedWebContents().reloadIgnoringCache();
    await session.defaultSession.clearStorageData();
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

const backupImage = (imgPath) => {
  let fileName = imgPath.split("/").pop();
  const backupFolder = imgPath.split("/").slice(0, -1).join("/") + "/backup/";

  if (!fs.existsSync(imgPath)) {
    console.log("file does not exist");
    return;
  }

  if (!fs.existsSync(backupFolder)) {
    fs.mkdirSync(backupFolder);
  }

  if (!fs.existsSync(backupFolder + fileName)) {
    fs.copyFile(imgPath, backupFolder + fileName, function (err) {
      if (err) {
        throw err;
      }
    });
  }
}
