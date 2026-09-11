#!/usr/bin/env python3
"""Combine the theme's stylesheets into the one that ships.

It concatenates the sources, removes `/* … */` comments, and drops the blank lines that removing
them leaves behind. That is all. It does not trim indentation, collapse whitespace inside
declarations, reorder or merge rules, shorten colours, or touch anything inside a quoted string
(which matters: the nav caret is `content: "\\25B8"`). Every transformation is one a human could do
by hand and check by eye.

Why bother at all: comments are **40% of the authored source** — deliberately, since they carry the
reasoning for the colour ramps, the measure cap and the `<details>` gap — and the stylesheet is the
only asset that blocks first paint. Removing them takes the sheet from 8,224 to 3,603 bytes
gzipped. Nothing else is worth doing: trimming indentation as well would save a further 100 bytes
and cost the readable output anyone debugging in devtools actually reads (docs/adr/0005).

    python3 theme/bundle.py src/a.css src/b.css > out.css
"""

from __future__ import annotations

import sys
from pathlib import Path


def strip_comments(css: str) -> str:
    """Remove CSS comments, leaving string literals untouched."""
    out: list[str] = []
    i, n = 0, len(css)
    while i < n:
        if css.startswith("/*", i):
            end = css.find("*/", i + 2)
            i = n if end == -1 else end + 2
            continue
        if css[i] in "\"'":
            quote, j = css[i], i + 1
            while j < n and css[j] != quote:
                j += 2 if css[j] == "\\" else 1
            out.append(css[i : j + 1])
            i = j + 1
            continue
        out.append(css[i])
        i += 1
    return "".join(out)


def bundle(sources: list[str]) -> str:
    """The shipped stylesheet, from the source files' contents in order."""
    css = strip_comments("\n".join(sources))
    return "\n".join(line for line in css.split("\n") if line.strip()) + "\n"


def main(paths: list[str]) -> int:
    if not paths:
        print(__doc__, file=sys.stderr)
        return 2
    sys.stdout.write(bundle([Path(p).read_text(encoding="utf-8") for p in paths]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
