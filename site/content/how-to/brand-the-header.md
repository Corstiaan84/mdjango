---
title: Brand the header
weight: 30
description: Set the wordmark, title, version chip and links from settings, or replace the header component to add a logo.
---

# Brand the header

**Goal:** make the header say your project's name, link to your places, and carry your logo.

**You need:** write access to the project's `settings.py`. For the logo, a directory listed in
`TEMPLATES[0]["DIRS"]`. Defaults for every setting are in the [settings reference](../../reference/settings/).

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

## Add a logo

There is no logo setting. The wordmark is text. To show an image, shadow the header component.

Create `templates/cotton/docs/header.html` in a directory listed in `TEMPLATES[0]["DIRS"]`:

```django
{% load static %}
<header class="docs-header">
  <div class="docs-header-inner">
    <button class="docs-hamburger" type="button" data-action="disclosure#toggle" aria-label="Open navigation">≡</button>
    <a href="{{ conf.home_url }}" class="docs-wordmark">
      <img src="{% static 'acme/logo.svg' %}" alt="{{ conf.brand }}" height="20">
    </a>
    <c-docs.breadcrumb :items="breadcrumb" />
    <div class="docs-header-spacer"></div>
    <button class="docs-search-trigger" type="button" data-action="search#open">
      <span class="k">/</span>
      <span class="label">search docs</span>
      <span class="kbd">⌘K</span>
    </button>
    {% if conf.version %}<span class="docs-version">{{ conf.version }}</span>{% endif %}
    {% if conf.llm_docs %}<a href="{% url 'mdjango:llms_txt' %}" class="docs-header-link docs-header-link--llm">llms.txt</a><a href="{% url 'mdjango:llms_full' %}" class="docs-header-link docs-header-link--llm">llms-full.txt</a>{% endif %}
    {% for l in conf.header_links %}<a href="{{ l.url }}" class="docs-header-link">{{ l.label }}</a>{% endfor %}
    {% if conf.github_url %}<a href="{{ conf.github_url }}" class="docs-header-link">github</a>{% endif %}
    <button class="docs-theme-toggle" type="button" data-action="theme#toggle" aria-label="Toggle dark mode">◐</button>
  </div>
</header>
```

This is the shipped header with one change: the wordmark wraps an image. The component receives
`conf` and `breadcrumb` as attributes. The `data-action` attributes wire the buttons to the shipped
Stimulus controllers and the class names pick up the shipped styles. Drop either and you own that
element.

Your file is found before mdjango's because cotton's loader chain reads `TEMPLATES["DIRS"]` before
app directories. [Replace part of the shell](../replace-the-shell/) covers the mechanism and what
else can be shadowed.

## Check the result

Reload any docs page. Under `DEBUG` settings are read on every request, so no restart is needed. In
production, restart the workers: the rendered page is cached for `MDJANGO_CACHE_SECONDS`, and a
shared cache backend keeps the old header until that expires. See
[Run in production](../run-in-production/).
