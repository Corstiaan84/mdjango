"""Sitemap + robots — the crawler surface (ADR 0007).

The harness (`site/config/urls.py`) mounts the `django.contrib.sitemaps` view at `/sitemap.xml`
and a `robots.txt`, exactly as the docs tell a Consumer to. These drive that wiring through the
test client; the pure export renderer is exercised directly.
"""

from __future__ import annotations

from datetime import date

from django.core.management import call_command

from mdjango.features.content.services import RegistryBuilder
from mdjango.sitemaps import render_sitemap_xml, sitemap_pages


def test_sitemap_lists_every_html_page(client):
    body = client.get("/sitemap.xml").content.decode()
    # the index page and ordinary pages, as absolute URLs (host from the request)
    assert "<loc>http://testserver/</loc>" in body
    assert "<loc>http://testserver/getting-started/quickstart/</loc>" in body
    assert "<loc>http://testserver/guides/networking/ingress/</loc>" in body
    # one <url> per HTML page: the root index + the 7 pages in nav order
    assert body.count("<url>") == 8


def test_sitemap_excludes_the_machine_artifacts(client):
    # the LLM artifacts, the search index and the .md alternates are not indexable pages
    body = client.get("/sitemap.xml").content.decode()
    assert "llms.txt" not in body
    assert "llms-full.txt" not in body
    assert "search-index.json" not in body
    assert ".md</loc>" not in body


def test_sitemap_emits_lastmod_only_for_pages_with_updated(client, settings, tmp_path):
    (tmp_path / "dated.md").write_text(
        "---\ntitle: Dated\nupdated: 2024-03-15\n---\n# Dated\n", encoding="utf-8"
    )
    (tmp_path / "plain.md").write_text("---\ntitle: Plain\n---\n# Plain\n", encoding="utf-8")
    settings.MDJANGO_CONTENT_DIR = tmp_path
    RegistryBuilder.clear_cache()

    body = client.get("/sitemap.xml").content.decode()
    assert "<lastmod>2024-03-15</lastmod>" in body
    # the plain page appears but carries no <lastmod>
    assert body.count("<url>") == 2
    assert body.count("<lastmod>") == 1


def test_robots_is_permissive_and_points_at_the_sitemap(client):
    r = client.get("/robots.txt")
    assert r.status_code == 200
    assert r["Content-Type"] == "text/plain"
    body = r.content.decode()
    assert "User-agent: *" in body
    assert "Allow: /" in body
    assert "Sitemap: http://testserver/sitemap.xml" in body


def test_export_writes_a_sitemap_at_the_dist_root_with_base_url(tmp_path):
    out = tmp_path / "dist"
    call_command("mdjango_build", str(out), base_url="https://docs.example.com")

    # a sitemap.xml is a site-root resource — it sits at the dist root, not under the mount
    sitemap = out / "sitemap.xml"
    assert sitemap.exists()
    xml = sitemap.read_text()
    assert "<loc>https://docs.example.com/</loc>" in xml  # the index page
    assert "<loc>https://docs.example.com/getting-started/quickstart/</loc>" in xml
    # machine artifacts stay out of the sitemap
    assert "llms.txt" not in xml
    assert "search-index.json" not in xml


def test_export_writes_no_sitemap_without_base_url(tmp_path):
    out = tmp_path / "dist"
    call_command("mdjango_build", str(out))
    assert not (out / "sitemap.xml").exists()


def test_export_renderer_builds_absolute_locs_and_iso_lastmod(tmp_path):
    (tmp_path / "dated.md").write_text(
        "---\ntitle: Dated\nupdated: 2024-03-15\n---\n# Dated\n", encoding="utf-8"
    )
    (tmp_path / "plain.md").write_text("---\ntitle: Plain\n---\n# Plain\n", encoding="utf-8")
    registry = RegistryBuilder(tmp_path).build()

    xml = render_sitemap_xml(sitemap_pages(registry), "https://docs.example.com/")

    assert xml.startswith('<?xml version="1.0" encoding="UTF-8"?>')
    # the trailing slash on base_url is normalised, not doubled
    assert "<loc>https://docs.example.com/dated/</loc>" in xml
    assert "<lastmod>2024-03-15</lastmod>" in xml
    # a page without `updated` carries a <loc> but no <lastmod>
    assert "<loc>https://docs.example.com/plain/</loc>" in xml
    assert xml.count("<lastmod>") == 1
    assert registry.get("dated").updated == date(2024, 3, 15)
