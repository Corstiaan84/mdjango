"""End-to-end: the mdjango_build command over the fixture content tree (see conftest.py)."""

from __future__ import annotations

from io import StringIO

import pytest
from django.contrib.staticfiles.finders import get_finder
from django.core.management import call_command
from django.core.management.base import CommandError


def test_build_exports_a_self_contained_dist(tmp_path):
    out = tmp_path / "dist"
    call_command("mdjango_build", str(out))

    # dir-per-page, mirroring the live URL tree
    assert (out / "index.html").exists()
    assert (out / "getting-started" / "quickstart" / "index.html").exists()
    # the search index, served as a file
    assert (out / "search-index.json").exists()
    # vendored assets copied under the static prefix
    assert (out / "static" / "mdjango" / "mdjango.css").exists()
    assert (out / "static" / "mdjango" / "application.js").exists()

    html = (out / "getting-started" / "quickstart" / "index.html").read_text()
    assert "Quickstart" in html
    assert 'data-search-index-url="/search-index.json"' in html


def test_build_writes_the_llm_artifacts(tmp_path):
    out = tmp_path / "dist"
    call_command("mdjango_build", str(out))

    # the two site-wide artifacts
    assert (out / "llms.txt").read_text().startswith("# Fixture Docs")
    assert "podman volume" in (out / "llms-full.txt").read_text()
    # per-page markdown, mirroring the HTML tree (incl. the landing at index.md)
    assert (out / "index.md").exists()
    page_md = (out / "getting-started" / "quickstart.md").read_text()
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


def test_build_copies_extra_css_into_the_dist(tmp_path, settings):
    """The runtime serves the consumer's theme sheet through their Django; the export has no
    collectstatic, so it must resolve each MDJANGO_EXTRA_CSS name and copy the file itself —
    otherwise the <link> it emits would 404 in the dist."""
    brand = tmp_path / "brandstatic"
    (brand / "acme").mkdir(parents=True)
    (brand / "acme" / "theme.css").write_text(":root{--accent:#f00}", encoding="utf-8")
    settings.STATICFILES_DIRS = [brand]
    get_finder.cache_clear()  # FileSystemFinder snapshots STATICFILES_DIRS at instantiation
    settings.MDJANGO_EXTRA_CSS = ("acme/theme.css",)

    out = tmp_path / "dist"
    call_command("mdjango_build", str(out))

    # the file rides along under the same static prefix the <link> resolves to
    assert (out / "static" / "acme" / "theme.css").read_text() == ":root{--accent:#f00}"
    html = (out / "index.html").read_text()
    assert '<link rel="stylesheet" href="/static/acme/theme.css">' in html


def test_build_warns_on_an_unresolved_extra_css_but_still_exports(tmp_path, settings):
    """A name the finders can't resolve is surfaced, not silent (the failure mode this whole hook
    exists to avoid), and the rest of the export still succeeds."""
    settings.MDJANGO_EXTRA_CSS = ("nope/missing.css",)
    out = tmp_path / "dist"
    err = StringIO()
    call_command("mdjango_build", str(out), stderr=err)

    assert (out / "index.html").exists()
    assert not (out / "static" / "nope" / "missing.css").exists()
    assert "MDJANGO_EXTRA_CSS" in err.getvalue() and "missing.css" in err.getvalue()


def test_llm_docs_off_skips_the_llm_artifacts(tmp_path, settings):
    settings.MDJANGO_LLM_DOCS = False
    out = tmp_path / "dist"
    call_command("mdjango_build", str(out))

    # pages + the search index are still written; the whole markdown/llm surface is not
    assert (out / "index.html").exists()
    assert (out / "search-index.json").exists()
    assert not (out / "llms.txt").exists()
    assert not (out / "llms-full.txt").exists()
    assert not (out / "index.md").exists()
    assert not (out / "getting-started" / "quickstart.md").exists()
