# Release Notes — ModuLaser Battery Calculator

Plain-language notes per release. The full history is in [CHANGELOG.md](CHANGELOG.md) and Help → Revision Log.

## v02.00.002 — Shared MASD engine (2026-10-13) · not yet released

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

Post-QA changes (2026-10-13, 9:08–9:10 PM ET; not yet re-checked by QA): Brent changed the sensitivity rule for all apps and the shared module — a hole PASSES at or below (≤) the class maximum, taking the more restrictive of UL and NFPA (supersedes the strict < rule); transport stays ≤. Target values VEWFD 1.0 / EWFD 1.5 / SFD 2.0 %obs/ft are shown in the UI, printouts, narrative and Report. UL projects also show the ModuLaser UL 268 range per class and enforce its lower limit (Install Manual App. A, printed p.113): VEWFD Special Application Range 1 0.05–1.00 %obs/ft, 3–60 s; EWFD Range 2 0.05–2.18 (max 1.5 per NFPA 76), 3–43 s; SFD Open Area 1.70–2.18, 6–43 s (Brent confirmed 9:17 PM ET; final). Both bounds enforced on UL projects; SFD target 2.0. NFPA 318-2025 §11.1.3 cited for the cleanroom (VEWFD – NFPA 76/318) path. Help states that the NFPA presets carry a UL 268 claim and that EWFD 1.5 comes from NFPA 76 (UL Range 2 transport 43 s), recorded per Brent.


## v02.00.001 — ModuLaser project file (2026-10-13)
- File → Export / Import project (`.mlproj.json`) shared with the Commissioning Report.
