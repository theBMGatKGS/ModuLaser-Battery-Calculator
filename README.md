# ModuLaser Battery Calculator — Desktop App (Electron)

Wraps the calculator in a real desktop window for Windows and macOS, with
its own icon, taskbar/dock entry, and Start Menu / Applications shortcut.

## What's new in 02.00.000

Web / PWA: https://thebmgatkgs.github.io/ModuLaser-Battery-Calculator/

Calculator revision **02.00.000_261013** (desktop installer `ModuLaser.Battery.Calculator.Setup.02.00.000.exe`; release tag `v02.00.000` when published). 02.00.000 folds in the unreleased 01.06.000 work. **Calculation math is unchanged** from 01.05.009.

- **New layout** — PipeCAD dark theme; menu bar (File / Edit / View / Help) + quick row (☰ sidebar, Import .pl, + Add Location, Save As…, Print, Auto-Save, ◧ results); collapsible **Project Settings** bar with a one-line summary and per-sheet override badges; **sheet sidebar** grouped by Area/Group with status dots (complete / needs entry / error / overridden) and + Add power supply; compact module table with n/16 zone counters; pinned **live results** panel (required Ah vs battery vs 65 Ah, PASS / FAIL / INCOMPLETE, load breakdown, clusters, validation messages). Panels collapse on narrow screens.
- **Print / Export** (File → Print / Export…, Print, Ctrl+P) — live 8.5 × 11 preview; **PDF**, **Word (.docx)**, **HTML** and **Excel** built offline (no CDN); detail levels **Summary / Standard / Full** (Full adds calculation appendix pages: formula, values substituted, result, reference). Project summary page + one letter page per PSU with capacity gauge, PASS/FAIL stamp, cluster diagram, module table, settings and BOM. In the desktop app PDF is saved directly via `printToPDF`.
- **Excel** — **CAD Schedule** sheet (compact per-PSU tables, thin borders, fixed widths, no merged cells/fills, for pasting into AutoCAD) + **Detail** sheet that follows the detail level with outline row groups.
- **Import PipeCAD .pl** wizard (from 01.06.000) — battery settings first, multi-file pick with Area/Group selection, 16-character rename table, power-supply assignment (≥1 per Area/Group, none across, max 4 detectors + 1 display, ≤ 65 Ah) with an Unassigned tray, Pack into fewest, and blocked Create sheets until assigned.
- **Linked .pl files** (from 01.06.000) — SHA-256 + per-device fingerprints, Check link, change banner, diff and safe re-import.
- **Help** rewritten: Quick Start, How Do I…, FAQ and revision log cover the new layout, Print / Export, detail levels and the CAD paste tip.

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
