---
title: URLs
weight: 30
description: The routes mdjango.urls mounts under your prefix, their names, and how to reverse them.
---

# URLs

Mount with `path("docs/", include("mdjango.urls"))`; any prefix works. The URLconf sets
`app_name = "mdjango"`, so names are reversed as `mdjango:<name>`. Examples below assume the
`docs/` prefix.

## Routes

| Path | Name | Response |
|---|---|---|
| `/docs/` | `mdjango:index` | HTML. The Index page, or the first Page in navigation order when there is no root `_index.md`. 404 when the tree has no pages. |
| `/docs/<path>/` | `mdjango:page` | HTML. `<path>` is the Page path (`how-to/deploy`, `how-to/hosts/harden`). 404 for an unknown path. |
| `/docs/search-index.json` | `mdjango:search_index` | JSON array; see below. Always available. |
| `/docs/llms.txt` | `mdjango:llms_txt` | `text/markdown`. 404 when `MDJANGO_LLM_DOCS` is false. |
| `/docs/llms-full.txt` | `mdjango:llms_full` | `text/markdown`. 404 when `MDJANGO_LLM_DOCS` is false. |
| `/docs/index.md` | `mdjango:index_markdown` | `text/markdown`. The landing page's source. 404 when `MDJANGO_LLM_DOCS` is false. |
| `/docs/<path>.md` | `mdjango:page_markdown` | `text/markdown`. One Page's source. 404 when unknown or `MDJANGO_LLM_DOCS` is false. |

File-shaped routes carry no trailing slash; the HTML page route requires one. That is what keeps a
page named `llms` from shadowing `llms.txt`.

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

## Headers

Every response carries a strong `ETag` (MD5 of the body). `Cache-Control` is
`public, max-age=<MDJANGO_CACHE_SECONDS>` when caching is enabled and `no-cache` otherwise. A
request with a matching `If-None-Match` receives `304 Not Modified`. See [Tune caching](../../how-to/tune-caching/).

## Search index

`search-index.json` is a JSON array with one object per visible Page, the Index page first:

| Field | Value |
|---|---|
| `id` | the Page path (`""` for the Index page) |
| `title` | Page title |
| `section` | ancestor trail as one string, `"Section / Subsection"`; empty for root pages |
| `text` | the rendered page reduced to plain text — full body, not a summary |
| `url` | the Page's HTML URL |

The client indexes `title`, `section` and `text` with MiniSearch (title boosted ×3, section ×2,
prefix and fuzzy matching on). Index and library are fetched on the first opening of the palette,
not on page load. Open with `/` or Ctrl/⌘-K; close with Esc.
