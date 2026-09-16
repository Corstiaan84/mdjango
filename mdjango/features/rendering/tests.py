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


# --- asset src/href rewriting (ADR 0008) ---------------------------------------------------------


def _resolver(known):
    """A stub asset resolver: a tree path in ``known`` maps to a served URL, else None."""
    return lambda tree_path: f"/docs/{tree_path}" if tree_path in known else None


def test_no_resolver_leaves_images_untouched():
    out = Renderer().render("![alt](diagram.png)")
    assert 'src="diagram.png"' in out.html  # default: pure pass-through, as before


def test_relative_image_resolving_to_an_asset_is_rewritten():
    r = Renderer(asset_resolver=_resolver({"how-to/diagram.png"}), page_dir="how-to")
    out = r.render("![alt](diagram.png)")
    assert 'src="/docs/how-to/diagram.png"' in out.html


def test_relative_image_not_an_asset_is_left_as_written():
    r = Renderer(asset_resolver=_resolver(set()), page_dir="how-to")
    out = r.render("![alt](typo.png)")
    assert 'src="typo.png"' in out.html


def test_absolute_and_external_srcs_are_untouched():
    r = Renderer(asset_resolver=_resolver({"how-to/x.png"}), page_dir="how-to")
    md = "![a](/static/x.png)\n\n![b](https://e.test/x.png)"
    out = r.render(md)
    assert 'src="/static/x.png"' in out.html
    assert 'src="https://e.test/x.png"' in out.html


def test_reference_escaping_the_root_is_untouched():
    r = Renderer(asset_resolver=_resolver({"x.png"}), page_dir="a")
    out = r.render("![a](../../x.png)")  # normalises to ../x.png — outside the tree
    assert "../../x.png" in out.html


def test_link_to_an_asset_is_rewritten_for_click_to_enlarge():
    # `<a href>` to an Asset is rewritten (the enlarge idiom); a link to a Page is not — an
    # extensionless page path never resolves to an Asset.
    r = Renderer(asset_resolver=_resolver({"how-to/full.png"}), page_dir="how-to")
    out = r.render("[big](full.png) and [next](../other-page/)")
    assert 'href="/docs/how-to/full.png"' in out.html
    assert 'href="../other-page/"' in out.html


def test_raw_html_image_is_rewritten():
    # The gallery is authored as raw-HTML <figure> groups; the output pass must reach those <img>s
    # even though md_in_html stashes the raw block rather than parsing it into elements.
    r = Renderer(asset_resolver=_resolver({"how-to/shot.png"}), page_dir="how-to")
    out = r.render('<figure><a href="shot.png"><img src="shot.png" alt="x"></a></figure>')
    assert 'src="/docs/how-to/shot.png"' in out.html
    assert 'href="/docs/how-to/shot.png"' in out.html
