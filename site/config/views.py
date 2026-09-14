"""Project-level views for the docs harness — cross-cutting pages that belong to no feature.

Kept out of ``config/urls.py`` (which only wires routes) per the stack's view-layering rule. A
``robots.txt`` is a class-based view like any other; it just belongs to the project (which owns the
site root) rather than to mdjango.
"""

from __future__ import annotations

from django.http import HttpResponse
from django.views import View


class RobotsTxt(View):
    """Serve a permissive ``robots.txt`` with an absolute ``Sitemap:`` line built from the request.

    The LLM artifacts and search index are left crawlable — duplicate-content dilution is a
    non-issue for docs, and the llms.txt convention wants those reachable (ADR 0007).
    """

    def get(self, request):
        sitemap_url = request.build_absolute_uri("/sitemap.xml")
        body = f"User-agent: *\nAllow: /\n\nSitemap: {sitemap_url}\n"
        return HttpResponse(body, content_type="text/plain")
