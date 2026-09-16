"""Runtime serving — the docs view adapters (HTTP layer).

The HTML pages (index + page) resolve a :class:`Page` from the registry, then render the shared
shell template with a fully-built context — the generated nav, breadcrumb, TOC, and prev/next pager
(ADR 0003 §3) — through :class:`ResponseCache`, which memoises the HTML and stamps caching headers
(ADR 0002). Three machine-readable adapters sit beside them (all from the *same* registry, ADR
0001): the search index (JSON), the two ``llms.txt`` artifacts, and per-page markdown. No business
logic here; the static-export command reuses :func:`page_context` / :func:`render_page_html`.
"""

from __future__ import annotations

import mimetypes
from collections.abc import Callable
from pathlib import Path

from django.http import Http404, HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import View

from ..conf import Conf, get_conf
from ..features.content.dtos import Asset, Page, Registry, Subsection
from ..features.content.services import RegistryBuilder
from ..features.llm.services import LlmArtifactBuilder
from ..features.rendering.services import Renderer
from ..features.search.services import SearchIndexer
from .common.caching import ResponseCache

TEMPLATE = "mdjango/page.html"
MARKDOWN_CONTENT_TYPE = "text/markdown; charset=utf-8"


def page_url(page: Page) -> str:
    if page.path == "":
        return reverse("mdjango:index")
    return reverse("mdjango:page", args=[page.path])


def page_markdown_url(page: Page) -> str:
    """The URL of a page's raw-markdown (``.md``) alternate."""
    if page.path == "":
        return reverse("mdjango:index_markdown")
    return reverse("mdjango:page_markdown", args=[page.path])


def asset_url(asset: Asset) -> str:
    """The served URL of a content-tree Asset — the mount prefix + its tree path (ADR 0008)."""
    return reverse("mdjango:asset", args=[asset.path])


def _page_tree_dir(registry: Registry, page: Page) -> str:
    """The page's directory within the content tree, as a POSIX string ("" at the root).

    A page's relative ``<img>`` references resolve against this, so it is the *filesystem* dir (real
    directory names), not the slugified URL path — the two can diverge, and an Asset lives on disk.
    """
    try:
        rel = page.source.relative_to(registry.root)
    except ValueError:
        return ""
    parent = rel.parent
    return "" if parent == Path(".") else parent.as_posix()


def asset_resolver(registry: Registry) -> Callable[[str], str | None]:
    """Build the renderer's seam: a tree-path → served-URL map, ``None`` for a non-Asset.

    This is where the mount prefix (``reverse``) enters, so the renderer never touches HTTP — it
    resolves a relative ``src`` to a tree path and asks this callable whether that is a known Asset
    and, if so, at what URL.
    """

    def resolve(tree_path: str) -> str | None:
        asset = registry.get_asset(tree_path)
        return asset_url(asset) if asset is not None else None

    return resolve


def _nav_link(page: Page, current_path: str) -> dict:
    return {
        "kind": "link",
        "title": page.title,
        "url": page_url(page),
        "active": page.path == current_path,
    }


def _nav_subgroup(subsection: Subsection, current_path: str) -> dict:
    """A collapsible subsection. ``open`` is a pure function of the current page — it has to be:
    :class:`ResponseCache` keys rendered HTML on ``page.path`` and serves the same bytes to every
    visitor, so per-visitor open state cannot be rendered server-side at all (ADR 0004 §5)."""
    items = [_nav_link(p, current_path) for p in subsection.pages]
    return {
        "kind": "subgroup",
        "title": subsection.title,
        "open": any(item["active"] for item in items),
        "items": items,
    }


def build_nav(registry: Registry, current_path: str) -> list[dict]:
    """The left section-nav: a list of groups, each holding page links and collapsible subgroups.

    Root loose pages interleave with sections by weight (ADR 0004 §4), so a run of them is
    coalesced into one untitled group sitting at its weight position — that keeps the top level of
    the nav uniform while the *inside* of a group is a link-or-subgroup mix.
    """
    nav: list[dict] = []
    for child in registry.children:
        if isinstance(child, Page):
            link = _nav_link(child, current_path)
            if nav and nav[-1]["loose"]:
                nav[-1]["items"].append(link)
            else:
                nav.append({"title": "", "loose": True, "items": [link]})
            continue
        items = [
            _nav_subgroup(item, current_path)
            if isinstance(item, Subsection)
            else _nav_link(item, current_path)
            for item in child.children
        ]
        nav.append({"title": child.title, "loose": False, "items": items})
    return nav


def build_breadcrumb(conf: Conf, page: Page) -> list[dict]:
    """The header trail: Section / Subsection / Page (ADR 0004 §6). No crumb is a link — groups
    have no URL of their own."""
    crumbs = [{"label": group.title, "url": ""} for group in page.groups]
    if page.path != "":
        crumbs.append({"label": page.title, "url": ""})
    return crumbs


def build_eyebrow(page: Page) -> str:
    """The label above the article's H1: the page's *innermost* group.

    The header breadcrumb already carries the whole trail, so the eyebrow stays the short, single
    label the design mock shows rather than repeating it.
    """
    return page.groups[-1].title if page.groups else ""


