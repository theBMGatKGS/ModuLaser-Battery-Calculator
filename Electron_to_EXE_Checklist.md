# ModuLaser Battery Calculator — Electron → .exe Checklist

Verified against the actual `electron-app` scaffold (package.json, main.js) as of Revision 01.04.005_260810. Every command below is copy-paste exact.

## Before you start

- [ ] **A Windows, macOS, or Linux machine.** The Windows build (`build:win`) can be produced from any of the three — you do *not* need a Windows machine to build the Windows installer.
- [ ] **Node.js (LTS) installed.** Download from [nodejs.org](https://nodejs.org) if you don't have it. This installs `npm` too.
- [ ] **An internet connection**, at least for the one-time dependency install (Electron itself is a ~150–200 MB download).
- [ ] **The `modulaser_calculator_electron.zip` deliverable**, unzipped somewhere convenient.

## Phase 1 — One-time setup

1. [ ] Unzip `modulaser_calculator_electron.zip`. You should see: `main.js`, `package.json`, `app/`, `build/`, `README.md`.
2. [ ] Open a terminal / command prompt **in that unzipped folder** (the one containing `package.json`).
3. [ ] Run:
   ```
   npm install
   ```
   This downloads Electron and electron-builder into a new `node_modules` folder. Takes a few minutes the first time; only needs to be done once (or again if you delete `node_modules`).

## Phase 2 — Sanity-check before building (recommended, optional)

4. [ ] Run:
   ```
   npm start
   ```
   This opens the calculator in a real Electron window immediately, without building anything — confirms the app itself works before you spend time on a full installer build. Close the window when done.

## Phase 3 — Build the Windows installer

5. [ ] Run:
   ```
   npm run build:win
   ```
6. [ ] Wait for it to finish (typically 1–3 minutes). You'll see electron-builder log its packaging steps; a successful run ends without an error and leaves a new `dist/` folder.
7. [ ] Find your installer at:
   ```
   dist/ModuLaser.Battery.Calculator.Setup.01.05.009.exe
   ```
   This is a real **NSIS installer** — not a portable single-file exe. Running it lets the user pick an install location, and it creates a Start Menu shortcut and (optionally) a desktop shortcut, per the `nsis` settings already configured in `package.json`.

## Phase 4 — Test the installer itself

8. [ ] Copy the `.exe` from `dist/` to a machine (or a clean VM) and run it.
9. [ ] **Expect a Windows SmartScreen warning** ("Windows protected your PC") the first time it runs — the installer isn't code-signed, so Windows doesn't yet recognize the publisher. This is normal and doesn't mean anything is broken. Click **More info → Run anyway** to proceed.
   - If you need this warning to *not* appear (e.g. for wider external distribution), that requires purchasing a code-signing certificate and configuring it in `package.json` under `build.win.certificateFile` / `certificatePassword` — a separate, optional step not covered here since it involves a real-world purchase and identity verification process.
10. [ ] Confirm the app installs, launches, and the calculator loads correctly — check **Help → About** in the app menu to confirm it shows the revision you expect (currently `01.04.005_260810`).

## Phase 5 — Distribute

11. [ ] Share the single `.exe` from `dist/` — that's the complete installer; no other files need to travel with it.
12. [ ] Each end user just double-clicks it, gets through the SmartScreen prompt once (Phase 4, step 9), and follows the install wizard.

## When you have a newer calculator version

- [ ] Replace `app/modulaser_battery_calculator.html` with the new export.
- [ ] Update `APP_REVISION` in `main.js` (and `"revision"` in `package.json`) to match.
- [ ] Repeat from Phase 3.

## If something goes wrong

- **`npm install` fails / hangs** — usually a network/proxy issue; retry, or check corporate firewall settings if on a work network.
- **`npm run build:win` fails** — re-run `npm install` first to make sure `node_modules` is intact and up to date, then try again.
- **Building the macOS `.dmg` instead** — use `npm run build:mac`, but note it can *only* run successfully on an actual Mac (Apple's code-signing tools aren't available on Windows/Linux). See the main `README.md` in this same folder for the full explanation and a free CI-based workaround if you don't have Mac access.
