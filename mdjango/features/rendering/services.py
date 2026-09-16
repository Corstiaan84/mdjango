"""Rendering service — markdown -> HTML + table of contents.

:class:`Renderer` builds one :class:`markdown.Markdown` per call, producing the article HTML
(heading ids + ``#`` permalinks, Pygments-tokenised code fences) and the H2/H3 table of contents.
Code fences are wrapped so the ``clipboard`` controller can add a copy affordance; the button reads
the code text at runtime.
"""

from __future__ import annotations

import posixpath
import re
from collections.abc import Callable

import markdown

from .dtos import Rendered, TocItem

# Each fence renders as `<div class="… highlight">` (the class list also carries `language-<lang>`
# when the fence is tagged, in a non-fixed order). We turn that wrapper into the clipboard
# controller's element and inject the copy button as its first child — matching only the opening
# tag means no matching-close bookkeeping.
_HIGHLIGHT_DIV = re.compile(r'<div class="(?P<cls>[^"]*\bhighlight\b[^"]*)">')
_COPY_BUTTON = (
    '<button class="copy-btn" type="button" data-action="clipboard#copy" '
    'data-clipboard-copied-label="copied">copy</button>'
)

# An `<img src="…">` or an `<a href="…">` in the output, any attribute order (double-quoted, as
# Python-Markdown and well-formed authored HTML both emit). We rewrite the captured URL in-place
# **only when it resolves to a content-tree Asset** — an output pass rather than a treeprocessor so
# it also catches raw-HTML that `md_in_html` stashes instead of parsing (ADR 0008). `<a href>` is
# rewritten too so the click-to-enlarge idiom (an image linked to its full-resolution self) works;
# it is safe because a relative link to another Page is extensionless and never matches an Asset.
_ASSET_REF = re.compile(r'(<(?:img|a)\b[^>]*?\b(?:src|href)=")([^"]*)(")', re.IGNORECASE)
# Left untouched: absolute, protocol-relative, root-relative, and non-file schemes — only a truly
# page-relative reference is a candidate for Asset rewriting.
_NON_RELATIVE = ("//", "/", "#", "data:", "mailto:", "http:", "https:")

_EXTENSIONS = [
    "toc",
    "tables",
    "attr_list",
    "def_list",
    "md_in_html",
    "sane_lists",
    "pymdownx.superfences",
    "pymdownx.highlight",
    "pymdownx.betterem",
    "pymdownx.tilde",
    "pymdownx.saneheaders",
]
_EXTENSION_CONFIGS = {
    "toc": {"permalink": "#", "permalink_title": "Link to this section", "toc_depth": "2-4"},
    "pymdownx.highlight": {"guess_lang": False, "pygments_lang_class": True},
}


class Renderer:
    """The rendering service: markdown body -> article HTML + H2/H3 table of contents.

    With no arguments it renders as before (no Asset rewriting) — the shape any non-page caller and
    the tests use. Given an ``asset_resolver`` (a ``tree_path -> url | None`` callable) and the
    page's ``page_dir`` within the content tree, it rewrites relative ``<img src>`` and ``<a href>``
    references that resolve to a known Asset to their served URL (ADR 0008). The resolver is the
    seam that keeps this
    service HTTP-free: the view layer builds it from ``reverse`` and the registry.
    """

    def __init__(
        self,
        asset_resolver: Callable[[str], str | None] | None = None,
        page_dir: str = "",
    ):
        self.asset_resolver = asset_resolver
        self.page_dir = page_dir

    def render(self, body: str) -> Rendered:
        md = self._make_md()
        html = self._wrap_code_blocks(md.convert(body))
        html = self._rewrite_asset_srcs(html)
        toc: list[TocItem] = []
        self._walk_toc(getattr(md, "toc_tokens", []), toc)
        return Rendered(html=html, toc=tuple(toc))

    def _rewrite_asset_srcs(self, html: str) -> str:
        if self.asset_resolver is None:
            return html

        def replace(m: re.Match) -> str:
            url = self._asset_url(m.group(2))
            return f"{m.group(1)}{url}{m.group(3)}" if url is not None else m.group(0)

        return _ASSET_REF.sub(replace, html)

    def _asset_url(self, src: str) -> str | None:
        """The served URL for a page-relative ``src``/``href``, or ``None`` to leave it alone."""
        if not src or src.startswith(_NON_RELATIVE) or "?" in src or "#" in src:
            return None
        tree_path = posixpath.normpath(posixpath.join(self.page_dir, src))
        if tree_path.startswith("..") or tree_path.startswith("/"):
            return None  # a ref that escapes the content root is never an Asset
        return self.asset_resolver(tree_path)

    @staticmethod
    def _make_md() -> markdown.Markdown:
        return markdown.Markdown(
            extensions=_EXTENSIONS,
            extension_configs=_EXTENSION_CONFIGS,
            output_format="html",
            tab_length=4,
        )

    @staticmethod
    def _wrap_code_blocks(html: str) -> str:
        return _HIGHLIGHT_DIV.sub(
            lambda m: (
                f'<div class="{m.group("cls")} code-block" data-controller="clipboard">'
                + _COPY_BUTTON
            ),
            html,
        )

    @classmethod
    def _walk_toc(cls, tokens: list[dict], out: list[TocItem]) -> None:
        for tok in tokens:
            level = tok.get("level")
            if level in (2, 3):
                out.append(TocItem(id=tok["id"], label=tok["name"], level=level))
            if tok.get("children"):
                cls._walk_toc(tok["children"], out)
