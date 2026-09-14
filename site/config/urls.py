"""URLconf for mdjango's self-hosted docs site — the canonical mount example (ADR 0006).

mdjango is mounted at the site **root** (this whole site is documentation, so it needs no ``/docs``
prefix). ``sitemap.xml`` and ``robots.txt`` are wired here, above the mdjango include, because both
are site-root resources the project owns — mdjango ships the :class:`DocsSitemap` class but not the
route (ADR 0007). This is exactly the wiring the docs tell a Consumer to add.
"""

from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from config.views import RobotsTxt
from mdjango.sitemaps import DocsSitemap

sitemaps = {"docs": DocsSitemap}

urlpatterns = [
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", RobotsTxt.as_view(), name="robots"),
    path("", include("mdjango.urls")),
]
