"""URLconf for mdjango's self-hosted docs site — the canonical mount example (ADR 0006).

mdjango is mounted at the site **root** (this whole site is documentation, so it needs no ``/docs``
prefix). ``sitemap.xml`` and ``robots.txt`` are wired here, above the mdjango include, because both
are site-root resources the project owns — mdjango ships the :class:`DocsSitemap` class but not the
route (ADR 0007). This is exactly the wiring the docs tell a Consumer to add.
"""

from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.urls import include, path
from django.views import View

from mdjango.sitemaps import DocsSitemap

sitemaps = {"docs": DocsSitemap}


class RobotsTxt(View):
    """Serve a permissive ``robots.txt`` with an absolute ``Sitemap:`` line built from the request.

    The LLM artifacts and search index are left crawlable — duplicate-content dilution is a
    non-issue for docs, and the llms.txt convention wants those reachable (ADR 0007).
    """

    def get(self, request):
        sitemap_url = request.build_absolute_uri("/sitemap.xml")
        body = f"User-agent: *\nAllow: /\n\nSitemap: {sitemap_url}\n"
        return HttpResponse(body, content_type="text/plain")


urlpatterns = [
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", RobotsTxt.as_view(), name="robots"),
    path("", include("mdjango.urls")),
]
