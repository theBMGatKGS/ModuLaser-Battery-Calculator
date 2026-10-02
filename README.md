# ModuLaser Battery Calculator — Desktop App (Electron)

Wraps the calculator in a real desktop window for Windows and macOS, with
its own icon, taskbar/dock entry, and Start Menu / Applications shortcut.

## Recent improvements (01.05)

Web / PWA: https://thebmgatkgs.github.io/ModuLaser-Battery-Calculator/

Calculator revision **01.05.009_261002** — GitHub release **[v01.05.009](https://github.com/theBMGatKGS/ModuLaser-Battery-Calculator/releases/tag/v01.05.009)** (same number; date suffix `_261002` is in-app only).

Going forward, desktop release tags match the calculator revision exactly: `vMM.mm.rrr` ↔ `MM.mm.rrr` (older `v1.0.x` tags remain as history).

- **Dropdown scroll + keyboard** (01.05.009) — tall calc-select menus (Fan Speed, Addresses, …) keep open while scrollbar-dragging or wheel-scrolling; Arrow/Page/Home/End navigate, Enter commits
- **Sheet header layout** (01.05.008) — Power Supply Name/Location on a full row above Design Basis + Ambient Temp; Design Basis wide enough for the longest preset label without truncation
- **Dropdown contrast** (01.05.007) — custom white-on-black listboxes for Addresses, Module Types, Design Basis, Ambient Temp, Fan Speed, and other selects (native option popups could not be styled reliably in Chromium after 01.05.006)
- **Import Calc** — replace or merge saved `.html` files (collision prompts + older-revision warning)
- **Clear** — this sheet or entire file (keep/clear header)
- **Confirm defaults** — clear blue needs-entry on header + current-sheet factory defaults
- **Blue needs-entry** highlighting (Date excluded)
- **How Do I…** searchable help in toolbar and Help overlay
- Quick Start steps 13–16 documenting the above

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
npm run build:win     # → dist/ModuLaser.Battery.Calculator.Setup.01.05.009.exe
npm run build:mac     # → dist/ModuLaser.Battery.Calculator.Setup.01.05.009.dmg
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
currently Revision `01.05.009_261002`, authored by The BMG. These are set
as constants at the top of `main.js` (`APP_REVISION`, `APP_AUTHOR`) —
update them there whenever you cut a new revision, and keep them matching
the calculator's own title-bar Revision/Date cells and its "About" section
in the Help overlay, so all three deliverables stay consistent.

GitHub releases use the same number as the calculator revision: tag/title
`v01.05.009` for calculator `01.05.009` (the `_YYMMDD` date stays in-app /
`package.json` `revision` only). The npm/`electron-builder` `version` field
stays plain semver without leading zeros (e.g. `1.5.7`) so NSIS accepts it;
installer filenames are forced to `…Setup.01.05.009.exe` via `artifactName`.

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
