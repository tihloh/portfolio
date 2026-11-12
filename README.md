# Christian Bustamante Portfolio

Personal portfolio showcasing software development, IT systems, infrastructure, automation, government IT experience, credentials, professional training, project evidence, and delivered systems.

## Editing the site

Edit the individual sections under `partials/`. The section order is defined in `scripts/build_portfolio.py`. The source layout is `index.template.html`.

The complete `index.html` is **generated at build time** instead of being assembled with JavaScript in visitors' browsers. `js/site.js` only handles optional interaction and the image viewer.

To build locally:

```bash
python3 scripts/build_portfolio.py
python3 scripts/build_portfolio.py --check
```

## Automatic rebuild and deployment

Each push to `master` starts GitHub Actions. It validates and assembles the partials, commits the refreshed `index.html` if changed, and deploys the static site using GitHub Pages.

**One-time GitHub Pages setting:** Settings → Pages → Build and deployment → Source → **GitHub Actions**. A branch-based Pages build is not triggered reliably by a commit generated with the default GitHub Actions token; this workflow deploys explicitly.

If the workflow cannot push the generated HTML, check repository Actions permissions and branch protection. Commits from the workflow's default token do not start an infinite workflow loop.

The existing custom domain is set in `CNAME`.

## Specialized portfolio pages (source structure)

The general homepage and existing build behavior remain intact. Six targeted pages
are maintained as separate sets of editable files in `pages/<page>/partials/`
with ordered sections defined in each `pages/<page>/page.json`.

Shared navigation, contact, footer, background, and image-viewer components are in
`shared/`. Selected pages can also include the existing `partials/credentials.html`.

Build and validate all seven HTML files locally:

```bash
python3 scripts/build_portfolio.py --all
python3 scripts/build_portfolio.py --all --check
python3 scripts/build_portfolio.py --page developer
```

The original `python3 scripts/build_portfolio.py` and `--check` commands still
build/check only the general homepage. The current GitHub Actions workflow and
GitHub Pages packaging have **not** yet been updated to generate/deploy the six
specialized pages. That deployment integration is a separate step.
