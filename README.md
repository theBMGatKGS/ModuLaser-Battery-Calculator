# ModuLaser Battery Calculator — Desktop App (Electron)

Wraps the calculator in a real desktop window for Windows and macOS, with
its own icon, taskbar/dock entry, and Start Menu / Applications shortcut.

## What's new in 02.00.004 (local, pending QA)
- **Valid defaults are no longer flagged.** Design Basis, Standby (h), Alarm (min), Ambient Temp., Module Type, Power, Addressing, supply mode, NFPA 72 edition and margin keep their defaults without amber and no longer make a sheet *Needs entry*. Only empty required fields (Power Supply Name, Location, module Address, Zone, Fan Speed…) are amber. **Edit → Confirm defaults** is kept but no longer needed (harmless).
- **New sheets start with no modules.** An empty sheet shows a guide: **Import .pl…** (from PipeCAD) or **+ Add Display / + Add Detector** (by hand). The last module can be removed (the guide returns). An empty sheet is *Needs entry* / INCOMPLETE.
- **Standby (h) / Alarm (min)** no longer cut values off on screens ≤ 1366 px (boxes keep 92 px; the settings row wraps).
- **Addressing per mode.** Networked sheets share an address pool per SenseNET network (1–127 on each network). A Standalone sheet is its own pool (1–9, now scoped per sheet instead of per cluster) and may reuse addresses from other sheets without a Validation Error; duplicates inside one Standalone sheet are still flagged.
- **Mixed Networked + Standalone** projects show a *Mixed addressing* banner: **Make all Networked…** / **Make all Standalone…**, confirm first, optional **Also re-address all modules** (Networked 1…N across sheets in order; Standalone 1…n per sheet; module order, ribbon/AUX/cluster assignments unchanged).
- **Imports keep addresses** (Import Calc, Import project, .pl re-import) and list any per-mode conflicts right after import.
- **SenseNET networks (up to 127 modules each).** Each Networked sheet has a SenseNET network number (selector on the Addressing row, SN1/SN2 tag in the sidebar, *Networked · SenseNET n* in print/Word/Excel settings, saved per sheet; older files default to network 1). Past 127 modules, whole sheets (last in sheet order first) move to SenseNET 2, 3… and are addressed from 1, and you're told a new network was added and the design must include its infrastructure. A sheet never spans networks. Duplicate addresses are checked per network. Networked re-address: 1–127 on SenseNET 1 in sheet order, then 1… on SenseNET 2. Imports keep networks; an import over 127 offers *Move overflow to a new SenseNET network*. Shared `modulaser-project.js` unchanged (the network rides in the calculator state inside `.mlproj.json`).
- **Address change log + Undo (QA F1/F2).** Unify / re-address, SenseNET network moves and Standalone clears are written to **Edit → Address change log…** (saved with the project and in `.mlproj.json` calculator state) with each module's address and network before and after, and can be undone in one step (Undo bar above the sheet, or Ctrl+Z outside text fields). Make all Standalone lists the addresses above 9 it will clear before you confirm and reports them afterwards; switching one sheet to Standalone does the same. Undo is disarmed by the next manual address/mode/network edit and Ctrl+Z is ignored while any field or dropdown has focus. Automatic SenseNET moves happen only when a network's count rises past 127; while a network is over 127 (e.g. after undoing a move) the flag stays and a **Move overflow to SenseNET n** banner offers the move. Clear file clears the address log.
- Calculation math, `masd-engine.js` 1.0.0 and `modulaser-project.js` 1.3.0 unchanged (no engine bump).
- QA: pending (brief `qa/brief-02.00.004.md`).

## What's new in 02.00.003
- **Needs-entry fields are visible again.** A sheet marked *Needs entry* (amber dot) now outlines every field that needs entry in **amber** (2px), including the custom dropdowns. In 02.00.000–02.00.002 the old 1px soft-blue outline blended into the dark theme, so nothing appeared highlighted.
- **Show next ›** in the Live Results panel scrolls to and focuses each needs-entry field in turn.
- Print label grey darkened `#747574` → `#6b6c6b` for WCAG AA contrast.
- **Module table fits without truncation or wrap:** Module Type shows DISP-MIN / DISP-STD / DISP-CMD / DETECTOR, Cluster shows the 2-digit number (01), Power shows Own circuit or **Ribbon Path**. Print/Export and Word module tables add Model, Cluster and Power with the same labels.
- QA 2026-10-14 final: Calculator d34555b / Toolbox 209f54f GO.
- QA 2026-10-14: Calculator 43d5a23 / Toolbox 7d1cfec GO-conditional; Word header wrap fixed in final (see [RELEASE_NOTES.md](RELEASE_NOTES.md)).
- Already-saved .html files keep their own code; open them in 02.00.003 via **File → Import Calc** to get these fixes.
- Calculation math unchanged. QA brief: needs-entry 2026-10-14 (see [RELEASE_NOTES.md](RELEASE_NOTES.md)).

## What's new in 02.00.002
- **Shared MASD engine 1.0.0** (`masd-engine.js`) — byte-identical with the **MASD Engineering Toolbox 00.01.000**, which embeds this calculator; results unchanged.
- **Harmonization rule:** any engine change bumps the engine version and both apps' revisions with matching notes.
- Project file (`modulaser-project.js` 1.3.0, shared with the Commissioning Report and Toolbox): SHA-256 design/site hashes, pass-through of field changes, approvals, Toolbox config and Performance Criteria.
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
- Import Calc (replace/merge), Clear (sheet or file), Confirm defaults (no longer needed since 02.00.004), needs-entry highlighting (amber since 02.00.003; empty required fields only since 02.00.004)
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
npm run build:win     # → dist/ModuLaser.Battery.Calculator.Setup.02.00.004.exe
npm run build:mac     # → dist/ModuLaser.Battery.Calculator.Setup.02.00.004.dmg
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
currently Revision `02.00.004_261015`, authored by The BMG. These are set
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
