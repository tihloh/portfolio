# Christian Bustamante Portfolio

Personal portfolio showcasing software development, IT systems, infrastructure, automation, government IT experience, credentials, professional training, project evidence, and delivered systems.

## Editing the site

Edit the individual sections under `partials/`. The section order is defined in `scripts/build_portfolio.py`. The source layout is `index.template.html`.

The complete `index.html` is **generated at build time** instead of being assembled with JavaScript in visitors' browsers. `js/site.js` only handles optional interaction and the image viewer.

No local computer or manual build is required. Edit the source files in GitHub; the existing GitHub Actions workflow assembles and deploys the site on pushes to `master`. To generate the site again without a code change, run **Build and deploy portfolio** manually from the repository's **Actions** tab.

## Automatic rebuild and deployment

Each push to `master` starts the existing GitHub Actions workflow. It assembles and validates the general portfolio and every specialized portfolio from their editable HTML partials, commits refreshed generated HTML files if changed, and deploys all seven static pages using GitHub Pages.

**One-time GitHub Pages setting:** Settings → Pages → Build and deployment → Source → **GitHub Actions**. A branch-based Pages build is not triggered reliably by a commit generated with the default GitHub Actions token; this workflow deploys explicitly.

If the workflow cannot push the generated HTML, check repository Actions permissions and branch protection. Commits from the workflow's default token do not start an infinite workflow loop.

The existing custom domain is set in `CNAME`.

## Specialized portfolio pages (source structure)

The general homepage and existing build behavior remain intact. Six targeted pages
are maintained as separate sets of editable files in `pages/<page>/partials/`
with ordered sections defined in each `pages/<page>/page.json`.

Shared navigation, contact, footer, background, and image-viewer components are in
`shared/`. Selected pages can also include the existing `partials/credentials.html`.

The existing GitHub Actions workflow now runs `python3 scripts/build_portfolio.py --all` and `--all --check` automatically. Each page receives one generated `<slug>/index.html`, and the general homepage stays at `index.html`.

**GitHub-only editing:** Modify the relevant `pages/<slug>/partials/*.html` or shared partials directly in GitHub and commit to `master`. The workflow handles building and deployment; there is no need to run Python on your PC.

You can also rebuild at any time from **GitHub → Actions → Build and deploy portfolio → Run workflow**. No additional workflows were added. The existing `master` push and manual triggers were retained.
