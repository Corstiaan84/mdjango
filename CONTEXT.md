# mdjango — context

`mdjango` is a reusable, drop-in **markdown documentation Django app** (`pip install
django-mdjango`, `import mdjango`). A consuming Django project points it at a tree of markdown
files and gets a complete, themed documentation site — served at runtime and/or exported static.

This file is a **glossary**, not a spec. Implementation decisions live in `docs/adr/`.

## Glossary

**Consumer** — a Django project that installs `mdjango` and mounts it. mdjango ships as a
standalone package and is **its own first Consumer**: its `site/` project mounts mdjango to serve
mdjango's own documentation (see **Self-hosted site**).

**Self-hosted site** — mdjango's own public docs site, served by the `site/` project in this repo
(the promoted former `example/` harness): a stand-in Consumer that mounts mdjango and points it at
mdjango's *real* documentation. It wears the unmodified **House style** — no **Seed** overrides, no
shadowed **Shell** — so it doubles as the canonical reference mount; the **Override surface** is
taught in the docs prose, not here. Not shipped in the wheel.

**Content tree** — the directory of markdown files a Consumer points mdjango at. The filesystem
is the whole source of truth: there is no database, and every published URL comes from a file in
this tree. It nests at most three levels deep — Section, Subsection, Page (ADR 0004).

**Page** — one markdown document. A Page is the only thing mdjango gives a URL: every URL is a
Page, and every Page is a file.

**Section** — a top-level grouping of Pages, one immediate subdirectory of the Content tree.
Sections are the site's map — always visible in the navigation, never collapsed.

**Subsection** — a grouping of Pages *inside* a Section, one level deeper. A Subsection is a
**label, not a destination**: it has no URL of its own, and its landing file supplies only a title
and an ordering weight. *Avoid*: group (the navigation layer's word for a rendered block),
category, topic.

**Loose page** — a Page that sits directly in its parent's directory rather than in a deeper
grouping: directly in the Content tree, or directly in a Section alongside its Subsections.

**Index page** — the Page served at the Content tree's mount root, sourced from a root
`_index.md`. It is the only Page with an empty URL path, and unlike a Section's or Subsection's
landing file — whose body is discarded (ADR 0004) — the Index page's body is rendered as the
site's landing. Optional: with no root `_index.md`, the mount root falls back to the first Page in
navigation order and there is no Index page. *Not* the search index or the `llms.txt` index, which
are machine-readable listings rather than Pages.

**Theme** — the single, opinionated docs shell + visual identity mdjango ships. There is exactly
**one** theme, light + dark baked in. It is not a theme *system*; a multi-theme registry is
deferred until a real second theme exists.

**House style** — the fixed, non-negotiable part of the Theme: the flat/monochrome/typographic
personality and the layout. A Consumer **cannot** change it (short of forking). Adopting mdjango
means adopting the house style; that is the point of "opinionated drop-in".

**Override surface** — the small set of values a Consumer *may* set to make the docs their own:
the two ends of each colour Ramp, one accent colour, the body font, and the base font size.
Everything else about the Theme is fixed or derived from these.

**Ramp** — one of the Theme's two colour progressions: the *surface* ramp, from the page ground to
the hairline tone, and the *text* ramp, from full-emphasis text to lowest-emphasis text. A Ramp is
defined by its two ends; its interior stops are Derived. Colour is only ever mixed *within* a
Ramp, never across the palette — mixing across it averages away the chroma the ends carry, which
would wash out any tinted palette.

**Seed value** — an Override-surface value the Consumer sets directly; for colour, the end of a
Ramp. **Derived value** — a Theme value computed from the ends of its own Ramp (body text, muted
text, raised surfaces) and locked, so a Consumer cannot break the internal contrast relationships
the design depends on.

**Shell** — the whole page mdjango renders around the article: header, section-nav, table of
contents, prev/next. mdjango owns the Shell by default (driven by config) but a Consumer can
override the base template / header / footer to supply their own chrome. The Shell is part of the
Theme; it is not the article.

**Home link** — the navigation link to the Index page, pinned at the top of the left nav above
every Section and labelled with the Index page's title. It exists only when an Index page does. The
Home link is to the Index page what a subgroup is to a Subsection: the nav-layer rendering of a
content-tree concept.

**LLM artifacts** — the machine-readable views of the docs mdjango publishes beside the HTML, per
the [llms.txt convention](https://llmstxt.org/): `llms.txt` (a curated, per-section index linking
each page's markdown), `llms-full.txt` (every page's markdown in one document), and per-page raw
markdown (a page's `.md` alternate). All are built from the same content tree as the site and served
both at runtime and in the static export. They are *source* markdown, not rendered HTML.
