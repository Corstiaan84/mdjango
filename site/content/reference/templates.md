---
title: Templates
weight: 60
description: The page template, the nine cotton components it composes, and the context each one reads.
---

# Templates

mdjango renders every HTML response through one template, `mdjango/page.html`, which composes
cotton components from `cotton/docs/`. There are no `{% block %}` tags and no `{% extends %}`;
customisation is by shadowing a component file at the same path in a directory listed in
`TEMPLATES["DIRS"]`. There are no template tags or context processors.

## Page context

`mdjango.views.page_context(page)` builds this dict; runtime views and the export both use it.

| Key | Type | Content |
|---|---|---|
| `conf` | `mdjango.conf.Conf` | resolved settings: `brand`, `home_url`, `version`, `github_url`, `header_links`, `site_title`, `description`, `llm_docs`, and `title` (site title or brand) |
| `page` | `Page` | the current Page: `path`, `title`, `weight`, `description`, `draft`, `source`, `body`, `section`, `subsection`, `groups` |
| `article_html` | `str` | rendered article, marked safe by the article component |
| `toc` | tuple of `TocItem(id, label, level)` | H2 and H3 headings; empty when the page has none |
| `home` | dict or `None` | `{kind, title, url, active}` for the Index page; `None` without a root `_index.md` |
| `nav` | list of dicts | groups `{title, loose, items}`; items are `{kind: "link", title, url, active}` or `{kind: "subgroup", title, open, items}` |
| `breadcrumb` | list of dicts | `{label, url}` per crumb, outermost group first, then the Page; `url` is always `""` |
| `eyebrow` | `str` | title of the Page's innermost group; `""` for root pages |
| `prev`, `next` | `Page` or `None` | neighbours in flattened navigation order |
| `prev_url`, `next_url` | `str` | their URLs, or `""` |
| `page_md_url` | `str` | the `.md` alternate URL, or `""` when `MDJANGO_LLM_DOCS` is false |

## `mdjango/page.html`

```django
<c-docs.base :title="conf.title" :page_md_url="page_md_url">
  <c-docs.header :conf="conf" :breadcrumb="breadcrumb" />
  <div class="docs-backdrop" data-action="disclosure#close"></div>
  <div class="docs-shell{% if not toc %} docs-shell--no-toc{% endif %}">
    <c-docs.sidebar :nav="nav" />
    <main class="docs-main">
      {% if toc %}<c-docs.toc :items="toc" variant="inline" />{% endif %}
      <c-docs.eyebrow :label="eyebrow" />
      <c-docs.article :html="article_html" />
      <c-docs.pager :prev="prev" :next="next" :prev_url="prev_url" :next_url="next_url" />
    </main>
    {% if toc %}<c-docs.toc :items="toc" variant="rail" />{% endif %}
  </div>
  <c-docs.search />
</c-docs.base>
```

## Components

All under `mdjango/templates/cotton/docs/`. "Attributes" are passed explicitly; "outer context"
is read from the page context without being passed.

| File | Renders | Attributes | Outer context |
|---|---|---|---|
| `base.html` | `<!doctype html>` through `</html>`: `<title>`, the `rel="alternate"` link, the no-flash theme script, the `mdjango.css` link, the import map, `<body data-controller="theme search disclosure">` with `{{ slot }}`, and the `application.js` module | `title`, `page_md_url` (default `""`) | — |
| `header.html` | wordmark, breadcrumb, search trigger, version chip, `llms.txt` links, header links, GitHub link, theme toggle | `conf`, `breadcrumb` | — |
| `sidebar.html` | `<nav class="docs-sidebar">`: Home link, mobile `llms.txt` group, one group per nav entry with `<details class="docs-nav-sub">` for subgroups | `nav` | `home`, `conf` |
| `toc.html` | `<nav class="docs-toc docs-toc--{variant}">` with one link per heading, `data-controller="scrollspy"` | `items`, `variant` (default `rail`) | — |
| `eyebrow.html` | `<p class="docs-eyebrow">`; nothing when the label is empty | `label` (default `""`) | — |
| `article.html` | `<article class="article">{{ html|safe }}</article>` | `html` | — |
| `pager.html` | `<nav class="docs-pager">` with prev/next links | `prev`, `next`, `prev_url`, `next_url` | — |
| `breadcrumb.html` | `<nav class="docs-breadcrumb">`; crumbs are `<span>`s, never links | `items` | — |
| `search.html` | the search dialog, `data-search-index-url="{% url 'mdjango:search_index' %}"` | — | — |

## Static assets

Under `mdjango/static/mdjango/`, all vendored:

| Path | Purpose |
|---|---|
| `mdjango.css` | the compiled stylesheet, `@font-face` rules included |
| `fonts.css` | the `@font-face` rules alone |
| `fonts/*.woff2` | IBM Plex Mono, six faces |
| `application.js` | Stimulus boot; registers the five controllers |
| `controllers/{theme,clipboard,scrollspy,disclosure,search}_controller.js` | dark mode, copy button, TOC highlight, mobile drawer, search palette |
| `vendor/stimulus.js`, `vendor/minisearch.js` | ESM builds, resolved by the import map in `base.html` |
