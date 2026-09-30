# Contributing

This tool is maintained iteratively — most changes are made through an AI
coding assistant session rather than a traditional open-source PR workflow, but
the same discipline applies regardless of who or what is making the change.

## Before making any change

1. **Read the calculator's own Help menu first** (Standards and Formulas, FAQs)
   — it documents the actual formulas, citations, and non-obvious behavior in
   more detail than any external doc will.
2. If a broader rebuild-level specification is needed, see
   `ModuLaser_Calculator_Rebuild_Spec.md` (in the outputs history / repo, if
   present) — it captures architecture, print-layout technique, and known
   pitfalls in much greater depth than this file.

## Core constraints — never violate these

- **Never let a change understate a battery or safety-margin requirement.**
  Every auto-computed minimum (margin, de-rating factor, battery size) must
  remain a hard floor a user can increase but never decrease below what the
  applicable standard requires. This applies to every feature, not just the
  ones it was originally stated for.
- **Verify any code/standard citation before writing it in.** Web search or an
  authoritative source, not secondhand summaries — this project's history
  includes catching a real arithmetic error in pasted source material before
  it got built in. If a specific clause/section can't be independently
  confirmed, cite at the standard/edition level instead of guessing precision.
- **One printed calculation page per power supply, in essentially every
  realistic scenario.** This drove a large amount of the print CSS and is not
  something to casually regress for the sake of an unrelated change.

## Testing expectations

- **Any change to calculation or validation logic** needs to be proven with
  concrete numbers — a quick Node/jsdom script that loads the calculator,
  drives it through the relevant scenario, and checks the actual output values
  against a hand-computed expectation. Don't assume a formula change is
  correct because the code "looks right."
- **Any change to print CSS or layout** needs to be verified by actually
  rendering the print output — headless Chromium (Puppeteer) to a real PDF,
  converted to an image, and visually inspected. Do not trust a CSS change
  based on reading the rules alone; several real bugs in this project's
  history (content silently clipping off the page edge, a broken 2-column
  layout) were only caught this way.
- **Test both a light/typical scenario and a dense/worst-case scenario**
  (many modules, an active invalid-calculation state) for any print change —
  a fix that works for one can silently not-quite-fit the other.
- Run a full baseline regression (a simple known scenario with a known
  expected total current draw / required Ah) after any change, not just the
  specific thing being changed.

## The three deliverables must stay in sync

The standalone HTML is the single source of truth. Every change needs to
propagate to all three:
1. `modulaser_battery_calculator.html` (primary)
2. `pwa/index.html` (copy of the above, wrapped with manifest/service worker)
   — bump the service worker's `CACHE_VERSION` constant on every content change
3. `electron-app/app/modulaser_battery_calculator.html` (copy of the above) —
   also update `APP_REVISION` in `electron-app/main.js` and `"revision"` in
   `electron-app/package.json`

## Versioning

See `CHANGELOG.md` for the format. In short: major/minor are a deliberate
decision, never auto-incremented — when a change seems significant enough to
warrant one, say so explicitly and let the decision be made deliberately;
don't bump it unilaterally. Patch numbers auto-increment per distinct logical
change and log an entry in the calculator's own `AMENDMENTS` array (the
in-app source of truth `CHANGELOG.md` is generated from).

## Known pitfalls (don't re-introduce these)

1. **Restore-timing / stale validation state.** Any check reading a value
   that's itself resolved asynchronously or deferred (e.g. during file
   restore) must not be trusted on the very first pass — add an explicit
   second pass after resolution rather than assuming later recalculation
   happens naturally.
2. **Scope creep in "which cluster does this apply to" logic.** Logic keyed
   by cluster should be tested against a display-less, remote-referencing
   sheet from the start — more than once, code that should scan every
   cluster a sheet touches instead only scanned locally-hosted clusters.
3. **Two fields representing the same information without being synced.**
   If two UI fields conceptually represent one piece of data, keep them
   either genuinely merged or explicitly auto-synced with a manual-override
   escape hatch — never silently redundant.
