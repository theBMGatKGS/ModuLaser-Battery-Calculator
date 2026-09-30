# Getting the Battery Calculator Live on GitHub Pages

## The situation

Your GitHub repo already has Pages configured and live: it serves the ModuLaser
Field Report tool from the `MASD-Commissioning-Report` branch at
**masdtools.net**. The battery calculator lives on a separate branch,
`MASD-Battery-Calculator`, which isn't currently published anywhere.

**A single repository can only have one GitHub Pages site** sourced from one
branch (or a `docs/` folder) — unless you use a custom GitHub Actions workflow
to build a combined deployment. That's the key constraint driving the options
below: the goal is to get the calculator live *without* breaking the Field
Report's existing masdtools.net URL.

## Recommended: serve both tools from the same site, different paths

This keeps masdtools.net working exactly as it does today for the Field
Report, and adds the calculator at **masdtools.net/calculator/**. It requires
switching the repo's Pages source from "Deploy from a branch" to "GitHub
Actions" (one-time change, safe — it doesn't touch either branch's content).

### Steps

1. **In the repo, go to Settings → Pages.** Under "Build and deployment,"
   change the Source from "Deploy from a branch" to **"GitHub Actions."**
   (This doesn't delete anything — it just changes how deployment happens.)

2. **Add this workflow file** at `.github/workflows/deploy-pages.yml` on
   whichever branch you consider your "main"/default branch (create it there,
   not on either of the two content branches):

   ```yaml
   name: Deploy Pages (Field Report + Battery Calculator)

   on:
     push:
       branches:
         - MASD-Commissioning-Report
         - MASD-Battery-Calculator
     workflow_dispatch: {}

   permissions:
     contents: read
     pages: write
     id-token: write

   concurrency:
     group: pages
     cancel-in-progress: false

   jobs:
     build:
       runs-on: ubuntu-latest
       steps:
         - name: Checkout Field Report (root)
           uses: actions/checkout@v4
           with:
             ref: MASD-Commissioning-Report
             path: field-report

         - name: Checkout Battery Calculator (subdirectory)
           uses: actions/checkout@v4
           with:
             ref: MASD-Battery-Calculator
             path: battery-calculator

         - name: Assemble combined site
           run: |
             mkdir -p _site/calculator
             # Field Report content at the site root
             cp -r field-report/* _site/
             # Battery Calculator: the PWA files live in a pwa/ subfolder in the
             # branch, not at branch root — copy that subfolder's CONTENTS
             # (not the folder itself) so index.html/manifest.json/sw.js/icons/
             # land as siblings directly under /calculator/. This flattening
             # matters: the PWA's service worker registers with a relative,
             # no-leading-slash path ('sw.js'), so its default scope becomes
             # whatever directory it physically sits in when deployed — it
             # needs to be a direct sibling of index.html at /calculator/ to
             # control the whole app, not nested one level deeper.
             cp -r battery-calculator/pwa/* _site/calculator/
             # Remove workflow/repo files that shouldn't be published, if present
             rm -rf _site/.github _site/calculator/.github

         - name: Setup Pages
           uses: actions/configure-pages@v5

         - name: Upload combined artifact
           uses: actions/upload-pages-artifact@v3
           with:
             path: _site

     deploy:
       needs: build
       runs-on: ubuntu-latest
       environment:
         name: github-pages
         url: ${{ steps.deployment.outputs.page_url }}
       steps:
         - name: Deploy to GitHub Pages
           id: deployment
           uses: actions/deploy-pages@v4
   ```

3. **The PWA files live in a `pwa/` subfolder in the branch** (alongside the
   standalone `.html` file and `electron-app/`), not at the branch root — the
   workflow above already accounts for this by copying `pwa/`'s *contents*
   into `_site/calculator/`, not the `pwa/` folder itself. You don't need to
   reorganize anything in the branch to make this work; keep `pwa/` where it
   is. This was confirmed by checking the actual files: `manifest.json`'s
   `start_url`/`scope`, `sw.js`'s cached-file list, and `index.html`'s
   manifest link and `serviceWorker.register('sw.js')` call all use relative
   paths with no leading slash — which is exactly what makes this deployable
   under any path prefix (`/`, `/calculator/`, or anything else) without
   editing a single file. The one thing that *does* matter is that the
   flattened output keeps `index.html`, `manifest.json`, `sw.js`, and `icons/`
   as direct siblings — the service worker's scope defaults to whatever
   directory it physically sits in, so it needs to be a sibling of
   `index.html`, not nested a level deeper, to control the whole app.

4. **Commit and push this workflow file.** It will run automatically on the
   next push to either content branch, or you can trigger it manually from the
   Actions tab (workflow_dispatch is enabled above) to deploy immediately
   without waiting for a new push.

5. **Verify:** masdtools.net should look unchanged (Field Report), and
   masdtools.net/calculator/ should serve the battery calculator.

### Why this approach

- Doesn't touch either branch's actual content.
- Doesn't require a new domain or a second repo.
- Keeps the existing masdtools.net URL working for the Field Report throughout.
- The `workflow_dispatch` trigger lets you deploy on demand while testing,
  without needing a real commit to either branch.

## Alternative: separate repository (simpler, different URL)

If you'd rather keep the calculator completely independent — its own repo, its
own `github.io` URL or custom domain — that avoids any of the above complexity
entirely:

1. Create a new repository (or use a fresh one dedicated to the calculator).
2. Push the `MASD-Battery-Calculator` branch's content to that new repo's
   default branch.
3. In that new repo's Settings → Pages, set Source to "Deploy from a branch,"
   pick the default branch, save.
4. GitHub gives you a `https://<username>.github.io/<repo-name>/` URL
   automatically; add a custom domain later if wanted.

This is the least error-prone option if you don't specifically need the
calculator to live at a `masdtools.net/...` path.

## Not recommended: just switching the existing Pages source

Technically, you could go to Settings → Pages and just change the source
branch from `MASD-Commissioning-Report` to `MASD-Battery-Calculator`. **Don't
do this** unless you're fine with the Field Report disappearing from
masdtools.net — a single "deploy from a branch" Pages site can only serve one
branch at a time, so this would replace one tool's live site with the other's,
not add to it.
