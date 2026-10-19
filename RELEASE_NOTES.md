# Release Notes — ModuLaser Battery Calculator

Plain-language notes per release. The full history is in [CHANGELOG.md](CHANGELOG.md) and Help → Revision Log.

## v02.02.000 — Brands, ASD-160 and printable Quick Start (2026-10-19) · released 2026-10-19

### Recent improvements
- **Manual battery or capacity pick turns Auto Battery Sizing off** (with a toast); the controls stay selectable in Auto.
- **Networked ASD-160s count toward the 127-module SenseNET limit** and share the network's addresses (duplicates flagged).
- **Unidentified power source → ⚠ Incomplete** everywhere: sheet status and amber dot, side panel, print stamp and project file; the Report adds a blank “Power source identified” item to every power supply sheet and an amber banner.
- **A manual alarm factor on an ASD-160 row is what gets validated** ("alarm factor N … exceeds … — lower the alarm factor").
- **Excel Detail sheet: Brand row** under Project (no fills). **Brand logo in the KGS print band** (PDF / HTML / print preview).
- Help screenshots re-shot with fully passing example data, including Recommended Power Supply Arrangement, Edit → Confirm defaults and the Import Calc prompt (from a saved example file).
- **Brand selector (Edwards | Kidde Commercial).** First field in Project Settings; part numbers, supply labels, BOM, logos and report titles follow the brand; the last choice is remembered for new projects.
- **Per-sheet supply variant** (120 V / 220–230 V / ULC), tamper and seismic accessories, and **FACU powers these ASDs** with a power-source prompt (in-house / third-party / unidentified — unidentified keeps the sheet Incomplete).
- **ASD-160 (Micra25 / Senator 25).** + Add ASD-160 and PipeCAD .pl import (MICRA25): 250 mA, dedicated AUX circuit, Remote configuration, networked address 1–127; UL scopes cap SFD/OAP at 1.28 %obs/ft with R-AF7.
- **Battery 12V6A5 (7.2 Ah)** is manual-only, with a too-small advisory.
- **AUX/ribbon rules.** Max 4 AUX per power supply; each ribbon run holds max 4 detectors + 1 display; a detector-started run counts that detector; hybrid clusters may use any number of runs; own-AUX modules are not runs. FAQ text no longer says "2-segment/4-follower".
- **View menu check marks** for Project Settings bar, Sheet sidebar and Results panel.
- **Help revised** with current screenshots, captured headless from the built app with example data (dark UI). New How Do I and FAQ topics: brand, ASD-160, Print Quick Start, ribbon/AUX limits, 12V6A5, 1.28 cap.
- **Help ▸ Print Quick Start.** 2-page letter Quick Start with numbered steps and screenshots, KGS print palette, printed from its own document (no Help chrome).
- Shared modules: modulaser-project.js 1.6.0, MASD engine 1.2.0. Hash policy: new fields at their defaults are stripped, so unchanged 02.01.000 files keep their hash.

