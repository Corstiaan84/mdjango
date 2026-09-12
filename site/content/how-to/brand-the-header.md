---
title: Brand the header
weight: 30
description: Set the wordmark, the browser title, the version chip, the GitHub link and extra header links.
---

# Brand the header

**Goal:** make the shell's header say your project's name and link where you want.

**You need:** write access to the consuming project's `settings.py`. All of these are plain Django
settings; the complete list with defaults is in the [settings reference](../../reference/settings/).

## Set the wordmark and title

```python
MDJANGO_BRAND = "acme"                 # the wordmark, left end of the header
MDJANGO_SITE_TITLE = "Acme documentation"   # <title>; defaults to the brand
MDJANGO_HOME_URL = "/"                 # where the wordmark links; defaults to "/"
```

The wordmark is a text string — there is no logo slot. To put an image there, shadow the header
component ([Replace part of the shell](../replace-the-shell/)).

## Show a version

```python
MDJANGO_VERSION = "v2.3.0"
```

This renders a small chip next to the search trigger. It is a display string only: mdjango serves
one version of the docs, and the chip changes nothing about routing. Leave it unset to hide the
chip.

## Add links

```python
MDJANGO_GITHUB_URL = "https://github.com/acme/acme"
MDJANGO_HEADER_LINKS = [
    {"label": "changelog", "url": "/changelog/"},
    {"label": "status", "url": "https://status.acme.example"},
]
```

`MDJANGO_GITHUB_URL` renders a link labelled `github` at the right end of the header; unset, it is
omitted. `MDJANGO_HEADER_LINKS` renders in the order given, between the `llms.txt` links and the
GitHub link. Each entry is a `{"label", "url"}` dict or an `mdjango.conf.HeaderLink`:

```python
from mdjango.conf import HeaderLink

MDJANGO_HEADER_LINKS = [HeaderLink("changelog", "/changelog/")]
```

On viewports 767px and narrower the header hides the breadcrumb and the `llms.txt` links; the links
reappear in the navigation drawer.

## Describe the site for machines

```python
MDJANGO_DESCRIPTION = "Deploy container apps to a server you own, with one config file."
```

This line does not appear in the header. It becomes the blockquote under the title in `llms.txt`
and `llms-full.txt` — see [Publish the LLM artifacts](../publish-llm-artifacts/).

## Check the result

Reload any docs page. The header reads, left to right: wordmark, breadcrumb, search trigger,
version chip, `llms.txt`, `llms-full.txt`, your links, `github`, theme toggle. Under `DEBUG` the
change is immediate; with `DEBUG = False`, restart the process — settings are read per request, but
rendered pages are cached ([Tune caching](../tune-caching/)).
