"""Sitemap — the crawler-facing index of the docs (ADR 0007).

mdjango ships the :class:`Sitemap` class because it alone knows the page list (it is opaque behind
the registry); the Consumer owns the *route*, mounting the standard ``django.contrib.sitemaps``
view at **their** site root::

    # settings.py
    INSTALLED_APPS += ["django.contrib.sitemaps"]

    # urls.py
    from django.contrib.sitemaps.views import sitemap
    from mdjango.sitemaps import DocsSitemap

    path("sitemap.xml", sitemap, {"sitemaps": {"docs": DocsSitemap}}),

At runtime the domain comes from Django (the request, or the Sites framework) — mdjango needs no
base-URL setting. For the *static export*, which has no request, the domain is supplied as the
``mdjango_build --base-url`` flag and :func:`render_sitemap_xml` builds the file directly.

Placement note (ADR 0007): this is HTTP-coupled (contrib.sitemaps reads ``request`` for the host),
which by ADR 0002's logic would put it under ``views/common/``. It lives at the package top level
anyway, because a ``Sitemap`` is a framework-defined artifact with a canonical import path
(``from mdjango.sitemaps import DocsSitemap``) that every Django developer expects.
"""

from __future__ import annotations

from datetime import date
from xml.sax.saxutils import escape

from django.contrib.sitemaps import Sitemap

from .features.content.dtos import Page, Registry
from .features.content.services import RegistryBuilder
from .views import page_url


def sitemap_pages(registry: Registry) -> list[Page]:
    """The addressable HTML Pages, in nav order — the one definition of "what's in the sitemap".

    The index Page (root ``_index.md``, path ``""``) is kept out of ``ordered_pages`` and re-added
    here at the front. The LLM artifacts, the search index, and the ``.md`` alternates are *not*
    pages a search engine indexes, so they are excluded. Drafts are already filtered out of
    ``ordered_pages`` by config. Reused by both :class:`DocsSitemap` (runtime) and the export.
    """
    pages = list(registry.ordered_pages)
    if registry.index_page is not None:
        pages.insert(0, registry.index_page)
    return pages


class DocsSitemap(Sitemap):
    """A ``django.contrib.sitemaps.Sitemap`` over the docs. ``location`` is the page's on-site path
    (contrib.sitemaps prepends scheme + host from the request); ``lastmod`` is the author-set
    ``updated`` date, omitted for pages that don't set one. No ``changefreq``/``priority`` — search
    engines ignore them for a docs tree of this size."""

    def items(self) -> list[Page]:
        return sitemap_pages(RegistryBuilder.cached())

    def location(self, page: Page) -> str:
        return page_url(page)

    def lastmod(self, page: Page) -> date | None:
        return page.updated


def render_sitemap_xml(pages: list[Page], base_url: str) -> str:
    """Render a sitemaps.org ``urlset`` with absolute ``<loc>`` URLs, for the static export.

    The export has no request to derive a host from, so ``base_url`` (the ``--base-url`` build
    flag, e.g. ``https://docs.example.com``) supplies the scheme + domain; each ``<loc>`` is
    ``base_url`` + the page's on-site path. ``<lastmod>`` is emitted only for pages with an
    ``updated`` date.
    """
    base = base_url.rstrip("/")
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for page in pages:
        loc = escape(base + page_url(page))
        if page.updated is not None:
            lines.append(
                f"  <url><loc>{loc}</loc><lastmod>{page.updated.isoformat()}</lastmod></url>"
            )
        else:
            lines.append(f"  <url><loc>{loc}</loc></url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"