### QA audit
- **QA/Auditor verdict: GO (final)** (2026-10-19, on Calculator 4f4c5e5 / Toolbox 7cd58c1 / Report 3303031; `qa/qa-build-review-02.02.000.md`). Brent approved the release 2026-10-19 3:59 PM CT.
- **Findings fixed before release:** F4 UI test that Auto never picks 12V6A5; F6 plan/decisions log completed (C1 #59–#67, plan rev 4.23c); F8 ribbon scope documented; F10 Toolbox Help uses Toolbox-specific menu shots; F11 two Help images replaced to show what the text names; F12 stale Report FAQ versions; Quick Start step 9 nit; paperwork (verbatim quotes).
- **Suites green:** 37 suites, 986 checks, 0 FAIL, 0 SKIP (Calculator, Toolbox and Report, including the Calculator 02.02.000 suites run against the Toolbox).
- **Deferred:** per-cluster total flag → 02.02.001.

## v02.01.000 — MiniLaser ASD support (2026-10-16) · released 2026-10-17

### Recent improvements
- **MiniLaser ASD (FHSD8075-ULF) support (Brent 10-16).** Each sheet has a separate **Standalone ASDs** table: a MiniLaser is never addressed, isn't on SenseNET and can be on any sheet. Draw by fan speed 1–10: 120/134/157/180/200/230/255/285/320/365 mA (standby = alarm).
- **Dedicated AUX circuit per MiniLaser.** One MiniLaser per AUX circuit, never shared, with the 35 mA per-circuit overhead and 3.0 A per-circuit limit. When there are more MiniLasers plus entry points than AUX outputs, validation fails and recommends adding a power supply.
- **I/O Expansion Modules.** Choose 0–2 × 9-30521 per MiniLaser (no added draw). The 9-30520 housing is added automatically when the count is above 0, and the BOM lists both by part number.
- **+ Add MiniLaser.** Opens the Pre-engineered picker (T or I shape, manual Tables 13–31). It fills fan speed, alarm factor and DIP settings and shows pipe length, hole sizes and transport time. Choose Manual config for anything else; the fan speed starts blank, amber with ⚠, until you set it.
- **.pl import.** SOLO detectors become MiniLasers, with fan speed and alarm factor taken from the .pl. Expansions in the .pl are ignored, with a notice, and Confirm Settings? still runs. When the .pl has no alarm factor, the app uses the highest factor whose average hole sensitivity (Fire 1 × holes) stays within the class limit (VEWFD 1.0, EWFD 1.5, SFD 2.0, OAP 2.18 %obs/ft). If even 0 is over the limit, 0 is set and validation fails, recommending fewer holes or a redesign. Each MiniLaser gets a DIP or Remote configuration recommendation.
- MiniLasers appear on screen, in print, Word, Excel (CAD Schedule, no fills), the Cluster Validation Report and `.mlproj.json`. `modulaser-project.js` 1.5.1 and `masd-engine.js` 1.1.0; ModuLaser calculation math unchanged.
- **Current Draw Reference (Brent 10-16).** The MiniLaser (FHSD8075-ULF) has its own table in the in-app Help Module Current Draw Reference, `ModuLaser_Current_Draw_Reference.html` and `.xlsx`: fan speeds 1–10 draw 120, 134, 157, 180, 200, 230, 255, 285, 320 and 365 mA, with alarm equal to the fan draw. The xlsx was rebuilt with no fills or colour coding.
- **MiniLaser-only sheets** no longer show the "No modules yet" guide. They still count as having devices, and a blank MiniLaser fan speed still keeps the sheet *Needs entry*.
- **Multi-supply arrangement.** MiniLasers aren't addressed, so they are never part of the address/network grouping. Arrangement export moves clusters only, so MiniLasers stay on the original sheet. Arrangement 1 adds their mA and their dedicated AUX circuits and shows a "MiniLasers (stay on this sheet)" row.
- **Arrangement with 2+ clusters (Brent 10-16, 9:02 PM).** The "Disparate clusters must not share power pathways" warning stays, but it no longer withholds the Recommended Power Supply Arrangement: the card (with MiniLasers on Arrangement 1) and its export show alongside the warning. Other flags still withhold it. Help/FAQ updated.
- **QA delta (02.01.000 review).** F1: the MiniLaser manual p.66 pipe limits are now enforced on .pl MiniLasers (`MLP.miniLaserPipeCheck`). Too many holes for the class (VEWFD 10, EWFD 20, SFD 35, UL OAP 24, SA 25, ULC 35), a pipe that is too long (NFPA/ULC 400 ft, UL OAP/SA-R1 300 ft, SA-R2 200 ft) or, when known, a first hole more than 16 ft out raises a validation flag. Pre-engineered picker rows come straight from the manual tables and are exempt. F8: on Edwards A/BPS every entry point has its own AUX circuit and ribbons stay within a cluster, so the "Disparate clusters" warning fires only if clusters actually share a pathway. A third-party supply doesn't track AUX per entry point, so the warning stays there. F6: the Current Draw Reference xlsx uses an explicit black font (still no fills). Tests: output goes to `$MLP_TEST_OUT`, `regress.py` takes `NEW_REV`/`BASE_REV`/`APP`, and test_v2 detects the Toolbox.
- **Final (QA GO + Brent).** The "Disparate clusters" message is a **warning only**: it is labelled "Warning:", the sheet can still PASS, and nothing is withheld. The "Recommendation withheld" banner, the arrangement card, the Bill of Materials and Export now all follow the same rule (shown unless a real validation issue exists). On Edwards A/BPS it never fires: AUX circuits are unique per entry point and ribbons stay within a cluster, so the unreachable shared-pathway check was removed. `modulaser-project.js` bumped to **1.5.1** (pipe limits). The first-hole distance check is manual-entry only, because .pl holes carry no position. Tests skip the Example Shaft sections with a clear message when Brent's fixtures (kept off GitHub) are absent. regress.py defaults to the repo under test.
- **Release prep (QA delta 3).** Service-worker cache bumped to `modulaser-calc-v53` (pwa/docs). Side panel: real validation flags get their own style, distinct from the amber advisory warning, and the sidebar count leaves out advisory warnings. Fixture-dependent tests print `SKIPPED` in their summary and fail when `REQUIRE_FIXTURES=1`.
- **MiniLaser detection class from a .pl (Brent-approved):** area override → project standard → SFD. Max transport time is no longer used. **A MiniLaser imported from a .pl is non-pre-engineered by default** (Brent: pre-engineered units don't need a PipeCAD design), so elbow/tee counts no longer decide it. The recommendation is DIP only when the fan is 2/4/7/10 and the AF is 2/4/6/8, otherwise Remote. Tick **Pre-engineered** on an imported row to override; DIP is then recommended (saved with the project and carried in `.mlproj.json` as `minilaser.preEngineered`).

### QA audit
- **QA/Auditor verdict: GO** (Delta review 4, 2026-10-17, on Calculator c59a78c / Toolbox e3dfb68 / Report b7cbadb; `qa/qa-report-02.01.000.md`). No blocking findings.
- **Findings fixed before release:** F1 MiniLaser pipe limits (manual p.66) enforced; F3/F4 test hygiene (fixture tests report SKIPPED, fail with `REQUIRE_FIXTURES=1`; repo-under-test defaults); F5 40% flow wording (PASS with a warning note); F6 print font; F8 Disparate-clusters made a warning only (sheet can pass; nothing withheld); dead A/BPS branch removed; `modulaser-project.js` 1.5.1; side-panel flag vs warning styling; service-worker cache bumps; README versions.
- **Suites green:** minilaser 48, disparate 13, 0204 43, addrlog 27, auto_address 47, cad 6, confirm 24, cvr 12, empty 17, g1 13, amber 22, columns 24, needs_entry 14, sensenet 30, v2 64, regress 3/3.
- **Remaining non-blocking nits:** `mlp_sync_test` silently skips `/workspace/mlp` when it's absent and doesn't compare the engine build source; the Calculator root build registers a `sw.js` that isn't present at the repo root (pwa/ and docs/ builds have one; predates this release).

## v02.00.005 — Auto addressing, CAD Schedule settings (2026-10-16) · released 2026-10-16

### Recent improvements
- **Auto addressing (Brent 10-16, revised 5:27 PM).** **New build** (first modules in an empty project — first .pl import or first + Add): **Networked or Standalone?** sets every sheet's mode, then **Auto address?** Yes / No. Yes numbers Networked sheets 1…N in sheet order across sheets (whole sheets roll to SenseNET 2 past 127, with the infrastructure notice) and Standalone sheets from 1 on each sheet. **Existing project** gaining modules (new .pl import, a new sheet, modules added to a sheet, Import Calc → Merge sheets): one prompt — **Continue addressing per previous sheets** (only the new modules; Networked continues after the last address on its network, a new sheet rolls to the next network past 127; a new Standalone sheet starts at 1), **Manually address**, or **Re-auto address entire project**. New sheets take the project's mode; mixed projects keep the Mixed addressing banner. After a .pl import: Confirm Settings? → (mode) → address; Revise import and linked-file re-imports don't prompt. Every automatic change is one **Edit → Address change log** entry with one-step Undo (Undo bar or Ctrl+Z). Quick repeated adds give one prompt, never stacked on another prompt.
- **Excel CAD Schedule shows standby, alarm and margin.** Each power supply table starts with a row with that sheet's own **Standby time** (h), **Alarm time** (min) and **Safety margin** (%). Still no merged cells or fills.
- **Cluster Validation Report print redesign (Brent approved).** KGS palette on white: navy title bar, project/network summary box, **Entry point** / **Ribbon Path** / **CALCULATION INVALID** / **VALIDATION ERROR PENDING** chips; every page repeats a header (CLUSTER VALIDATION REPORT · project · Network #) and footer (app name + revision · Page n of N); table headers repeat across pages, rows never split, cells don't wrap. On-screen report unchanged apart from the chips.
- **Incomplete shown in amber with ⚠ (Brent 10-16 6:07 PM).** Every Incomplete indication — sheet status (⚠ INCOMPLETE), an empty sheet's required Ah, battery and PSU recommendation, sidebar, Live Results, print stamps/tiles/tables and legend, Word cells, the withheld PSU recommendation and the CVR pending-validation chip — is amber with a warning symbol: needs-entry amber on screen (AA on the dark theme), #8a5a00 on #fdf3dc in print and Word (AA on white; the ⚠ and the word read in grayscale). Excel exports have no fills or colour coding at all (Brent 6:28 PM): there it's plain "⚠ Incomplete" text. `.mlproj.json` keeps the plain status for the Field Report.
- Calculation math, `masd-engine.js` 1.0.0 and `modulaser-project.js` 1.4.0 unchanged.

### QA audit
| Date | Commits audited | Result | Report |
|---|---|---|---|
| 2026-10-16 | Calculator 57230cc / Toolbox f04f862 | QA/Auditor PASS (GO), no blocking findings. Calculator suites green: amber 22, auto_address 47, cad 6, cvr 12, addrlog 27, sensenet 30, confirm 24, empty 17, g1 13, columns 24, needs_entry 14, 0204 43, v2 64, regress 3/3 | `qa/qa-report-02.00.005.md` |

## v02.00.004 — Defaults, empty sheets, addressing modes (2026-10-15) · released 2026-10-16

### Highlights
- **Valid defaults are no longer flagged.** Design Basis, Standby (h), Alarm (min), Ambient Temp., Module Type, Power, Addressing, supply mode, NFPA 72 edition and margin keep their defaults without amber and no longer make a sheet *Needs entry*. Only empty required fields (Power Supply Name, Location, module Address, Zone, Fan Speed…) are amber. **Edit → Confirm defaults** is kept but no longer needed (harmless).
- **New sheets start with no modules.** An empty sheet shows a guide: **Import .pl…** (from PipeCAD) or **+ Add Display / + Add Detector** (by hand). The last module can be removed (the guide returns). An empty sheet is *Needs entry* / INCOMPLETE.
- **Standby (h) / Alarm (min)** no longer cut values off on screens ≤ 1366 px (boxes keep 92 px; the settings row wraps).
- **Addressing per mode.** Networked sheets share an address pool per SenseNET network (1–127 on each network). A Standalone sheet is its own pool (1–9, now scoped per sheet instead of per cluster) and may reuse addresses from other sheets without a Validation Error; duplicates inside one Standalone sheet are still flagged.
- **Mixed Networked + Standalone** projects show a *Mixed addressing* banner: **Make all Networked…** / **Make all Standalone…**, confirm first, optional **Also re-address all modules** (Networked 1…N across sheets in order; Standalone 1…n per sheet; module order, ribbon/AUX/cluster assignments unchanged).
- **Imports keep addresses** (Import Calc, Import project, .pl re-import) and list any per-mode conflicts right after import.
- **SenseNET networks (up to 127 modules each).** Each Networked sheet has a SenseNET network number (selector on the Addressing row, SN1/SN2 tag in the sidebar, *Networked · SenseNET n* in print/Word/Excel settings, saved per sheet; older files default to network 1). Past 127 modules, whole sheets (last in sheet order first) move to SenseNET 2, 3… and are addressed from 1, and you're told a new network was added and the design must include its infrastructure. A sheet never spans networks. Duplicate addresses are checked per network. Networked re-address: 1–127 on SenseNET 1 in sheet order, then 1… on SenseNET 2. Imports keep networks; an import over 127 offers *Move overflow to a new SenseNET network*. Shared `modulaser-project.js` unchanged (the network rides in the calculator state inside `.mlproj.json`).
- **Address change log + Undo (QA F1/F2).** Unify / re-address, SenseNET network moves and Standalone clears are written to **Edit → Address change log…** (saved with the project and in `.mlproj.json` calculator state) with each module's address and network before and after, and can be undone in one step (Undo bar above the sheet, or Ctrl+Z outside text fields). Make all Standalone lists the addresses above 9 it will clear before you confirm and reports them afterwards; switching one sheet to Standalone does the same. Undo is disarmed by the next manual address/mode/network edit and Ctrl+Z is ignored while any field or dropdown has focus. Automatic SenseNET moves happen only when a network's count rises past 127; while a network is over 127 (e.g. after undoing a move) the flag stays and a **Move overflow to SenseNET n** banner offers the move. Clear file clears the address log.
- **Confirm Settings? after a .pl import (Brent 10-16).** After **Create sheets**, a prompt summarizes the settings applied during import (Design Basis, standby/alarm, ambient temperature, margin, edition, supply capacity/mode, files → sheets/modules). **Confirm** marks every item configured during the import as confirmed, so only genuinely empty fields (e.g. addresses) stay amber. **Revise import** rolls the import back and reopens the wizard on the review step with every choice kept. (Linked-file updates are unchanged.)
- **Design Basis and Ambient Temperature start on "- Select -".** It's an empty required selection: amber, and the sheet stays INCOMPLETE/Needs entry until chosen (no de-rating meanwhile, so no NaN). The .pl wizard requires both in step 1. Saved files keep their values; legacy files without these keys keep the old defaults (NFPA 72 Voice, 77 °F). Until a sheet has modules it shows **Incomplete** for battery Ah everywhere: results card, Live Results, sidebar, print, Word and Excel. In `.mlproj.json` the PSU has `requiredAh: null` and `incomplete: true`, with no battery and a blank PSU model/enclosure. There's no PASS and no battery/PSU recommendation. The Field Report imports it with Required Ah blank, and the shared modules are unchanged.
- Calculation math and `masd-engine.js` 1.0.0 unchanged (no engine bump). Shared `modulaser-project.js` 1.4.0 (bumped from 1.3.0 for SenseNET networks: each device in .mlproj.json carries its network, the shared validator checks duplicates per network and the 127 limit per network; byte-identical in the Calculator, Toolbox and Field Report 02.00.002).
- Open older saved .html files in 02.00.004 with **File → Import Calc** to get these changes.

### QA audit
| Date | Commits audited | Result | Report |
|---|---|---|---|
| 2026-10-16 | Calculator 951f769 / Toolbox 956e1e1 / Report de287fb | QA 2026-10-16: Calculator 951f769 / Toolbox 956e1e1 / Report de287fb GO | `qa/brief-02.00.004.md` |

## v02.00.003 — Needs-entry highlight fix (2026-10-14)

### Highlights
- **Needs entry now shows where.** Sheets with the amber *Needs entry* status outline every field still needing entry with a 2px **amber** outline and tint (inputs, custom dropdowns, radio groups), matching the sidebar dot. Before, the 1px soft-blue outline from 01.05 was indistinguishable from normal borders on the 02.00 dark theme, and the dropdown highlights sat on hidden native selects' visible buttons in the same blue.
- **Show next ›** button on the Live Results message (*N fields still need entry (amber outline)*) scrolls to and focuses each field in turn.
- **Print contrast:** KGS label grey `#747574` → `#6b6c6b` (5.0:1 on the info panel, 5.3:1 on white).
- **Module table columns (per Brent):** Module Type labels DISP-MIN / DISP-STD / DISP-CMD / DETECTOR; Cluster shows the 2-digit number only (01); Power shows *Own circuit* or *Ribbon Path*. Fixed column widths so nothing truncates or wraps; the table scrolls sideways on narrow windows. Print/Export and Word module tables gain Model, Cluster and Power columns, single-line. Saved files are unaffected (stored values unchanged).
- Status logic, counts and calculation math unchanged (regression scenarios identical).
- **Already-saved .html files keep the code they were saved with.** Opening one of them directly still shows the old look. To get these fixes, open 02.00.003 and bring the data in with **File → Import Calc** (or Import project).

### QA audit
| Date | Commits audited | Result | Report |
|---|---|---|---|
| 2026-10-14 | Calculator 43d5a23 · Toolbox 7d1cfec | **QA 2026-10-14: Calculator 43d5a23 / Toolbox 7d1cfec GO-conditional; Word header wrap fixed in final** | `qa/qa-needs-entry-2026-10-14.md` |
| 2026-10-14 | Calculator d34555b · Toolbox 209f54f | **QA 2026-10-14 final: Calculator d34555b / Toolbox 209f54f GO** | `qa/qa-needs-entry-2026-10-14.md` |

QA findings fixed after that audit: Toolbox false "Older revision" warning when re-importing its own saved file (F1); cross-sheet Cluster hint overflow (F2); "No cluster display" button text (F3); Word default font, fixed table layout and spanned summary rows (F4); a hidden field counted on new sheets, 19 instead of 18 (F5); stale lineage/docs (F6); tests extended to every sheet, imported through the app, Word render checked (F7). Final: Word Standby mA / Alarm mA columns widened to 1100 twips so the header no longer wraps; the summary row shows 'Status:' again.

## v02.00.002 — Shared MASD engine (2026-10-13)

### Highlights
- **Shared MASD engine 1.0.0** (`masd-engine.js`): the battery math, reference data and PipeCAD .pl import are byte-identical with the new **MASD Engineering Toolbox 00.01.000**, which embeds this calculator. Results unchanged — regression scenarios give the same numbers as 02.00.001.
- **Harmonization rule:** any engine change bumps the engine version and the revision of both apps, with matching notes; each app records the engine version.
- **Project file pass-through:** field changes, approvals, Toolbox device configuration, Toolbox Performance Criteria and unknown keys survive a round trip. Saved-by records the Prepared By name.
- **modulaser-project.js 1.3.0**, identical in the calculator, the Commissioning Report and the Toolbox: SHA-256 design and site hashes; metric .pl hole-sensitivity warning; corrected citations.

### QA audit
| Date | Commit audited | Result | Issue |
|---|---|---|---|
| 2026-10-13 | cc55189 (02.00.001) + working tree | Defaults citations FAIL → fixed · Example Project rule PASS · Audit trail FAIL → fixed · Quick Start version FAIL → fixed | [#1](https://github.com/theBMGatKGS/ModuLaser-Battery-Calculator/issues/1) |
| 2026-10-13 re-check (8:28–8:45 PM ET) | 2b2b93b | **CONDITIONAL PASS** — fixed after re-check: stable design hash, mis-cited table number removed, UL 268 confirmation required, UL thresholds (≤60/43/43 s), sign-off order enforced, name-gated edits, append-only log, ASAG44201 replaced by NFPA 76-2024 clauses, Quick Start 02.00.001+, legacy Ah checks | [#1](https://github.com/theBMGatKGS/ModuLaser-Battery-Calculator/issues/1) |

**Fixes included:** citations (App. A p.113 hole limits, Table 29 p.76 flow, Prealarm), unsourced defaults labelled typical – unverified, pass-through of changes/approvals/unknown keys, SHA-256 hashes, Saved-by name, Quick Start version text, test wait-for-condition.
**QA re-check (2026-10-13):** CONDITIONAL PASS; post-re-check fixes listed above and in the revision log.
**Final verdict:**

QA audit 2026-10-13, final re-check of commit 848e97d (clean tree). **PASS.** Tests: regress 3/3, test 106/106, calc_project_test 16/16, shared-file and engine parity 2/2. Verified: SHA-256 design hash stable on a no-op round trip (Report → Calculator → Calculator), unknown fields, change log and sign-offs preserved, savedBy name, shared modulaser-project.js 1.3.0 and MASD engine 1.0.0 identical across apps. Known limitation: metric PipeCAD hole sensitivity is shown unconverted with a warning (unit unconfirmed). UL 268 thresholds (shared) are per Brent, not verified by QA. Issue: https://github.com/theBMGatKGS/ModuLaser-Battery-Calculator/issues/1

QA delta re-check 2026-10-13, commit b1cb13b (clean). **PASS.** Brent's rule is verified: a hole passes at or below (≤) the class maximum, the more restrictive of UL and NFPA (VEWFD 1.0 %obs/ft / 60 s, EWFD 1.5 / 43 s, SFD/OAP 2.18 / 43 s; targets 1.0 / 1.5 / 2.0). UL projects enforce the ModuLaser UL 268 range lower limits (Install Manual App. A p.113). This supersedes the earlier rule (a hole had to be below the limit). Tests: sens_rule 14/14, regress 3/3, test 106/106, calc_project_test 16/16, parity 2/2; design hash stable on round trip. Per Brent, unverified by QA: the ≤ rule (the manual's FM 3230 rows say "<") and EWFD 1.5 (from NFPA 76-2024 8.5.3.2.1.3; UL Range 2 itself is 0.05–2.18). Final pre-tag pass 2026-10-13 (10:02–10:40 PM ET): Calculator 6adde0d / Report 5448488 (release a32d988) / Toolbox 8aa707a — GO; sens_rule 14/14; committed tests pass (release commits differ from these only by this release-note line).


## v02.00.001 — ModuLaser project file (2026-10-13)
- File → Export / Import project (`.mlproj.json`) shared with the Commissioning Report.
