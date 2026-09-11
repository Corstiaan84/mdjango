"""Content service — read the markdown tree into a :class:`Registry`, and cache it.

Convention-driven tree (3-level cap — ADR 0004)::

    content/
      _index.md                 -> the docs index page (path "")
      about.md                  -> a loose Page (path "about")
      getting-started/          -> a Section
        _index.md               -> section title/weight (optional)
        quickstart.md           -> a Page (path "getting-started/quickstart")
      guides/
        databases/              -> a Subsection
          _index.md             -> subsection title/weight (optional)
          recover.md            -> a Page (path "guides/databases/recover")
        secrets.md

Frontmatter keys: ``title``, ``weight`` (int), ``draft`` (bool), ``description``. Pages and groups
interleave by ``(weight, title)`` within their parent, so a group can sit anywhere in a curated
sequence. A group with no visible pages is omitted entirely — it would otherwise render as a dead
nav label and an empty ``llms.txt`` heading. The tree is trusted (authored by the project, not
user-submitted). :class:`RegistryBuilder` is the service class; the stateless frontmatter parser
lives in the sibling ``frontmatter`` concept module.
"""

from __future__ import annotations

import re
from pathlib import Path

from django.utils.text import slugify

from ...conf import get_conf
from ..common.exceptions import ContentError
from . import frontmatter
from .dtos import Page, Registry, Section, Subsection

INDEX_STEMS = ("_index", "index")
_H1 = re.compile(r"^\s{0,3}#\s+(.+?)\s*#*\s*$", re.MULTILINE)


