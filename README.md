# tjdoolittle.github.io

Project showcase, served by GitHub Pages at <https://tjdoolittle.github.io>.

Static HTML and CSS — no framework, no build step, no external requests. Edit
`index.html` and push; Pages redeploys on its own.

## Files

| File | Purpose |
| --- | --- |
| `index.html` | Page content. Each project is one `<li class="card">`. |
| `styles.css` | All styling. Light/dark themes are CSS variables at the top. |
| `.nojekyll` | Tells Pages to serve the files as-is, no Jekyll processing. |

## Adding a project

Copy an existing card in `index.html` and edit it. The pieces:

- `.chip` — status badge. `chip-live` for something you can open, `chip-wip`
  for in-progress, or plain `chip` for anything else.
- `.tags` — one `<li>` per technology.
- `.card-links` — `link-primary` for the main call to action, plain `<a>` for
  secondary links, `link-muted` `<span>` for non-links like "Source private".

## Local preview

Any static server works:

```bash
python -m http.server 8000
```

Then open <http://localhost:8000>.
