# tjdoolittle.github.io

Project showcase, served by GitHub Pages at <https://tjdoolittle.github.io>.

Static HTML and CSS — no framework, no build step, no external requests. Edit
`index.html` and push; Pages redeploys on its own.

## Files

| File | Purpose |
| --- | --- |
| `index.html` | Page content. Each project is one `<li class="card">`. |
| `styles.css` | All styling. Light/dark themes are CSS variables at the top. |
| `resume.pdf` | The résumé the site serves. Replace this file to update it. |
| `.nojekyll` | Tells Pages to serve the files as-is, no Jekyll processing. |

## Updating the résumé

Overwrite `resume.pdf` with the new version and push. Nothing in `index.html`
needs editing — keep the filename as `resume.pdf`:

```bash
cp /path/to/new-resume.pdf resume.pdf
git commit -am "Update resume" && git push
```

The "Updated <month> <year>" label reads the file's `Last-Modified` header at
page load, so it relabels itself. If `resume.pdf` is ever missing, the section
degrades to "Résumé available on request" rather than showing a broken viewer.

Pages caches assets for about ten minutes, so a swapped PDF can take that long
to reach someone who already visited. A hard refresh gets it immediately.

## Adding a project

Copy an existing card in `index.html` and edit it. The pieces:

- `.chip` — status badge. `chip-live` for something you can open, `chip-wip`
  for in-progress, or plain `chip` for anything else.
- `.tags` — one `<li>` per technology.
- `.card-links` — `link-primary` for the main call to action, plain `<a>` for
  secondary links, `link-muted` `<span>` for non-link notes. Omit the whole
  block if a project has nothing to link to.

The site deliberately links only to running apps — no repository or source
links on any card.

## Local preview

Any static server works:

```bash
python -m http.server 8000
```

Then open <http://localhost:8000>.
