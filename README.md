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
