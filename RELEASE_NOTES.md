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
**Final verdict:** [PENDING RE-CHECK — placeholder]

## v02.00.001 — ModuLaser project file (2026-10-13)
- File → Export / Import project (`.mlproj.json`) shared with the Commissioning Report.
