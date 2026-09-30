const { app, BrowserWindow, Menu, dialog } = require('electron');
const path = require('path');

// ---- App identity — keep these in sync with the HTML/PWA "About" section ----
// Format: MM.mm.rrr_YYMMDD (major.minor set manually, revision+date auto-tracked
// per change — see the AMENDMENTS list in app/modulaser_battery_calculator.html
// for the full running changelog, also viewable in-app via Help → About).
const APP_NAME = 'ModuLaser Battery Calculator';
const APP_REVISION = '01.04.005_260810';
const APP_AUTHOR = 'The BMG';

const isMac = process.platform === 'darwin';

function showAboutDialog() {
  dialog.showMessageBox({
    type: 'info',
    title: `About ${APP_NAME}`,
    message: APP_NAME,
    detail: `Revision ${APP_REVISION}\nAuthored by ${APP_AUTHOR}\n\nFull amendment history: Help → About in the app.`,
    buttons: ['OK'],
    icon: path.join(__dirname, 'build', 'icon.png'),
  });
}

function buildMenu() {
  const template = [
    ...(isMac
      ? [{
          label: app.name,
          submenu: [
            { label: `About ${APP_NAME}`, click: showAboutDialog },
            { type: 'separator' },
            { role: 'services' },
            { type: 'separator' },
            { role: 'hide' },
            { role: 'hideOthers' },
            { role: 'unhide' },
            { type: 'separator' },
            { role: 'quit' },
          ],
        }]
      : []),
    {
      label: 'Help',
      submenu: [
        { label: `About ${APP_NAME}`, click: showAboutDialog },
      ],
    },
  ];
  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1440,
    height: 940,
    minWidth: 900,
    minHeight: 600,
    autoHideMenuBar: true, // Windows/Linux: menu bar stays hidden until Alt is pressed, for a cleaner look;
                            // macOS: the app menu bar is separate (always at the top of the screen) and unaffected.
    icon: path.join(__dirname, 'build', 'icon.png'), // used on Windows/Linux window/taskbar icon
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  win.loadFile(path.join(__dirname, 'app', 'modulaser_battery_calculator.html'));

  // Uncomment the next line if you ever need to debug the app with DevTools:
  // win.webContents.openDevTools();
}

app.whenReady().then(() => {
  app.name = APP_NAME;

  // Native macOS "About" panel (Apple menu → About ModuLaser Battery Calculator).
  // On Windows/Linux this call is a no-op — that's why the Help → About menu item
  // above uses a dialog directly, so About works identically on every platform.
  app.setAboutPanelOptions({
    applicationName: APP_NAME,
    applicationVersion: APP_REVISION,
    version: APP_REVISION,
    copyright: `Authored by ${APP_AUTHOR}`,
  });

  buildMenu();
  createWindow();

  app.on('activate', () => {
    // macOS: re-create a window when the dock icon is clicked and no windows are open
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  // On macOS it's common to keep the app running until the user quits explicitly (Cmd+Q)
  if (!isMac) app.quit();
});
