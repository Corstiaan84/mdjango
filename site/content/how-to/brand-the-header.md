---
title: Brand the header
weight: 30
description: Set the wordmark, title, version chip and header links from settings.
---

# Brand the header

**Goal:** make the header say your project's name and link to your places.

**You need:** write access to the project's `settings.py`. Defaults for every setting are in the
[settings reference](../../reference/settings/).

## Set the text and links

```python
# settings.py
MDJANGO_BRAND = "acme"                               # wordmark, left of the header
MDJANGO_SITE_TITLE = "Acme documentation"            # <title>; falls back to MDJANGO_BRAND
MDJANGO_HOME_URL = "/"                               # where the wordmark links
MDJANGO_VERSION = "v2.3.0"                           # display-only chip; empty hides it
MDJANGO_GITHUB_URL = "https://github.com/acme/acme"  # link labelled "github"; empty hides it
MDJANGO_HEADER_LINKS = [
    {"label": "changelog", "url": "/changelog/"},
    {"label": "status", "url": "https://status.acme.example"},
]
```

`MDJANGO_HEADER_LINKS` also accepts `mdjango.conf.HeaderLink(label, url)` instances. A dict missing
either key raises a `KeyError` on the first request.

The header renders left to right: hamburger (narrow screens only), wordmark, breadcrumb, search
trigger, version chip, the two `llms.txt` links, your header links in order, the GitHub link, the
theme toggle. Below 768px the breadcrumb and the `llms.txt` links hide and the navigation collapses
into a drawer.

`MDJANGO_VERSION` is a display string. It does not select a version of the content.

## What is not configurable

The wordmark is text. There is no logo setting, and the header's layout, order and labels are part
of the House style. The colours and typeface it uses come from the seeds in
[Change the colours and type](../change-colours-and-type/).

## Check the result

Reload any docs page. Under `DEBUG` settings are read on every request, so no restart is needed. In
production, restart the workers: the rendered page is cached for `MDJANGO_CACHE_SECONDS`, and a
shared cache backend keeps the old header until that expires. See
[Run in production](../run-in-production/).
