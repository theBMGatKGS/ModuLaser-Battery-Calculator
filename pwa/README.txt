ModuLaser Battery Calculator — Progressive Web App
===================================================

WHAT'S IN THIS FOLDER
  index.html                  The calculator (same features as the standalone file)
  manifest.json               App identity: name, icons, colors, standalone window
  sw.js                       Service worker: offline caching (app + Excel library + fonts)
  icons/                      App icons (192, 512, and maskable 512)

HOW TO DEPLOY (pick one)

  GitHub Pages (free)
    1. Create a repository and upload this folder's contents to its root.
    2. Repo Settings -> Pages -> deploy from the main branch, root folder.
    3. Your app is at https://<username>.github.io/<repo>/

  Netlify (free)
    1. netlify.com -> "Add new site" -> "Deploy manually"
    2. Drag this whole folder onto the page. Done.

  Internal web server
    Copy the folder to any HTTPS-served path. All paths are relative,
    so it works from a subdirectory (e.g. https://intranet/tools/modulaser/).

  NOTE: HTTPS is required for install/offline (localhost is exempt for testing).
  Opening index.html directly from disk still works as a normal page —
  the PWA features simply stay dormant.

INSTALLING
  Desktop Chrome/Edge: install icon in the address bar -> "Install".
  Android: browser menu -> "Add to Home screen" / "Install app".
  iOS Safari: Share -> "Add to Home Screen".

OFFLINE BEHAVIOR
  After the first online visit, the app, fonts, and the Excel export
  library are cached, so everything works with no connection.

AUTOSAVE IN PWA MODE
  Autosave data lives in the browser's storage for the hosted URL, so it
  follows the app rather than a downloaded file. "Save As..." still
  downloads self-contained HTML snapshot copies whenever you want a
  file to archive or share.

UPDATING THE APP
  Replace index.html on the server and bump CACHE_VERSION in sw.js
  (v1 -> v2). Users get the new version on their next visit.
