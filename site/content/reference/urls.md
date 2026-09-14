---
title: URLs
weight: 30
description: The routes mdjango.urls mounts under your prefix, their names, the response headers, and the search index schema.
---

# URLs

Mount with `path("docs/", include("mdjango.urls"))`. Any prefix works. The URLconf sets
`app_name = "mdjango"`, so names reverse as `mdjango:<name>`. Examples below assume the `docs/`
prefix.

The namespace is fixed. Templates and services reverse routes as `mdjango:<name>`, so passing a
`namespace=` argument to `include()` or mounting the URLconf at two prefixes breaks every internal
link.

### Serve the docs at the site root

If the site *is* the docs, mount at the root instead of under `docs/`:

```python
urlpatterns = [
    # any other root routes (sitemap.xml, robots.txt, admin/, …) FIRST
    path("", include("mdjango.urls")),  # a catch-all — must come last
]
```

The `<path:page_path>/` route matches any path, so the mdjango include has to be the **last**
pattern: anything you serve at the root — `sitemap.xml`, `robots.txt`, the admin — must be declared
above it or the page view will shadow it with a 404. Reversed URLs and the export drop the prefix
accordingly (`mdjango:index` is `/`, a page is `/how-to/deploy/`). This is exactly how mdjango's own
docs site is mounted.

## Routes

| Path | Name | Response |
|---|---|---|
| `/docs/` | `mdjango:index` | HTML. The Index page, or the first Page in navigation order when there is no root `_index.md`. 404 when the tree has no Pages. |
| `/docs/<path>/` | `mdjango:page` | HTML. `<path>` is the Page path (`how-to/deploy`, `how-to/hosts/harden`). 404 for an unknown path. |
| `/docs/search-index.json` | `mdjango:search_index` | JSON array; see below. Always available. |
| `/docs/llms.txt` | `mdjango:llms_txt` | `text/markdown`. 404 when `MDJANGO_LLM_DOCS` is false. |
| `/docs/llms-full.txt` | `mdjango:llms_full` | `text/markdown`. 404 when `MDJANGO_LLM_DOCS` is false. |
| `/docs/index.md` | `mdjango:index_markdown` | `text/markdown`. The landing page's source. 404 when `MDJANGO_LLM_DOCS` is false. |
| `/docs/<path>.md` | `mdjango:page_markdown` | `text/markdown`. One Page's source. 404 when unknown or `MDJANGO_LLM_DOCS` is false. |

File-shaped routes carry no trailing slash and the HTML page route requires one. That keeps a Page
named `llms` from shadowing `llms.txt`. The `index.md` route is declared before `<path>.md` so it is
not read as a Page named `index`.

Markdown responses are served as `text/markdown; charset=utf-8`. The per-page `.md` is the source
body with front-matter stripped; a body that does not open with a heading gets `# <title>`
prepended.

## Reversing

```python
from django.urls import reverse

reverse("mdjango:index")                                    # /docs/
reverse("mdjango:page", args=["how-to/deploy"])             # /docs/how-to/deploy/
reverse("mdjango:page_markdown", args=["how-to/deploy"])    # /docs/how-to/deploy.md
reverse("mdjango:llms_txt")                                 # /docs/llms.txt
```

`mdjango.views.page_url(page)` and `mdjango.views.page_markdown_url(page)` do the same from a
`Page` object, handling the Index page's empty path.

## Sitemap

`sitemap.xml` is **not** a route `mdjango.urls` mounts. mdjango ships the `mdjango.sitemaps.DocsSitemap`
class; you mount the standard `django.contrib.sitemaps` view at your **site root** (not under the
docs prefix — a sitemap is a root resource), and Django supplies the domain from the request. See
[Make your docs discoverable](../../how-to/make-docs-discoverable/). `robots.txt` and `/.well-known/`
are your site root's concern too and mdjango ships neither.

## Headers

Every response carries a strong `ETag` (MD5 of the body). `Cache-Control` is
`public, max-age=<MDJANGO_CACHE_SECONDS>` when caching is enabled and `no-cache` otherwise. A
request with a matching `If-None-Match` receives `304 Not Modified`. No `Vary`, `Last-Modified` or
`s-maxage` is set. See [How caching works](../../explanation/how-caching-works/).

## Errors

| Situation | Response |
|---|---|
| unknown Page path | 404 |
| no Pages in the tree, at the mount root | 404 |
| any markdown route with `MDJANGO_LLM_DOCS = False` | 404 |
| `ContentError` or `ImproperlyConfigured` while reading the tree | 500 (uncaught) |

## Search index

`search-index.json` is a JSON array with one object per visible Page, the Index page first, then
navigation order:

| Field | Value |
|---|---|
| `id` | the Page path (`""` for the Index page) |
| `title` | Page title |
| `section` | ancestor trail as one string, `"Section / Subsection"`; empty for root Pages |
| `text` | the rendered page reduced to plain text: tags stripped, entities unescaped, whitespace collapsed. The full body, not a summary. |
| `url` | the Page's HTML URL |

The client indexes `title`, `section` and `text` with MiniSearch: title boosted ×3, section ×2,
prefix and fuzzy (`0.2`) matching on. Index and library are fetched on the first opening of the
palette, not on page load. Open with `/` or Ctrl/⌘-K; close with Esc. Building the index renders
every Page, so it is the most expensive build in the app.
