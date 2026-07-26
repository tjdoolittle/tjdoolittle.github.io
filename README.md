# tjdoolittle.github.io

Project showcase, served by GitHub Pages at <https://tjdoolittle.github.io>.

Static HTML and CSS — no framework, no build step. Edit `index.html` and push;
Pages redeploys on its own. The only external request is the optional analytics
tracker (see below), and it stays off until you add a code.

## Files

| File | Purpose |
| --- | --- |
| `index.html` | Page content. Each project is one `<li class="card">`. |
| `stats.html` | Public visit-stats page (`Stats` in the nav). |
| `styles.css` | All styling. Light/dark themes are CSS variables at the top. |
| `site.js` | Shared theme toggle + analytics loader. Holds the GoatCounter code. |
| `resume.pdf` | The résumé the site serves. Replace this file to update it. |
| `.nojekyll` | Tells Pages to serve the files as-is, no Jekyll processing. |

## Visit stats

Traffic is counted with [GoatCounter](https://www.goatcounter.com) — no cookies,
no personal data, no consent banner needed. It ships **off**; the tracker never
loads and the Stats page shows an "not connected yet" note until you switch it
on:

1. Sign up at <https://www.goatcounter.com> and pick a code (your subdomain,
   e.g. `tjdoolittle` → `tjdoolittle.goatcounter.com`).
2. In `site.js`, set `window.GOATCOUNTER_CODE` to that code (one line, near the
   top). That single value powers the tracker on every page and the Stats page.
3. In GoatCounter → Settings, tick **"Allow using the visitor counter"** so the
   public Stats page can read the totals. To make the full referrer/country
   dashboard public too (the "Detailed breakdown" link), also tick **"Make
   statistics public"**.
4. Commit and push.

The Stats page pulls site-wide totals live from GoatCounter's public counter and
degrades to a clear message if they can't load. `stats.html` is marked
`noindex`, so search engines skip it even though anyone with the link can view.

## Updating the résumé

The published `resume.pdf` deliberately omits the direct phone number and home
ZIP — the file is public and gets scraped. A fresh export from Word puts them
back, so run it through `tools/trim-resume.py`, which writes `resume.pdf`:

```bash
uv run --no-project --with pypdf tools/trim-resume.py /path/to/new-export.pdf
git commit -am "Update resume" && git push
```

The script trims the header to `Atlanta, GA | email | LinkedIn`, re-centers the
line, and clears the document metadata (Word leaves the original author's name
in it). It validates the PDF's layout first and refuses to write if anything
looks off, so a bad export fails loudly rather than producing a mangled file —
see the header comment in [tools/trim-resume.py](tools/trim-resume.py) if a
future template change trips it.

Nothing in `index.html` needs editing — keep the filename as `resume.pdf`. If
you ever want to publish the full version verbatim, `cp` it to `resume.pdf`
instead and skip the script.

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
