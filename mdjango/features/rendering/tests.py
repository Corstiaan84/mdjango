"""Rendering service: TOC extraction, permalinks, code-block wrapping, tables."""

from __future__ import annotations

from .services import Renderer


def test_headings_get_ids_and_permalinks():
    out = Renderer().render("# Title\n\n## First section\n\ntext")
    assert 'id="first-section"' in out.html
    assert 'class="headerlink"' in out.html


def test_toc_captures_h2_and_h3_only():
    md = "# Page\n\n## Two\n\n### Three\n\n#### Four\n\n## Another"
    out = Renderer().render(md)
    levels = [(t.level, t.id) for t in out.toc]
    assert levels == [(2, "two"), (3, "three"), (2, "another")]  # H1 and H4 excluded


def test_code_fence_is_wrapped_for_clipboard():
    out = Renderer().render("```bash\n$ walden up\n```\n")
    assert 'data-controller="clipboard"' in out.html
    assert "code-block" in out.html
    assert 'data-action="clipboard#copy"' in out.html
    assert "highlight" in out.html  # keeps Pygments' original classes


def test_tables_render():
    out = Renderer().render("| A | B |\n|---|---|\n| 1 | 2 |\n")
    assert "<table>" in out.html
    assert "<td>1</td>" in out.html


def test_inline_code_is_not_wrapped():
    out = Renderer().render("some `inline` code")
    assert "code-block" not in out.html
    assert "<code>inline</code>" in out.html
