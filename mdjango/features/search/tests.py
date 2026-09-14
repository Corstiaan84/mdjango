"""Search service: HTML stripping and index building over synthetic content trees."""

from __future__ import annotations

from ..content.services import RegistryBuilder
from .services import SearchIndexer


def test_strip_html_reduces_to_text():
    html = '<h2 id="x">Deploy <a class="headerlink">#</a></h2><p>Run <code>walden up</code>.</p>'
    text = SearchIndexer.strip_html(html)
    assert "Deploy" in text
    assert "walden up" in text
    assert "<" not in text and ">" not in text


def write(root, rel, text):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def test_index_has_one_entry_per_page_with_fields(tmp_path, settings):
    write(tmp_path, "guides/_index.md", "---\ntitle: Guides\n---\n")
    write(tmp_path, "guides/deploy.md", "---\ntitle: Deploy\n---\n# Deploy\n\nRun `walden up`.")
    write(tmp_path, "_index.md", "---\ntitle: Home\n---\n# Home\n\nWelcome.")
    reg = RegistryBuilder(tmp_path).build()

    index = SearchIndexer(reg).build()
    by_title = {e["title"]: e for e in index}
    assert set(by_title) == {"Home", "Deploy"}
    deploy = by_title["Deploy"]
    assert deploy["section"] == "Guides"
    assert "walden up" in deploy["text"]  # full body text, not just the description
    assert deploy["url"].endswith("/guides/deploy/")
    assert by_title["Home"]["url"] == "/"  # the index page (mounted at root)