def page_context(page: Page) -> dict:
    """The full template context for one page. Shared by runtime views and static export."""
    registry = RegistryBuilder.cached()
    conf = get_conf()
    rendered = Renderer(
        asset_resolver=asset_resolver(registry),
        page_dir=_page_tree_dir(registry, page),
    ).render(page.body)
    prev, nxt = registry.neighbours(page)
    # The Index page is kept out of the section-nav (registry.children) and re-enters here as the
    # Home link: a pinned link at the top of the left nav, present only when a root _index.md is.
    home = _nav_link(registry.index_page, page.path) if registry.index_page is not None else None
    return {
        "conf": conf,
        "page": page,
        "article_html": rendered.html,
        "toc": rendered.toc,
        "home": home,
        "nav": build_nav(registry, page.path),
        "breadcrumb": build_breadcrumb(conf, page),
        "eyebrow": build_eyebrow(page),
        "prev": prev,
        "next": nxt,
        "prev_url": page_url(prev) if prev else "",
        "next_url": page_url(nxt) if nxt else "",
        "page_md_url": page_markdown_url(page) if conf.llm_docs else "",
    }


def render_page_html(page: Page) -> str:
    """Render a page to a full HTML string. Shared by runtime views and the static export, so the
    two outputs cannot drift (ADR 0001)."""
    return render_to_string(TEMPLATE, page_context(page))


def resolve_page(page_path: str) -> Page:
    """Registry lookup with the HTTP mapping: unknown path -> 404. ``""`` is the landing page —
    the explicit ``_index.md`` or, failing that, the first page in nav order."""
    registry = RegistryBuilder.cached()
    if page_path == "":
        page = registry.index_page or (
            registry.ordered_pages[0] if registry.ordered_pages else None
        )
        if page is None:
            raise Http404("no documentation content")
        return page
    page = registry.get(page_path)
    if page is None:
        raise Http404(f"no such page: {page_path}")
    return page


class CachedPageView(View):
    """Serve one docs page's HTML through the response cache (ADR 0002); subclasses resolve it."""

    def get(self, request, **kwargs) -> HttpResponse:
        page = self.get_page(**kwargs)
        cache = ResponseCache()
        html = cache.cached_html(page, render_page_html)
        return cache.finalize(request, HttpResponse(html))

    def get_page(self, **kwargs) -> Page:
        raise NotImplementedError


class DocsIndexView(CachedPageView):
    def get_page(self, **kwargs) -> Page:
        return resolve_page("")


class DocsPageView(CachedPageView):
    def get_page(self, page_path, **kwargs) -> Page:
        return resolve_page(page_path)


class SearchIndexView(View):
    """Serve the client-side search index as JSON. The static export writes the same index to a
    file, so runtime and export search are identical (ADR 0001)."""

    def get(self, request) -> HttpResponse:
        cache = ResponseCache()
        return cache.finalize(request, JsonResponse(SearchIndexer.cached(), safe=False))


class RequireLlmDocs:
    """404 the LLM/markdown endpoints when ``MDJANGO_LLM_DOCS`` is off.

    The whole markdown surface (``llms.txt``, ``llms-full.txt``, ``index.md``, per-page
    ``.md``) is one feature toggled as a unit. The gate is HTTP (``Http404``), so it lives in
    the view layer, not the service — services stay interface-agnostic (see conventions).
    """

    def dispatch(self, request, *args, **kwargs):
        if not get_conf().llm_docs:
            raise Http404("llm docs are disabled")
        return super().dispatch(request, *args, **kwargs)


class LlmsTxtView(RequireLlmDocs, View):
    """Serve ``llms.txt`` — the curated, per-section index of the docs (ADR 0001)."""

    def get(self, request) -> HttpResponse:
        cache = ResponseCache()
        body = LlmArtifactBuilder.cached().index
        return cache.finalize(request, HttpResponse(body, content_type=MARKDOWN_CONTENT_TYPE))


class LlmsFullView(RequireLlmDocs, View):
    """Serve ``llms-full.txt`` — every page's markdown concatenated in nav order (ADR 0001)."""

    def get(self, request) -> HttpResponse:
        cache = ResponseCache()
        body = LlmArtifactBuilder.cached().full
        return cache.finalize(request, HttpResponse(body, content_type=MARKDOWN_CONTENT_TYPE))


class PageMarkdownView(RequireLlmDocs, View):
    """Serve one page's raw markdown (the ``.md`` alternate a page's ``<link>`` points at)."""

    def get(self, request, page_path="") -> HttpResponse:
        page = resolve_page(page_path)
        body = LlmArtifactBuilder(RegistryBuilder.cached()).page_markdown(page)
        cache = ResponseCache()
        return cache.finalize(request, HttpResponse(body, content_type=MARKDOWN_CONTENT_TYPE))


class AssetView(View):
    """Serve one content-tree Asset (ADR 0008) — the catch-all route, last in the URLconf.

    Only paths the registry actually discovered are served: an unknown or non-whitelisted path is a
    404, which also means a ``../`` traversal can never resolve (the registry holds only files found
    under the content root). Bytes are read with a guessed content-type and carry the same
    ``ETag``/``Cache-Control`` as the pages.
    """

    def get(self, request, asset_path: str) -> HttpResponse:
        asset = RegistryBuilder.cached().get_asset(asset_path)
        if asset is None:
            raise Http404(f"no such asset: {asset_path}")
        content_type = mimetypes.guess_type(asset.source.name)[0] or "application/octet-stream"
        cache = ResponseCache()
        response = HttpResponse(asset.source.read_bytes(), content_type=content_type)
        return cache.finalize(request, response)
