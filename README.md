# ModuLaser Battery Calculator — Desktop App (Electron)

Wraps the calculator in a real desktop window for Windows and macOS, with
its own icon, taskbar/dock entry, and Start Menu / Applications shortcut.

## What's new in 02.00.002
- **Shared MASD engine 1.0.0** (`masd-engine.js`) — byte-identical with the **MASD Engineering Toolbox 00.01.000**, which embeds this calculator; results unchanged.
- **Harmonization rule:** any engine change bumps the engine version and both apps' revisions with matching notes.
- Project file (`modulaser-project.js` 1.2.0, shared with the Commissioning Report and Toolbox): SHA-256 design/site hashes, pass-through of field changes, approvals, Toolbox config and Performance Criteria.
- QA audit 2026-10-13 ([issue #1](https://github.com/theBMGatKGS/ModuLaser-Battery-Calculator/issues/1)): see [RELEASE_NOTES.md](RELEASE_NOTES.md).

## What's new in 02.00.000

- **Web / PWA (live):** https://thebmgatkgs.github.io/ModuLaser-Battery-Calculator/ — open in a browser, or install it (Chrome/Edge install icon; iPhone/iPad Safari → Share → Add to Home Screen). Works offline after the first visit.
- **Windows installer:** [ModuLaser.Battery.Calculator.Setup.02.00.000.exe](https://github.com/theBMGatKGS/ModuLaser-Battery-Calculator/releases/download/v02.00.000/ModuLaser.Battery.Calculator.Setup.02.00.000.exe) — release [v02.00.000](https://github.com/theBMGatKGS/ModuLaser-Battery-Calculator/releases/tag/v02.00.000) (x64 NSIS, unsigned; SmartScreen may prompt).

Calculator revision **02.00.000_261013**. Major version 02.00 folds in the unreleased 01.06.000 work. **Calculation math is unchanged** — the same scenarios give identical Ah and BOM results to 01.05.009 (verified by the automated test suite).

### New layout
- **PipeCAD dark theme** on screen; printouts keep the KGS print palette.
- **Left sidebar** — power supply sheets grouped by Area/Group, each with a status dot (complete / needs entry / error / overridden), plus **+ Add power supply**.
- **Collapsible Project Settings bar** — one-line summary when collapsed; shows the Design Basis, standby/alarm and other sheet settings most sheets use, with an **override badge** on any sheet that differs (it is a summary, not a separate master setting).
- **Pinned live results panel** — required Ah vs the selected battery vs the 65 Ah limit, PASS / FAIL / INCOMPLETE, load breakdown, clusters and the sheet's validation messages.
- **Compact inline-edit module table** — every zone name has a live **n/16 character counter** (turns red over 16) and the ModuLaser 16-character display warning; the Zone column fits a full 16-character name and its counter.
- Panels collapse on narrow screens; the View menu toggles them.

### Menus and quick actions
- **File / Edit / View / Help** menu bar (keyboard accessible, white-on-black).
- **Quick-action row:** ☰ sidebar, Import .pl, + Add Location, Save As…, Print, Auto-Save indicator, ◧ results panel.

### PipeCAD .pl import wizard
1. **Battery settings first** (Design Basis, standby/alarm, temperature, battery) so every created sheet starts correct.
2. **Multi-file pick** — choose one or more `.pl` files, select which **Area/Groups** to import; metric drawings are converted to feet.
3. **Rename table** — name pattern with `{project} {file} {area} {name} {##}` (remembered), live **16-character display limit** counter, short-name suggestions and duplicate flags.
4. **Power supply assignment** — rules enforced: max **4 detectors + 1 display** per PSU; **≤ 65 Ah including the display**; one or more PSU per Area/Group; **no sharing across Area/Groups**. Seeded from **PSU positions in the file**, otherwise **3 ft plan-view clusters**; anything left goes to a per-Area/Group **Unassigned tray** (drag, Move to…, + Add power supply, or **Pack into fewest**). Create sheets stays blocked until the tray is empty.
- **Display `partNumber` mapping:** `0` = Standard Display (FHSD8310), `1` = Minimum Display (FHSD8300), `2` = Command Display (FHSD8320).

### Linked .pl tracking
- Each import saves the file name, size, date, SHA-256 and per-device fingerprints in the calc. **Check link** detects changes, shows a change banner and a diff, and **re-import** never changes addresses or hand edits without confirmation.

### Print / Export dialog
- File → Print / Export…, Print in the quick row, or **Ctrl+P**. One dialog with a **live 8.5 × 11 preview**, sheet scope, summary-page and BOM options, and **PDF**, **Word (.docx)**, **HTML** and **Excel** buttons — all built offline (no CDN). In the desktop app PDF is saved directly; in the browser it goes through the print dialog.
- **Detail levels: Summary / Standard / Full.**
- **Project summary page** — every PSU's Area/Group, required Ah, battery and PASS/FAIL.
- **One-page 8.5 × 11 PSU sheets** in the KGS palette: header, **capacity gauge** (required Ah, selected battery and 65 Ah marks, margin and de-rating shaded), **PASS/FAIL stamp**, **mini cluster diagram** (PSU with detectors and display), module table, settings and BOM.
- **Full-math appendix** pages per PSU: each step shows the **formula, substituted values, result with units and the code reference**.

### Excel export
- **CAD Schedule** tab — compact per-PSU tables (Zone, Type, Fan speed, Address, Standby mA, Alarm mA, footer with Ah / battery / PASS), thin borders, fixed widths, no merged cells or fills, for **copy/paste directly onto 2D CAD drawings**.
- **Detail** tab — follows the chosen detail level with **outline row grouping** (expand/collapse per PSU and per step).

### Help
- **Help, Quick Start, How Do I…, FAQ, tooltips and the Revision Log** fully rewritten for 02.00.000 — new layout, .pl import, Print / Export, detail levels and the CAD paste tip.

### Recent improvements (01.05)
- Dropdown scroll + keyboard navigation (01.05.009)
- Sheet header layout: PS Name/Location on its own row; wider Design Basis (01.05.008)
- White-on-black custom dropdowns (01.05.007)
- Import Calc (replace/merge), Clear (sheet or file), Confirm defaults, blue needs-entry highlighting
- Searchable How Do I… help

Full history: [`CHANGELOG.md`](CHANGELOG.md) and Help → Revision Log in the app.

## One-time setup

1. Install [Node.js](https://nodejs.org) (LTS version) if you don't have it.
2. Open a terminal in this folder and run:
   ```
   npm install
   ```

## Try it without building anything

```
npm start
```
Opens the calculator in an Electron window right away — good for checking
everything works before you build an installer.

## Build an installer

```
npm run build:win     # → dist/ModuLaser.Battery.Calculator.Setup.02.00.000.exe
npm run build:mac     # → dist/ModuLaser.Battery.Calculator.Setup.02.00.000.dmg
npm run build:all     # both, if your machine can build both (see note below)
```

### Important: macOS builds need to run on a Mac

`electron-builder` can build a **Windows** installer from Windows, macOS, or
Linux. But it can **only build a macOS app/.dmg while running on macOS** —
Apple's code-signing tools don't exist anywhere else. So:

- Building on **Windows**: `npm run build:win` works directly.
  `npm run build:mac` will fail — you'd need a Mac (or a free CI service
  like GitHub Actions with a `macos-latest` runner) to produce the .dmg.
- Building on a **Mac**: both `build:win` and `build:mac` work directly.

If you don't have access to a Mac, the easiest free route is a GitHub
Actions workflow that checks out this folder and runs `npm run build:mac`
on a `macos-latest` runner — happy to help set that up if you want it.

## About menu

The app has a Help → About menu item (and on macOS, the standard app menu's
"About ModuLaser Battery Calculator" too) showing the revision and author —
currently Revision `02.00.000_261013`, authored by The BMG. These are set
as constants at the top of `main.js` (`APP_REVISION`, `APP_AUTHOR`) —
update them there whenever you cut a new revision, and keep them matching
the calculator's own title-bar Revision/Date cells and its "About" section
in the Help overlay, so all three deliverables stay consistent.

GitHub releases use the same number as the calculator revision: tag/title
`v02.00.000` for calculator `02.00.000` (the `_YYMMDD` date stays in-app /
`package.json` `revision` only). The npm/`electron-builder` `version` field
stays plain semver without leading zeros (e.g. `1.5.7`) so NSIS accepts it;
installer filenames are forced to `…Setup.02.00.000.exe` via `artifactName`.

### Revision numbering scheme

Format: `MM.mm.rrr_YYMMDD`
- `MM` (major) and `mm` (minor) are set manually — never auto-changed.
- `rrr` is a 3-digit counter, incremented by 1 for each distinct logical
  change made in a chat session, reset to `000` only when `mm` is next
  revised manually.
- `YYMMDD` is the actual calendar date of that change.
- GitHub release tag: `vMM.mm.rrr` (matches the calculator revision;
  supersedes the older separate `v1.0.x` desktop numbering).

The full running changelog lives in the `AMENDMENTS` array inside
`app/modulaser_battery_calculator.html` (near the top of the `<script>`
block) — that's the source of truth; the Electron About dialog just shows
the latest revision and points here for the complete history.

## Updating the calculator itself

Replace `app/modulaser_battery_calculator.html` with the newer version
whenever you get an updated export, then rebuild.

## iOS

Electron cannot produce an iOS app — it's a desktop-only technology
(Windows/macOS/Linux). For iOS, use the PWA version of this calculator
instead: host it (even a free static host like GitHub Pages or Netlify
works), then on the iPhone open it in Safari and use
Share → "Add to Home Screen." That gives a real home-screen icon and a
standalone app-like window, with offline support via the service worker
already built into the PWA package. A true native iOS app (App Store or
sideloaded) would require Xcode, a paid $99/year Apple Developer account,
and a substantially different build — not something this Electron setup
can produce.

## Folder contents

- `main.js` — Electron entry point, opens the calculator in a window
- `app/modulaser_battery_calculator.html` — the calculator itself
- `build/icon.ico` / `icon.icns` / `icon.png` — app icons for Windows/macOS/Linux
- `package.json` — dependencies + electron-builder configuration
