---
title: Templates
weight: 60
description: The page template, the nine cotton components it composes, the context each one reads, and the shipped static assets.
---

# Templates

mdjango renders every HTML response through one template, `mdjango/page.html`, which composes
cotton components from `cotton/docs/`. There are no `{% block %}` tags, no `{% extends %}`, no
template tags and no context processors. The templates are not a customisation surface. What a
Consumer may change is listed in [settings](../settings/) and [theme tokens](../theme-tokens/).

## Page context

`mdjango.views.page_context(page)` builds this dict. Runtime views and the export both use it.

| Key | Type | Content |
|---|---|---|
| `conf` | `mdjango.conf.Conf` | resolved settings: `brand`, `home_url`, `version`, `github_url`, `header_links`, `site_title`, `description`, `llm_docs`, and `title` (site title or brand) |
| `page` | `Page` | the current Page: `path`, `title`, `weight`, `description`, `draft`, `source`, `body`, `section`, `subsection`, `groups` |
| `article_html` | `str` | rendered article, marked safe by the article component |
| `toc` | tuple of `TocItem(id, label, level)` | H2 and H3 headings; empty when the page has none |
| `home` | dict or `None` | `{kind, title, url, active}` for the Index page; `None` without a root `_index.md` |
| `nav` | list of dicts | groups `{title, loose, items}`; items are `{kind: "link", title, url, active}` or `{kind: "subgroup", title, open, items}` |
| `breadcrumb` | list of dicts | `{label, url}` per crumb, outermost group first, then the Page; `url` is always `""` |
| `eyebrow` | `str` | title of the Page's innermost group; `""` for root Pages |
| `prev`, `next` | `Page` or `None` | neighbours in flattened navigation order |
| `prev_url`, `next_url` | `str` | their URLs, or `""` |
| `page_md_url` | `str` | the `.md` alternate URL, or `""` when `MDJANGO_LLM_DOCS` is false |

## The page template

`mdjango/templates/mdjango/page.html` wraps everything in `<c-docs.base>`, then renders the header,
the drawer backdrop, a `.docs-shell` grid holding the sidebar, `<main>` (inline TOC, eyebrow,
article, pager) and the TOC rail, then the search dialog. When `toc` is empty both TOC instances
are omitted and the shell gets the `docs-shell--no-toc` class, which drops the rail column.

## Components

All under `mdjango/templates/cotton/docs/`. "Attributes" are passed explicitly by the page
template. "Outer context" is read from the page context without being passed.

| File | Renders | Attributes | Outer context |
|---|---|---|---|
| `base.html` | `<!doctype html>` through `</html>`: `<title>`, the `rel="alternate"` link, the no-flash theme script, the `mdjango.css` link, the import map, `<body class="docs-body" data-controller="theme search disclosure">` with `{{ slot }}`, and the `application.js` module | `title`, `page_md_url` (default `""`) | — |
| `header.html` | hamburger, wordmark, breadcrumb, search trigger, version chip, `llms.txt` links, header links, GitHub link, theme toggle | `conf`, `breadcrumb` | — |
| `sidebar.html` | `<nav class="docs-sidebar">`: Home link, mobile `llms.txt` group, one group per nav entry with `<details class="docs-nav-sub">` for subgroups | `nav` | `home`, `conf` |
| `toc.html` | `<nav class="docs-toc docs-toc--{variant}">` with one link per heading, `data-controller="scrollspy"` | `items`, `variant` (default `rail`) | — |
| `eyebrow.html` | `<p class="docs-eyebrow">`; nothing when the label is empty | `label` (default `""`) | — |
| `article.html` | `<article class="article">{{ html\|safe }}</article>` | `html` | — |
| `pager.html` | `<nav class="docs-pager">` with prev/next links; an empty placeholder where a neighbour is absent | `prev`, `next`, `prev_url`, `next_url` | — |
| `breadcrumb.html` | `<nav class="docs-breadcrumb">`; crumbs are `<span>`s, never links | `items` | — |
| `search.html` | the search dialog, `data-search-index-url="{% url 'mdjango:search_index' %}"` | — | — |

## Stimulus controllers

Booted by `application.js`, which registers five controllers. `theme`, `search` and `disclosure`
mount on `<body>`.

| Identifier | Mounted on | Does |
|---|---|---|
| `theme` | `<body>` | flips `data-theme` on `<html>` and persists it to `localStorage` |
| `search` | `<body>` | the palette: `/` and Ctrl/⌘-K open it, fetches MiniSearch and the index on first open, keyboard navigation |
| `disclosure` | `<body>` | opens and closes the mobile navigation drawer |
| `scrollspy` | each `<c-docs.toc>` | marks the TOC link of the heading nearest the top of the viewport |
| `clipboard` | each code block, injected by the renderer | copies the block's text; shows "copied" for 1.6 seconds |

## Static assets

Under `mdjango/static/mdjango/`, all vendored:

| Path | Purpose |
|---|---|
| `mdjango.css` | the compiled stylesheet, `@font-face` rules included |
| `fonts.css` | the `@font-face` rules alone |
| `fonts/*.woff2`, `fonts/LICENSE.txt` | IBM Plex Mono, six faces, OFL 1.1 |
| `application.js` | Stimulus boot; registers the five controllers |
| `controllers/{theme,clipboard,scrollspy,disclosure,search}_controller.js` | one file per controller |
| `vendor/stimulus.js`, `vendor/minisearch.js` | ESM builds, resolved by the import map in `base.html` |
