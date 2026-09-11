"""Search service — build the client-side search index from the registry.

:class:`SearchIndexer` produces a flat list of ``{id, title, section, text, url}`` documents (each
page rendered and stripped to plain text) and owns its build-once cache. The index is served two
ways from the *same* build (ADR 0001): a runtime view returns it as JSON, and the static-export
command writes it to a file. The client (MiniSearch) fetches it lazily on first search.
"""

from __future__ import annotations

import html as htmllib
import re

from django.urls import reverse

from ...conf import get_conf
from ..content.dtos import Page, Registry
from ..content.services import RegistryBuilder
from ..rendering.services import Renderer

_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")


class SearchIndexer:
    """The search service: turn a :class:`Registry` into MiniSearch documents."""

    _cache: list[dict] | None = None

    def __init__(self, registry: Registry):
        self.registry = registry
        self._renderer = Renderer()

    def build(self) -> list[dict]:
        """Build the search documents from every non-draft page (+ the index page)."""
        entries: list[dict] = []
        if self.registry.index_page is not None:
            entries.append(self._entry(self.registry.index_page))
        entries += [self._entry(page) for page in self.registry.ordered_pages]
        return entries

    @staticmethod
    def _trail(page: Page) -> str:
        """A page's ancestor trail, ``"Section / Subsection"`` (ADR 0004 §6). The leaf group alone
        would be ambiguous across sections; the top section alone would discard the grouping."""
        return " / ".join(g.title for g in page.groups)

    def _entry(self, page: Page) -> dict:
        url = (
            reverse("mdjango:index")
            if page.path == ""
            else reverse("mdjango:page", args=[page.path])
        )
        return {
            "id": page.path,
            "title": page.title,
            "section": self._trail(page),
            "text": self.strip_html(self._renderer.render(page.body).html),
            "url": url,
        }

    @staticmethod
    def strip_html(html: str) -> str:
        """Reduce rendered HTML to searchable plain text."""
        text = _TAG.sub(" ", html)
        text = htmllib.unescape(text)
        return _WS.sub(" ", text).strip()

    # --- build-once cache ----------------------------------------------------------------------

    @classmethod
    def cached(cls) -> list[dict]:
        if cls._cache is None or get_conf().always_rebuild:
            cls._cache = cls(RegistryBuilder.cached()).build()
        return cls._cache

    @classmethod
    def clear_cache(cls) -> None:
        cls._cache = None
