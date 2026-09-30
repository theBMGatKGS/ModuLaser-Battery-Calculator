# ModuLaser Battery Calculator

A fire alarm standby battery sizing calculator for the ModuLaser aspirating smoke
detection (ASD) product line on Edwards EST fire alarm platforms — built for
mission-critical / data center fire and life safety design work.

**Current revision:** 01.04.008 — see [CHANGELOG.md](./CHANGELOG.md) for the full history, or open the calculator's own **Help → Revision Log** for the same information in-app.

---

## What it does

Given a network of ModuLaser display and detector modules (addresses, zones, fan
speeds, cluster assignments), the calculator:

- Computes total system current draw and required standby/alarm battery capacity
  per the applicable code or standard.
- Supports **13 Design Basis presets**: NFPA 72 (Standard, Voice, and NFPA 110
  Generator Backup variants), UFC 3-600-01 (Hydro and FA/MNS), AWS, CAN/ULC-S524:2024
  (Standard and Voice), four BS 5839-1 categories, and a fully custom basis —
  each with its own verified code citation and, for BS 5839-1, a genuinely
  different sizing formula (Annex E, with an automatically-determined battery
  de-rating factor).
- Recommends the correct Edwards power supply, enclosure, and battery hardware —
  or, in third-party mode, hands off raw load figures for use with another
  manufacturer's own sizing tool.
- Validates the design as you build it: soft advisory flags (duplicate
  addresses, missing circuit sources, oversized ribbon segments) and hard
  invalid-calculation triggers (missing fan speed or address, battery capacity
  exceeding the largest available unit, AUX circuit overcurrent) that withhold
  hardware recommendations until resolved.
- Supports both **Networked** (network-wide unique addressing, 1–127) and
  **Standalone** (per-cluster addressing, 1–9, for a cluster with no SenseNET
  pathway to the rest of the network) addressing schemes, per sheet.
- Produces a print-ready output tuned to fit one power supply's full calculation
  on a single printed page, with an optional Bill of Materials and an optional
  granular per-module calculation-detail page.
- Includes a built-in 4-section Help menu (How to Use the Calculator, Standards
  and Formulas, FAQs, Revision Log) covering the full workflow and every cited
  formula/standard in detail.

## Deliverables

This repository/branch produces three synced deliverables from one source file:

| Deliverable | What it is | Where |
|---|---|---|
| **Standalone HTML** | One self-contained `.html` file — no install, no server, works offline once downloaded | `modulaser_battery_calculator.html` |
| **PWA** | The same calculator packaged as an installable web app (works offline, "Add to Home Screen" on mobile) | `pwa/` |
| **Electron desktop app** | A Windows/macOS desktop app scaffold, buildable into an installer | `electron-app/` |

See [`electron-app/README.md`](./electron-app/README.md) and
[`electron-app/Electron_to_EXE_Checklist.md`](./electron-app/Electron_to_EXE_Checklist.md)
for building the desktop installer, and [`PAGES_SETUP.md`](./PAGES_SETUP.md) for
publishing the standalone/PWA version live via GitHub Pages.

## Quick start

Open `modulaser_battery_calculator.html` directly in any modern browser — no
build step, no dependencies to install. For the full walkthrough, use the
in-app **Help** button once it's open (12-step Quick Start + a fully worked
example).

## Versioning

`MM.mm.rrr_YYMMDD` — major and minor version numbers are set deliberately, not
auto-incremented; the patch number increments once per distinct logical change
and resets when minor/major changes. Full detail in
[CHANGELOG.md](./CHANGELOG.md).

## License

See [LICENSE](./LICENSE).
