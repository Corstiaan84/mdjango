---
title: Publish the LLM artifacts
weight: 60
description: Describe the site and its pages for llms.txt, serve it at the domain root, or switch the markdown surface off.
---

# Publish the LLM artifacts

**Goal:** make the machine-readable views of the docs useful to an agent, or turn them off.

**You need:** a served Content tree. The artifacts are on by default. Their exact format and routes
are in the [URLs reference](../../reference/urls/).

## Know what is already published

| URL | Content |
|---|---|
| `/docs/llms.txt` | site title, optional summary, one linked entry per page grouped by Section and Subsection |
| `/docs/llms-full.txt` | every page's markdown in one document, in navigation order |
| `/docs/<page>.md` | one page's markdown. Also `/docs/index.md` for the Index page |

All three are source markdown, not rendered HTML, and are served with
`text/markdown; charset=utf-8`. Every HTML page carries a `<link rel="alternate" type="text/markdown">`
pointing at its own `.md`.

## Describe the site

```python
# settings.py
MDJANGO_SITE_TITLE = "Acme documentation"
MDJANGO_DESCRIPTION = "Install, configure and operate the Acme CLI and its hosted control plane."
```

The title becomes the `#` heading of both site-wide artifacts. The description becomes a `>`
blockquote under it. Without a title the heading falls back to `MDJANGO_BRAND`, then to
"Documentation".

## Describe each page

```markdown
---
title: Roll back a deploy
description: Return a host to the previous release without touching the database.
---
```

The `description` key becomes the suffix of the page's `llms.txt` entry:

```text
- [Roll back a deploy](/docs/how-to/rollback.md): Return a host to the previous release without touching the database.
```

Write one sentence an agent can select on. A page without a description is listed without a suffix.

Inside a Section, `llms.txt` lists the Section's own Pages first and then each Subsection under a
`###` heading, even where the navigation interleaves them by weight. Markdown headings cannot
express interleaving without misfiling a page.

## Serve llms.txt at the domain root

The convention expects `/llms.txt` at the root. mdjango serves it under the mount. Redirect:

```python
# urls.py
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("llms.txt", RedirectView.as_view(pattern_name="mdjango:llms_txt")),
    path("docs/", include("mdjango.urls")),
]
```

## Switch the surface off

```python
# settings.py
MDJANGO_LLM_DOCS = False
```

The four markdown routes (`llms.txt`, `llms-full.txt`, `index.md`, `<page>.md`) return 404, the
header and drawer links disappear, and the `<link rel="alternate">` is dropped. `search-index.json`
is unaffected. Search is not part of this surface and cannot be disabled.
