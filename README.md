# resume.loximity.dev

Personal résumé site for **Ahmad Faris Aiman bin Arizal** — Lead Cloud Engineer, KAF Digital Bank.

A single self-contained `index.html`: all CSS, JavaScript, SVG graphics, and the
animation library (anime.js v3.2.1) are inlined, so it works fully offline and on
any static host with no build step and no external JS dependency. Only the web
fonts load from Google Fonts, and the page has a safe fallback stack if they don't.

## Structure

```
.
├── index.html    # the entire site
├── CNAME         # custom domain for GitHub Pages (resume.loximity.dev)
├── .nojekyll     # tell GitHub Pages to serve files as-is (skip Jekyll)
└── README.md
```

## Deploy to GitHub Pages

1. Create a repo and push these files:

   ```bash
   git init
   git add .
   git commit -m "Initial resume site"
   git branch -M main
   git remote add origin git@github.com:<you>/<repo>.git
   git push -u origin main
   ```

2. In the repo: **Settings → Pages → Build and deployment**
   - Source: **Deploy from a branch**
   - Branch: **main**, folder: **/ (root)** → Save

3. The site publishes at `https://<you>.github.io/<repo>/` within a minute or two.

### Custom domain (resume.loximity.dev)

The `CNAME` file already pins the domain. On the DNS side, add a CNAME record:

```
resume.loximity.dev.  CNAME  <you>.github.io.
```

Then in **Settings → Pages → Custom domain**, confirm `resume.loximity.dev` and
tick **Enforce HTTPS** once the certificate is issued.

> If you'd rather serve it at the apex/user page instead of a project page, name
> the repo `<you>.github.io` and it'll publish at the root with no subpath.

## Local preview

Just open `index.html` in a browser, or:

```bash
python3 -m http.server 8000   # then visit http://localhost:8000
```

## Editing

Everything lives in `index.html`. The résumé content sits in the HTML body; the
scroll animations are driven by the inlined anime.js at the bottom of the file.
