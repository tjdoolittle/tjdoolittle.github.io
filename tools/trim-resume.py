#!/usr/bin/env python3
"""Trim the phone number and ZIP from a resume PDF before publishing it.

The published site (resume.pdf) deliberately omits the direct phone number and
home ZIP that a normal resume carries, since the file is public and
search-indexable. A fresh export from Word puts them back, so run this over the
new export each time you update the resume:

    uv run --no-project --with pypdf tools/trim-resume.py <new-export.pdf>

That writes the trimmed result to resume.pdf in the repo root (override with a
second argument). Then commit and push as usual.

What it does, on page 1 only:
  * rewrites the header contact line from
        "Atlanta, GA, 30316 | (540) 230-7829 | doolittle.thomas@gmail.com | LinkedIn"
    to
        "Atlanta, GA | doolittle.thomas@gmail.com | LinkedIn"
  * re-centers the line and re-places the email/LinkedIn link underlines so the
    layout stays intact
  * clears document metadata (Word's "Print to PDF" leaves the original
    author's name in /Author)

Why it is this involved: the resume is produced by Word's "Print to PDF", which
stores text as subset-font glyph IDs with every run absolutely positioned, so
characters can't simply be deleted — the runs after them have to move, and the
whole line has to be re-centered. Before changing anything the script validates
its width model against the untouched file and aborts if the geometry does not
add up, so a layout change in a future export fails loudly instead of producing
a mangled PDF.

Requires pypdf. Only the header contact line is matched; if a future template
changes that line's text or geometry, EXPECTED_CONTACT / the layout constants
below may need updating (the script will tell you which check failed).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import DecodedStreamObject

# --- what to change -----------------------------------------------------
EXPECTED_CONTACT = 'Atlanta, GA, 30316 | (540) 230-7829 | '
REPLACEMENT = 'Atlanta, GA | '

# --- page-1 geometry these depend on (612pt page under the stream's 0.75
#     scale => usable width 816; center 408). The contact line sits at the
#     Tm y below; its link underlines are stroked paths at UNDERLINE_Y. ---
PAGE_CENTER = 408.0
CONTACT_LINE_Y = 106.08
UNDERLINE_Y = 107.84
TOLERANCE = 0.75          # allowed px error in the width-model self-check

TM_RUN = re.compile(
    r'/(F\d+)\s+([\d.]+)\s+Tf\s*\n1 0 0\.000000 -1 ([\d.-]+) ([\d.-]+) Tm\s*\n\[(.*?)\]\s*TJ',
    re.S)
LINE_PATH = re.compile(r'([\d.-]+)\s+([\d.-]+)\s+m\s+([\d.-]+)\s+([\d.-]+)\s+l')


def die(msg: str) -> None:
    sys.exit(f'trim-resume: {msg}')


def build_font_tables(page):
    """Return (glyph->unicode, unicode->glyph, glyph->width, default-width) per font."""
    g2u, u2g, widths, default_w = {}, {}, {}, {}
    for name in page['/Resources']['/Font']:
        font = page['/Resources']['/Font'][name].get_object()

        tu = font.get('/ToUnicode')
        if tu is not None:
            cmap = tu.get_object().get_data().decode('latin-1')
            m: dict[int, str] = {}
            for block in re.findall(r'beginbfchar(.*?)endbfchar', cmap, re.S):
                for s, d in re.findall(r'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>', block):
                    m[int(s, 16)] = chr(int(d[:4], 16))
            for block in re.findall(r'beginbfrange(.*?)endbfrange', cmap, re.S):
                for lo, hi, d in re.findall(
                        r'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>', block):
                    lo, hi, d = int(lo, 16), int(hi, 16), int(d[:4], 16)
                    for k in range(lo, hi + 1):
                        m[k] = chr(d + k - lo)
            g2u[name] = m
            u2g[name] = {v: k for k, v in m.items()}

        if font.get('/Widths') is not None:
            # Simple font: /Widths indexed from /FirstChar.
            fc = int(font['/FirstChar'])
            widths[name] = {fc + i: float(w) for i, w in enumerate(font['/Widths'])}
            default_w[name] = 1000.0
        elif font.get('/DescendantFonts') is not None:
            # Type0/CID font: /W is "c [w ...]" runs or "c_first c_last w" ranges.
            df = font['/DescendantFonts'].get_object()[0].get_object()
            table: dict[int, float] = {}
            arr = [x.get_object() if hasattr(x, 'get_object') else x
                   for x in df.get('/W', [])]
            i = 0
            while i < len(arr):
                if isinstance(arr[i + 1], list):
                    for k, w in enumerate(arr[i + 1]):
                        table[int(arr[i]) + k] = float(w)
                    i += 2
                else:
                    for c in range(int(arr[i]), int(arr[i + 1]) + 1):
                        table[c] = float(arr[i + 2])
                    i += 3
            widths[name] = table
            default_w[name] = float(df.get('/DW', 1000))

    return g2u, u2g, widths, default_w


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        die('usage: trim-resume.py <source.pdf> [output.pdf]')

    src = Path(sys.argv[1])
    repo_root = Path(__file__).resolve().parent.parent
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else repo_root / 'resume.pdf'
    if not src.exists():
        die(f'source not found: {src}')

    reader = PdfReader(str(src))
    page = reader.pages[0]
    g2u, u2g, widths, default_w = build_font_tables(page)
    content = page.get_contents().get_data().decode('latin-1')

    def width_of(fname: str, size: float, body: str) -> float:
        """Advance of a TJ array: glyph widths less the inline kerning."""
        total = 0.0
        for glyph, kern in re.findall(r'<([0-9A-Fa-f]{4})>|(-?[\d.]+)', body):
            if glyph:
                w = widths['/' + fname].get(int(glyph, 16), default_w['/' + fname])
                total += w / 1000.0 * size
            elif kern:
                total -= float(kern) / 1000.0 * size
        return total

    # Collect the runs making up the contact line.
    runs = []
    for m in TM_RUN.finditer(content):
        fname, size, x, y, body = m.groups()
        if abs(float(y) - CONTACT_LINE_Y) < 0.01:
            runs.append({
                'm': m, 'font': fname, 'size': float(size), 'x': float(x), 'body': body,
                'text': ''.join(g2u['/' + fname].get(int(h, 16), '?')
                                for h in re.findall(r'<([0-9A-Fa-f]{4})>', body)),
            })

    if not runs:
        die(f'contact line not found at y={CONTACT_LINE_Y}; template may have changed')
    if runs[0]['text'] != EXPECTED_CONTACT:
        die(f'contact run reads {runs[0]["text"]!r}, expected {EXPECTED_CONTACT!r}; '
            'nothing changed — update EXPECTED_CONTACT if the resume text changed')

    # Self-check: predict each run's x from the previous run's advance.
    for a, b in zip(runs, runs[1:]):
        predicted = a['x'] + width_of(a['font'], a['size'], a['body'])
        if abs(predicted - b['x']) > TOLERANCE:
            die(f'width model off by {predicted - b["x"]:.2f}px at {a["text"][:24]!r}; '
                'refusing to write a possibly-mangled PDF')

    # New first run, and how far everything shifts to stay centered.
    rev = u2g['/' + runs[0]['font']]
    missing = [c for c in REPLACEMENT if c not in rev]
    if missing:
        die(f'font lacks glyphs for {missing!r}; cannot render {REPLACEMENT!r}')
    new_body = ''.join(f'<{rev[c]:04X}>' for c in REPLACEMENT)
    delta = (width_of(runs[0]['font'], runs[0]['size'], runs[0]['body'])
             - width_of(runs[0]['font'], runs[0]['size'], new_body))

    # Rewrite from the end of the stream so earlier spans keep their offsets.
    out_stream = content

    for m in reversed([m for m in LINE_PATH.finditer(content)
                       if abs(float(m.group(2)) - UNDERLINE_Y) < 0.01]):
        x1, y1, x2, y2 = (float(g) for g in m.groups())
        repl = f'{x1 - delta / 2:.6f} {y1:.6f} m {x2 - delta / 2:.6f} {y2:.6f} l'
        out_stream = out_stream[:m.start()] + repl + out_stream[m.end():]

    for idx in range(len(runs) - 1, -1, -1):
        r = runs[idx]
        new_x = r['x'] + delta / 2 if idx == 0 else r['x'] - delta / 2
        body = new_body if idx == 0 else r['body']
        repl = (f'/{r["font"]} {r["size"]:.6f} Tf\n'
                f'1 0 0.000000 -1 {new_x:.6f} {CONTACT_LINE_Y:.6f} Tm\n'
                f'[{body}] TJ')
        out_stream = out_stream[:r['m'].start()] + repl + out_stream[r['m'].end():]

    writer = PdfWriter(clone_from=str(src))
    stream = DecodedStreamObject()
    stream.set_data(out_stream.encode('latin-1'))
    writer.pages[0].replace_contents(stream)
    writer.add_metadata({
        '/Title': 'Thomas J. Doolittle — Resume',
        '/Author': 'Thomas J. Doolittle',
        '/Producer': '', '/Creator': '', '/Keywords': '', '/Subject': '',
    })
    with open(out, 'wb') as fh:
        writer.write(fh)

    # Prove the sensitive strings are gone before declaring success.
    check = PdfReader(str(out))
    text = '\n'.join(p.extract_text() for p in check.pages)
    leaked = [s for s in ('7829', '(540)', '30316') if s in text]
    if leaked:
        die(f'wrote {out} but these still appear: {leaked} — do not publish')

    print(f'trim-resume: wrote {out}')
    print(f'  header now: {check.pages[0].extract_text().splitlines()[4].strip()}')
    print('  phone/ZIP removed, metadata cleared — commit and push resume.pdf')


if __name__ == '__main__':
    main()
