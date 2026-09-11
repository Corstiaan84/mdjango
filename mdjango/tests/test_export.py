"""End-to-end: the mdjango_build command over the example content."""

from __future__ import annotations

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError


def test_build_exports_a_self_contained_dist(tmp_path):
    out = tmp_path / "dist"
    call_command("mdjango_build", str(out))

    # dir-per-page, mirroring the live URL tree
    assert (out / "docs" / "index.html").exists()
    assert (out / "docs" / "getting-started" / "quickstart" / "index.html").exists()
    # the search index, served as a file
    assert (out / "docs" / "search-index.json").exists()
    # vendored assets copied under the static prefix
    assert (out / "static" / "mdjango" / "mdjango.css").exists()
    assert (out / "static" / "mdjango" / "application.js").exists()

    html = (out / "docs" / "getting-started" / "quickstart" / "index.html").read_text()
    assert "Quickstart" in html
    assert 'data-search-index-url="/docs/search-index.json"' in html


def test_build_writes_the_llm_artifacts(tmp_path):
    out = tmp_path / "dist"
    call_command("mdjango_build", str(out))

    # the two site-wide artifacts
    assert (out / "docs" / "llms.txt").read_text().startswith("# walden docs")
    assert "podman volume" in (out / "docs" / "llms-full.txt").read_text()
    # per-page markdown, mirroring the HTML tree (incl. the landing at index.md)
    assert (out / "docs" / "index.md").exists()
    page_md = (out / "docs" / "getting-started" / "quickstart.md").read_text()
    assert page_md.startswith("# Quickstart")


def test_check_passes_on_valid_content():
    call_command("mdjango_build", check=True)  # must not raise


def test_check_fails_on_a_bad_tree(tmp_path, settings):
    bad = tmp_path / "content"
    (bad / "s" / "sub" / "deeper").mkdir(parents=True)  # a fourth level (ADR 0004)
    (bad / "s" / "sub" / "deeper" / "x.md").write_text("x", encoding="utf-8")
    settings.MDJANGO_CONTENT_DIR = bad
    with pytest.raises(CommandError):
        call_command("mdjango_build", check=True)


def test_llm_docs_off_skips_the_llm_artifacts(tmp_path, settings):
    settings.MDJANGO_LLM_DOCS = False
    out = tmp_path / "dist"
    call_command("mdjango_build", str(out))

    # pages + the search index are still written; the whole markdown/llm surface is not
    assert (out / "docs" / "index.html").exists()
    assert (out / "docs" / "search-index.json").exists()
    assert not (out / "docs" / "llms.txt").exists()
    assert not (out / "docs" / "llms-full.txt").exists()
    assert not (out / "docs" / "index.md").exists()
    assert not (out / "docs" / "getting-started" / "quickstart.md").exists()
