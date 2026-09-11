"""Consumer-facing configuration.

Every knob is a Django setting read lazily through :func:`get_conf`, so a consumer configures
mdjango the same way they configure the rest of their project — in ``settings.py``. Nothing here
touches the *theme* override surface (the five CSS seeds); that is set in the template/CSS layer,
per ADR 0003. These settings drive the **shell**: what the chrome says and links to.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


@dataclass(frozen=True)
class HeaderLink:
    """One optional link in the header nav (beside github)."""

    label: str
    url: str


@dataclass(frozen=True)
class Conf:
    """Resolved mdjango configuration — read from Django settings on each :func:`get_conf` call."""

    content_dir: Path
    # Shell / branding (ADR 0003 §3) — all display-only.
    brand: str
    home_url: str
    version: str
    github_url: str
    header_links: tuple[HeaderLink, ...] = field(default_factory=tuple)
    site_title: str = ""
    # One-line site summary — the blockquote in the LLM artifacts (llms.txt / llms-full.txt).
    description: str = ""
    # LLM docs — the llms.txt / llms-full.txt / per-page .md surface: generation, routes, and
    # the header + sidebar links. Default on; MDJANGO_LLM_DOCS=False darkens the whole surface.
    llm_docs: bool = True
    # Content behaviour.
    include_drafts: bool = False
    # Dev ergonomics: rebuild the registry on every request instead of once.
    always_rebuild: bool = False
    # Response caching (mdjango ADR 0002). Seconds for the server-side page cache *and* the
    # `Cache-Control: public, max-age` header; 0 disables both (headers become `no-cache`).
    cache_seconds: int = 300

    @property
    def title(self) -> str:
        """The string for ``<title>`` — an explicit ``MDJANGO_SITE_TITLE`` or the brand."""
        return self.site_title or self.brand


def _get(name: str, default):
    return getattr(settings, name, default)


def get_conf() -> Conf:
    """Read mdjango's settings into a :class:`Conf`.

    ``MDJANGO_CONTENT_DIR`` is the only required setting; the rest have sensible defaults so a
    consumer gets a working (if unbranded) site from a single line.
    """
    raw_dir = _get("MDJANGO_CONTENT_DIR", None)
    if not raw_dir:
        raise ImproperlyConfigured(
            "MDJANGO_CONTENT_DIR is required — set it to the directory holding your markdown tree."
        )
    content_dir = Path(raw_dir)

    raw_links = _get("MDJANGO_HEADER_LINKS", ())
    links = tuple(
        link if isinstance(link, HeaderLink) else HeaderLink(link["label"], link["url"])
        for link in raw_links
    )

    return Conf(
        content_dir=content_dir,
        brand=_get("MDJANGO_BRAND", "docs"),
        home_url=_get("MDJANGO_HOME_URL", "/"),
        version=_get("MDJANGO_VERSION", ""),
        github_url=_get("MDJANGO_GITHUB_URL", ""),
        header_links=links,
        site_title=_get("MDJANGO_SITE_TITLE", ""),
        description=_get("MDJANGO_DESCRIPTION", ""),
        llm_docs=bool(_get("MDJANGO_LLM_DOCS", True)),
        include_drafts=bool(_get("MDJANGO_INCLUDE_DRAFTS", _get("DEBUG", False))),
        always_rebuild=bool(_get("MDJANGO_ALWAYS_REBUILD", _get("DEBUG", False))),
        cache_seconds=int(_get("MDJANGO_CACHE_SECONDS", 300)),
    )
