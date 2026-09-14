"""Content-layer data types.

`Page`/`Subsection`/`Section`/`Registry` form the in-memory content model. They carry structure
and trivial lookups only (no rendering, no HTTP) — the equivalent of a model + manager in the
stack's layering. `Registry.get`/`neighbours` are thin accessors, kept here so the content service
returns one cohesive object.

The three-level cap (ADR 0004) is **structural**, not a runtime check: a `Section` holds Pages and
Subsections, a `Subsection` holds only Pages, so there is no shape in this module that can nest a
fourth level. `children` lists are the *ordered* contents of their parent — Pages and groups
interleaved by weight — so nav order is the model's order, not something a consumer re-derives.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


# eq=False: Page.section/Page.subsection <-> .pages/.children are reference cycles, so field-based
# equality would recurse forever (e.g. list.index in neighbours). Each page/group is a singleton in
# the registry, so identity equality is both correct and cycle-free.
@dataclass(eq=False)
class Page:
    """One markdown document, addressable by ``path`` — the only thing that gets a URL."""

    path: str  # url path relative to the docs root, e.g. "guides/databases/recover"
    title: str
    weight: int
    description: str
    draft: bool
    source: Path
    body: str
    # Optional author-set last-updated date (frontmatter `updated: YYYY-MM-DD`), feeding the
    # sitemap's <lastmod>. Deliberately not file mtime — a git/CI checkout stamps every file with
    # the checkout time, so mtime would be identical and wrong across pages (ADR 0007).
    updated: date | None = None
    section: Section | None = None  # the top-level Section, whatever the depth
    subsection: Subsection | None = None  # set only for a page inside a Subsection

    @property
    def groups(self) -> tuple[Section | Subsection, ...]:
        """The page's named ancestor groups, outermost first — the trail the breadcrumb, the
        eyebrow and the search index each render their own way. Untitled groups are skipped, so a
        root-level loose page yields ``()``."""
        return tuple(g for g in (self.section, self.subsection) if g is not None and g.title)


@dataclass(eq=False)
class Subsection:
    """A group of Pages inside a Section — a nav label, not a destination (ADR 0004 §3)."""

    slug: str
    title: str
    weight: int
    source: Path | None = None  # the subsection's _index.md, if it has one
    pages: list[Page] = field(default_factory=list)


@dataclass(eq=False)
class Section:
    """A top-level group — one immediate subdirectory of the content root.

    ``children`` holds the section's own loose Pages and its Subsections in one weight-ordered
    list, so an author can place a group anywhere in a curated sequence (ADR 0004 §4).
    """

    slug: str
    title: str
    weight: int
    source: Path | None = None  # the section's _index.md, if it has one
    children: list[Page | Subsection] = field(default_factory=list)


@dataclass(eq=False)
class Registry:
    """The whole content tree, built once and held in memory."""

    root: Path
    children: list[Page | Section]  # root loose Pages and Sections, interleaved by weight
    pages_by_path: dict[str, Page]
    ordered_pages: list[Page]  # flattened nav order, for prev/next
    index_page: Page | None

    def get(self, path: str) -> Page | None:
        return self.pages_by_path.get(path.strip("/"))

    def neighbours(self, page: Page) -> tuple[Page | None, Page | None]:
        """The (previous, next) pages in flattened nav order, for the pager.

        Keyed on ``page.path``, not object identity. Under ``always_rebuild`` (DEBUG) the registry
        is rebuilt on every ``RegistryBuilder.cached()`` call, so the ``page`` handed in here can be
        a *different object* from its twin in ``ordered_pages`` — ``Page`` is ``eq=False``, so an
        identity ``.index(page)`` would miss and drop the pager links. ``path`` is the stable
        identity (unique per the duplicate-path guard), so it survives a rebuild.
        """
        paths = [p.path for p in self.ordered_pages]
        try:
            i = paths.index(page.path)
        except ValueError:
            return (None, None)
        prev = self.ordered_pages[i - 1] if i > 0 else None
        nxt = self.ordered_pages[i + 1] if i + 1 < len(self.ordered_pages) else None
        return (prev, nxt)
