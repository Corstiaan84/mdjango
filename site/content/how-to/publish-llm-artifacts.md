---
title: Publish the LLM artifacts
weight: 80
description: Make llms.txt, llms-full.txt and per-page markdown say what you want, expose llms.txt at the site root, or switch the whole surface off.
---

# Publish the LLM artifacts

**Goal:** control the machine-readable views of your docs — the `llms.txt` family — that mdjango
publishes beside the HTML.

**You need:** a mounted site. The routes are listed in the [URL reference](../../reference/urls/).

## Know what is published

Three artifacts, all generated from the *source* markdown of the Content tree and served under the
mount prefix:

| URL | Content |
|---|---|
| `/docs/llms.txt` | Title, optional summary, then one `- [Title](…/page.md): description` entry per page under `##` Section and `###` Subsection headings. |
| `/docs/llms-full.txt` | Title and summary, then every page's markdown in navigation order, separated by `---`. |
| `/docs/<page>.md` (and `/docs/index.md`) | One page's markdown, with a `# Title` heading prepended if the body does not open with one. |

Every HTML page advertises its alternate with
`<link rel="alternate" type="text/markdown" href="…/page.md">`, and the header links to the two
site-wide files. The static export writes all of them.

Inside a Section, `llms.txt` lists the Section's own pages before its Subsections, even when weights
interleave them in the navigation — markdown headings cannot return to Section level once a `###`
has opened. `llms-full.txt` keeps the exact navigation order.

## Write the summary and the descriptions

```python
MDJANGO_DESCRIPTION = "Deploy container apps to a server you own, with one config file."
```

renders as the blockquote under the title:

```markdown
# acme docs

> Deploy container apps to a server you own, with one config file.

## Getting started
- [Quickstart](/docs/getting-started/quickstart.md): From a fresh server to a running app.
```

The per-page suffix comes from each page's `description` front-matter key. Pages without one are
listed without a suffix. Write descriptions as a single sentence an agent can select on.

## Serve llms.txt at the site root

The convention expects `/llms.txt` at the domain root; mdjango serves it under the mount. Add a
redirect in your project's `urls.py`:

```python
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("llms.txt", RedirectView.as_view(pattern_name="mdjango:llms_txt")),
    path("docs/", include("mdjango.urls")),
]
```

## Switch the surface off

```python
MDJANGO_LLM_DOCS = False
```

All four markdown routes return 404, the header and drawer links disappear, and the `<link
rel="alternate">` is dropped from every page. `search-index.json` is unaffected — search is not part
of this surface.