class RegistryBuilder:
    """The content service: walk a content root into a :class:`Registry`.

    Holds the walk's context (``root``, ``include_drafts``) as state, and owns the process-wide
    build-once cache (``cached``/``clear_cache``). Raises :class:`ContentError` on a malformed tree.
    """

    _cache: Registry | None = None

    def __init__(self, root, *, include_drafts: bool = False):
        self.root = Path(root)
        self.include_drafts = include_drafts

    # --- build ---------------------------------------------------------------------------------

    def build(self) -> Registry:
        if not self.root.is_dir():
            raise ContentError(f"content dir does not exist: {self.root}")

        index_page: Page | None = None
        children: list[Page | Section] = []

        for entry in sorted(self.root.iterdir(), key=lambda p: p.name):
            if entry.is_dir():
                children.append(self._build_section(entry))
            elif entry.suffix == ".md":
                if self._is_index(entry):
                    index_page = self._read_page(entry, path="")
                else:
                    page = self._read_page(entry, path=slugify(entry.stem))
                    if self._is_visible(page):
                        children.append(page)

        children = [child for child in self._sorted(children) if self._flatten([child])]

        ordered = self._flatten(children)
        pages_by_path: dict[str, Page] = {}
        for page in ordered:
            if page.path in pages_by_path:
                raise ContentError(
                    f"duplicate page path {page.path!r}: {page.source} and "
                    f"{pages_by_path[page.path].source}"
                )
            pages_by_path[page.path] = page

        if index_page is not None:
            pages_by_path[""] = index_page

        return Registry(
            root=self.root,
            children=children,
            pages_by_path=pages_by_path,
            ordered_pages=ordered,
            index_page=index_page,
        )

    def _build_section(self, directory: Path) -> Section:
        section = Section(slug=slugify(directory.name), title="", weight=100)
        children: list[Page | Subsection] = []

        for entry in self._group_entries(directory, section):
            if entry.is_dir():
                subsection = self._build_subsection(entry, section_slug=section.slug)
                if subsection.pages:
                    children.append(subsection)
                continue
            page = self._read_page(entry, path=f"{section.slug}/{slugify(entry.stem)}")
            if self._is_visible(page):
                children.append(page)

        section.children = self._sorted(children)
        for page in self._flatten([section]):
            page.section = section
        return section

    def _build_subsection(self, directory: Path, *, section_slug: str) -> Subsection:
        subsection = Subsection(slug=slugify(directory.name), title="", weight=100)
        pages: list[Page] = []

        for entry in self._group_entries(directory, subsection):
            if entry.is_dir():
                raise ContentError(
                    f"content is capped at three levels (section -> subsection -> page); found a "
                    f"nested directory {entry} inside subsection {directory.name!r}"
                )
            page = self._read_page(
                entry, path=f"{section_slug}/{subsection.slug}/{slugify(entry.stem)}"
            )
            if self._is_visible(page):
                pages.append(page)

        subsection.pages = self._sorted(pages)
        for page in subsection.pages:
            page.subsection = subsection
        return subsection

    def _group_entries(self, directory: Path, group: Section | Subsection) -> list[Path]:
        """Set a group's title/weight from its own ``_index.md``, and return its other entries.

        The title/weight come from the ``_index.md`` (whose body is discarded — ADR 0004 §3), or
        fall back to the humanised directory name. What comes back is everything the caller still
        has to interpret: subdirectories and page files, in filename order.
        """
        group.title = self._humanize(directory.name)
        entries: list[Path] = []

        for entry in sorted(directory.iterdir(), key=lambda p: p.name):
            if entry.is_dir():
                entries.append(entry)
                continue
            if entry.suffix != ".md":
                continue
            if self._is_index(entry):
                meta, _ = frontmatter.split_frontmatter(entry.read_text(encoding="utf-8"))
                group.title = meta.get("title", group.title)
                group.weight = frontmatter.as_int(meta.get("weight"), group.weight)
                group.source = entry
                continue
            entries.append(entry)

        return entries

    # --- content-tree helpers ------------------------------------------------------------------

    def _is_visible(self, page: Page) -> bool:
        return self.include_drafts or not page.draft

    @staticmethod
    def _order_key(item: Page | Section | Subsection) -> tuple[int, str]:
        return (item.weight, item.title.lower())

    @classmethod
    def _sorted(cls, items: list) -> list:
        return sorted(items, key=cls._order_key)

    @classmethod
    def _flatten(cls, children: list) -> list[Page]:
        """Every Page under ``children``, depth-first in nav order."""
        pages: list[Page] = []
        for child in children:
            if isinstance(child, Page):
                pages.append(child)
            elif isinstance(child, Subsection):
                pages.extend(child.pages)
            else:
                pages.extend(cls._flatten(child.children))
        return pages

    @classmethod
    def _read_page(cls, source: Path, path: str) -> Page:
        meta, body = frontmatter.split_frontmatter(source.read_text(encoding="utf-8"))
        title = meta.get("title") or cls._first_h1(body) or cls._humanize(source.stem)
        return Page(
            path=path,
            title=title,
            weight=frontmatter.as_int(meta.get("weight"), 100),
            description=meta.get("description", ""),
            draft=frontmatter.as_bool(meta.get("draft"), False),
            source=source,
            body=body,
        )

    @staticmethod
    def _is_index(p: Path) -> bool:
        return p.stem in INDEX_STEMS

    @staticmethod
    def _humanize(stem: str) -> str:
        return stem.replace("-", " ").replace("_", " ").strip().capitalize()

    @staticmethod
    def _first_h1(body: str) -> str | None:
        m = _H1.search(body)
        return m.group(1).strip() if m else None

    # --- build-once cache ----------------------------------------------------------------------
    # Read from disk once per process. In DEBUG (or with MDJANGO_ALWAYS_REBUILD) rebuild every
    # access so edits show up without a restart.

    @classmethod
    def cached(cls) -> Registry:
        conf = get_conf()
        if cls._cache is None or conf.always_rebuild:
            cls._cache = cls(conf.content_dir, include_drafts=conf.include_drafts).build()
        return cls._cache

    @classmethod
    def clear_cache(cls) -> None:
        """Drop the cached registry (used by tests and the build command)."""
        cls._cache = None
