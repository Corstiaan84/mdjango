"""Guarantees about the assets a page actually pulls down.

These are static reads of the shipped files rather than behavioural tests, because the failures
they catch are invisible: the page still works, it just costs more to load than it should.
"""

from __future__ import annotations

import re
from pathlib import Path

STATIC = Path(__file__).resolve().parent.parent / "static" / "mdjango"
SEARCH_CONTROLLER = STATIC / "controllers" / "search_controller.js"

# `import x from "y"` / `import "y"` at the top level — the form that makes the module a hard
# dependency of the page, as opposed to `import("y")`, which is a request made when it is needed.
_STATIC_IMPORT = re.compile(r"""^\s*import\s+(?:[^;'"]*\sfrom\s+)?["']([^"']+)["']""", re.M)


def test_the_search_index_library_is_not_pulled_into_every_page_view():
    """MiniSearch is the largest thing the shell loads after the fonts (~19KB gzipped) and most
    readers never open the palette. A static import made every page view pay for it."""
    src = SEARCH_CONTROLLER.read_text(encoding="utf-8")
    eager = _STATIC_IMPORT.findall(src)
    assert "minisearch" not in eager, (
        f"minisearch is statically imported, so it loads on every page view: {eager}"
    )
    assert 'import("minisearch")' in src, "the lazy import is gone; search will not work"


def test_the_search_controller_still_loads_stimulus_eagerly():
    """The controller itself is small and must register with Stimulus on load — only the search
    library is deferred, so this pins the distinction rather than 'no static imports'."""
    assert "@hotwired/stimulus" in _STATIC_IMPORT.findall(
        SEARCH_CONTROLLER.read_text(encoding="utf-8")
    )
