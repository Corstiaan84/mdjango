"""LLM-artifact service — emit the machine-readable views of the docs.

Following the `llms.txt convention <https://llmstxt.org/>`_, mdjango publishes three markdown
artifacts alongside the HTML site, so an LLM or agent can read clean source instead of scraping
rendered pages:

- **``llms.txt``** — a curated index: the site title, an optional summary, then one linked list
  item per page (pointing at that page's ``.md``), grouped by section and subsection.
- **``llms-full.txt``** — every page's markdown concatenated into one document, in nav order.
- **per-page ``.md``** — the raw markdown of a single page (:meth:`page_markdown`).

:class:`LlmArtifactBuilder` is the service class. It reads the *source* markdown (``page.body``),
never the rendered HTML — the artifacts are markdown-in, markdown-out, so no rendering pass is
needed. Like the search index, the two site-wide artifacts are built once from the *same* registry
and served two ways (ADR 0001): a runtime view returns them, and the static export writes them.
"""

from __future__ import annotations

from django.urls import reverse

from ...conf import get_conf
from ..content.dtos import Page, Registry, Subsection
from ..content.services import RegistryBuilder
from .dtos import LlmArtifacts


class LlmArtifactBuilder:
    """The LLM-artifact service: turn a :class:`Registry` into the ``llms.txt`` family."""

    _cache: LlmArtifacts | None = None

    def __init__(self, registry: Registry):
        self.registry = registry
        conf = get_conf()
        self.title = conf.title or "Documentation"
        self.description = conf.description

    # --- per-page markdown ---------------------------------------------------------------------

    def page_markdown(self, page: Page) -> str:
        """One page as standalone markdown: its raw body, with a title heading ensured.

        Frontmatter is already stripped from ``body``; the title may live only in frontmatter, so
        a body that doesn't open with a heading gets one prepended — the ``.md`` stays standalone.
        """
        body = page.body.strip()
        if body.lstrip().startswith("#"):
            return body + "\n"
        heading = f"# {page.title}"
        return f"{heading}\n\n{body}\n" if body else f"{heading}\n"

    # --- site-wide artifacts -------------------------------------------------------------------

    def index(self) -> str:
        """``llms.txt`` — title, optional summary, then a linked list of pages per group.

        The tree's shape becomes real heading nesting — ``##`` per section, ``###`` per subsection
        (ADR 0004 §6) — because the consumers here are agents that can read structure. A run of
        root loose pages gets one generic ``##`` heading, mirroring how the nav coalesces them.

        Inside a section, its own pages are listed **before** its subsections rather than
        interleaved by weight as the nav does (ADR 0004 §4). Markdown headings are flat and
        sequential: once a ``###`` opens there is no way back to section level, so a page sorting
        after a subsection would be listed *under* that subsection's heading and the index would
        assert a grouping that does not exist. Grouping here is the only shape that neither
        misfiles a page nor repeats a heading; the weight order is still exact in the nav and in
        ``llms-full.txt``.
        """
        lines = [f"# {self.title}"]
        if self.description:
            lines += ["", f"> {self.description}"]
        in_loose_run = False
        for child in self.registry.children:
            if isinstance(child, Page):
                if not in_loose_run:
                    lines += ["", "## Documentation"]
                    in_loose_run = True
                lines.append(self._entry(child))
                continue
            in_loose_run = False
            lines += ["", f"## {child.title or 'Documentation'}"]
            lines += [self._entry(p) for p in child.children if isinstance(p, Page)]
            for item in child.children:
                if isinstance(item, Subsection):
                    lines += ["", f"### {item.title}"]
                    lines += [self._entry(page) for page in item.pages]
        return "\n".join(lines).rstrip() + "\n"

    def _entry(self, page: Page) -> str:
        suffix = f": {page.description}" if page.description else ""
        return f"- [{page.title}]({self._md_url(page)}){suffix}"

    def full(self) -> str:
        """``llms-full.txt`` — the whole corpus as one markdown document, in nav order."""
        lines = [f"# {self.title}"]
        if self.description:
            lines += ["", f"> {self.description}"]
        for page in self._pages():
            lines += ["", "---", "", self.page_markdown(page).rstrip()]
        return "\n".join(lines).rstrip() + "\n"

    def _pages(self) -> list[Page]:
        """The index page (if any) first, then every page in flattened nav order."""
        head = [self.registry.index_page] if self.registry.index_page is not None else []
        return head + self.registry.ordered_pages

    @staticmethod
    def _md_url(page: Page) -> str:
        if page.path == "":
            return reverse("mdjango:index_markdown")
        return reverse("mdjango:page_markdown", args=[page.path])

    # --- build-once cache ----------------------------------------------------------------------

    @classmethod
    def cached(cls) -> LlmArtifacts:
        if cls._cache is None or get_conf().always_rebuild:
            builder = cls(RegistryBuilder.cached())
            cls._cache = LlmArtifacts(index=builder.index(), full=builder.full())
        return cls._cache

    @classmethod
    def clear_cache(cls) -> None:
        cls._cache = None
