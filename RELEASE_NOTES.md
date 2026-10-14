# Release Notes — ModuLaser Battery Calculator

Plain-language notes per release. The full history is in [CHANGELOG.md](CHANGELOG.md) and Help → Revision Log.

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
| 2026-10-14 | Calculator 3757dd8 · Toolbox ff61dc5 | **Calculator GO / Toolbox re-check pending** | `qa/qa-needs-entry-2026-10-14.md` |

QA findings fixed after that audit: Toolbox false "Older revision" warning when re-importing its own saved file (F1); cross-sheet Cluster hint overflow (F2); "No cluster display" button text (F3); Word default font, fixed table layout and spanned summary rows (F4); a hidden field counted on new sheets, 19 instead of 18 (F5); stale lineage/docs (F6); tests extended to every sheet, imported through the app, Word render checked (F7).

## v02.00.002 — Shared MASD engine (2026-10-13)

### Highlights
- **Shared MASD engine 1.0.0** (`masd-engine.js`): the battery math, reference data and PipeCAD .pl import are byte-identical with the new **MASD Engineering Toolbox 00.01.000**, which embeds this calculator. Results unchanged — regression scenarios give the same numbers as 02.00.001.
- **Harmonization rule:** any engine change bumps the engine version and the revision of both apps, with matching notes; each app records the engine version.
- **Project file pass-through:** field changes, approvals, Toolbox device configuration, Toolbox Performance Criteria and unknown keys survive a round trip. Saved-by records the Prepared By name.
- **modulaser-project.js 1.3.0**, identical in the calculator, the Commissioning Report and the Toolbox: SHA-256 design and site hashes; metric .pl hole-sensitivity warning; corrected citations.

### QA audit
| Date | Commit audited | Result | Issue |
|---|---|---|---|
| 2026-10-13 | cc55189 (02.00.001) + working tree | Defaults citations FAIL → fixed · Solano rule PASS · Audit trail FAIL → fixed · Quick Start version FAIL → fixed | [#1](https://github.com/theBMGatKGS/ModuLaser-Battery-Calculator/issues/1) |
| 2026-10-13 re-check (8:28–8:45 PM ET) | 2b2b93b | **CONDITIONAL PASS** — fixed after re-check: stable design hash, mis-cited table number removed, UL 268 confirmation required, UL thresholds (≤60/43/43 s), sign-off order enforced, name-gated edits, append-only log, ASAG44201 replaced by NFPA 76-2024 clauses, Quick Start 02.00.001+, legacy Ah checks | [#1](https://github.com/theBMGatKGS/ModuLaser-Battery-Calculator/issues/1) |

**Fixes included:** citations (App. A p.113 hole limits, Table 29 p.76 flow, Prealarm), unsourced defaults labelled typical – unverified, pass-through of changes/approvals/unknown keys, SHA-256 hashes, Saved-by name, Quick Start version text, test wait-for-condition.
**QA re-check (2026-10-13):** CONDITIONAL PASS; post-re-check fixes listed above and in the revision log.
**Final verdict:**

QA audit 2026-10-13, final re-check of commit 848e97d (clean tree). **PASS.** Tests: regress 3/3, test 106/106, calc_project_test 16/16, shared-file and engine parity 2/2. Verified: SHA-256 design hash stable on a no-op round trip (Report → Calculator → Calculator), unknown fields, change log and sign-offs preserved, savedBy name, shared modulaser-project.js 1.3.0 and MASD engine 1.0.0 identical across apps. Known limitation: metric PipeCAD hole sensitivity is shown unconverted with a warning (unit unconfirmed). UL 268 thresholds (shared) are per Brent, not verified by QA. Issue: https://github.com/theBMGatKGS/ModuLaser-Battery-Calculator/issues/1

QA delta re-check 2026-10-13, commit b1cb13b (clean). **PASS.** Brent's rule is verified: a hole passes at or below (≤) the class maximum, the more restrictive of UL and NFPA (VEWFD 1.0 %obs/ft / 60 s, EWFD 1.5 / 43 s, SFD/OAP 2.18 / 43 s; targets 1.0 / 1.5 / 2.0). UL projects enforce the ModuLaser UL 268 range lower limits (Install Manual App. A p.113). This supersedes the earlier rule (a hole had to be below the limit). Tests: sens_rule 14/14, regress 3/3, test 106/106, calc_project_test 16/16, parity 2/2; design hash stable on round trip. Per Brent, unverified by QA: the ≤ rule (the manual's FM 3230 rows say "<") and EWFD 1.5 (from NFPA 76-2024 8.5.3.2.1.3; UL Range 2 itself is 0.05–2.18). Final pre-tag pass 2026-10-13 (10:02–10:40 PM ET): Calculator 6adde0d / Report 5448488 (release a32d988) / Toolbox 8aa707a — GO; sens_rule 14/14; committed tests pass (release commits differ from these only by this release-note line).


## v02.00.001 — ModuLaser project file (2026-10-13)
- File → Export / Import project (`.mlproj.json`) shared with the Commissioning Report.
