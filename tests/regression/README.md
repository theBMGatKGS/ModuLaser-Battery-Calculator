# Battery Calculator regression suites (calctests)

Playwright regression suites used for 02.00.x → 02.01.000. They were copied here from the working folder `/workspace/mlpbuild/calctests`, which is not a git repo. Version expectations have been updated for 02.01.000 / Toolbox 00.02.000.

Run one suite: `python3 tests/regression/test_v2.py` (and so on); run every `test_*.py` for the full set. `regress.py` is the main-vs-branch comparison only (same scenarios must give the same results). Pin the build under test with `NEW_REV=<commit>` (and `BASE_REV`, default `main`) or `APP=<file url>`. All output goes to `$MLP_TEST_OUT` (default: a fresh temp dir).

- Default target: `helpers.py` → `APP=file:///workspace/ModuLaser-Battery-Calculator/modulaser_battery_calculator.html`. Set the `APP` env var to test the Toolbox (`file:///workspace/MASD-Engineering-Toolbox/index.html`).
- External fixtures, not in this repo: `/workspace/qa/brent-needs-entry.html`, the PipeCAD samples under `/workspace/pl-samples` and `/workspace/plbuild/t/`, the Field Report at `/workspace/ModuLaser-Commisioning-Report/index.html`, and `/workspace/v2build/` (used by `help_edit.py`/`dev.py`, not tests).
- `inject.py`, `dev.py`, `help_edit.py` and `shot.py` are build/screenshot helpers, not tests.

- Defaults use the repo under test: `regress.py` builds both the base (`BASE_REV`, default `main`) and the new build from this repo (working tree, or `NEW_REV`). `test_disparate_arrangement.py` covers the warning-only Disparate-clusters rule.
- `make_nfpa318_pl.py` writes the synthetic `NFPA318-Fab-Ceiling.pl` (NFPA 318 fab ceiling, 6 detectors + 1 Minimum Display, fictional values) into `/workspace/plbuild/t/` on every run; it replaces the former real-project fixture.
- `make_synthetic_pl.py` + `synthetic_pl_specs.json` write the other synthetic fixtures (Example-Campus-PSU, Example-Tunnel-5Area, Example-Deck-14Area, Example-Warehouse-OAP into `/workspace/plbuild/t/`; Example-Shaft-MiniLaser, Example-Shaft-ASD160, Example-EN54-Metric into `/workspace/plbuild/synth/`). The specs are numbers-only layout skeletons with fictional names; they replace the former real-project files.
- Real project files stay off GitHub. Set `ML_FIXTURE` (or `ASD_FIXTURE`) to run a suite on one; those sections SKIP with a clear message when the file is absent.
