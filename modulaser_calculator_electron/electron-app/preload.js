// Exposes a minimal, safe bridge for Print / Export → PDF in the desktop app.
const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('mlDesktop', {
  printToPDF: (html, suggestedName) => ipcRenderer.invoke('ml-print-pdf', String(html), String(suggestedName || '')),
});
