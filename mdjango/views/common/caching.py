"""Response caching — cross-cutting view plumbing (mdjango ADR 0002).

Two layers, both keyed on the fact that a docs page is the *same bytes for every visitor* (no
users, no per-request state — ADR 0001):

1. **Server-side page cache.** The heavy views memoise their rendered HTML string in Django's cache
   (LocMemCache by default) so a repeat request skips the markdown + Pygments + template pass.
2. **HTTP caching headers.** Every GET carries a strong ``ETag`` (so a conditional request can 304)
   and a ``Cache-Control`` — ``public, max-age`` when caching is on, ``no-cache`` otherwise — so
   browsers and CDNs can cache without touching Django at all.

Both are governed by ``MDJANGO_CACHE_SECONDS`` (``conf.cache_seconds``) and are switched off
whenever the registry is being rebuilt per request (``always_rebuild`` — i.e. ``DEBUG``), so edits
show up immediately in development. This lives under ``views/common/`` because it is HTTP-coupled
(it touches ``request``/``HttpResponse`` and sets headers) — the service layer stays interface-
agnostic.
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable

from django.core.cache import cache
from django.http import HttpResponse, HttpResponseNotModified

from ...conf import Conf, get_conf
from ...features.content.dtos import Page

_KEY_PREFIX = "mdjango:page:"


class ResponseCache:
    """Cache rendered pages and stamp HTTP caching headers on docs responses."""

    def __init__(self, conf: Conf | None = None):
        self.conf = conf or get_conf()

    @property
    def enabled(self) -> bool:
        """Caching is off while the registry rebuilds per request, or when explicitly disabled."""
        return bool(self.conf.cache_seconds) and not self.conf.always_rebuild

    def cached_html(self, page: Page, render_html: Callable[[Page], str]) -> str:
        """The page's rendered HTML, from cache when enabled, otherwise freshly rendered."""
        if not self.enabled:
            return render_html(page)
        key = _KEY_PREFIX + (page.path or "@index")
        html = cache.get(key)
        if html is None:
            html = render_html(page)
            cache.set(key, html, self.conf.cache_seconds)
        return html

    def finalize(self, request, response: HttpResponse) -> HttpResponse:
        """Add ``ETag`` + ``Cache-Control``; return a 304 if the client's copy is still current."""
        etag = f'"{hashlib.md5(response.content, usedforsecurity=False).hexdigest()}"'
        cache_control = self._cache_control()
        if request.headers.get("If-None-Match") == etag:
            response = HttpResponseNotModified()
        response.headers["ETag"] = etag
        response.headers["Cache-Control"] = cache_control
        return response

    def _cache_control(self) -> str:
        if not self.enabled:
            return "no-cache"
        return f"public, max-age={self.conf.cache_seconds}"
