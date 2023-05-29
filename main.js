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

      const folderName = path.basename(folderPath)
      const csvPath = path.join(folderPath, folderName+'.csv')

      // get list of images in the directory
      let imageList = await readdir(folderPath);

      imageList = imageList.filter(
        (file) => file.endsWith(".jpg") || file.endsWith(".png")
      );

      return { folderPath, folderName, imageList, csvPath };
    }
  });

  ipcMain.handle("checkFileExists", async (event, filePath) => {
    return fs.existsSync(filePath);
  });

  ipcMain.handle("saveCSV", async (event, csvPath, csvData) => {
    let df = new dfd.DataFrame(csvData);
    dfd.toCSV(df, { filePath: csvPath });
    console.log("saved to ", csvPath);
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

  ipcMain.handle("saveCrop", async (event, imageDir, imageName, cropData) => {
    const imagePath = path.join(imageDir, imageName)
    const image = sharp(imagePath);


    // save original image as a backup. store it in backup folder
    backupImage(imageDir, imageName);

    image
      .extract({
        left: cropData.x,
        top: cropData.y,
        width: cropData.width,
        height: cropData.height,
      })
      .toBuffer()
      .then(function (data) {
        fs.writeFileSync(imagePath, data);
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

const backupImage = (imgDir, imageName) => {
  const imgPath = path.join(imgDir, imageName)
  const backupFolder = path.join(imgDir, "backup")

  if (!fs.existsSync(imgPath)) {
    console.log("file does not exist");
    return;
  }

  if (!fs.existsSync(backupFolder)) {
    fs.mkdirSync(backupFolder);
  }

  if (!fs.existsSync(path.join(backupFolder, imageName))) {
    fs.copyFile(imgPath, path.join(backupFolder, imageName), function (err) {
      if (err) {
        throw err;
      }
    });
  }
}
