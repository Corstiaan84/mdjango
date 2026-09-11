"""Rendering service — markdown -> HTML + table of contents.

:class:`Renderer` builds one :class:`markdown.Markdown` per call, producing the article HTML
(heading ids + ``#`` permalinks, Pygments-tokenised code fences) and the H2/H3 table of contents.
Code fences are wrapped so the ``clipboard`` controller can add a copy affordance; the button reads
the code text at runtime.
"""

from __future__ import annotations

import re

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
    """The rendering service: markdown body -> article HTML + H2/H3 table of contents."""

    def render(self, body: str) -> Rendered:
        md = self._make_md()
        html = self._wrap_code_blocks(md.convert(body))
        toc: list[TocItem] = []
        self._walk_toc(getattr(md, "toc_tokens", []), toc)
        return Rendered(html=html, toc=tuple(toc))

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
