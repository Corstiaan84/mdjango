---
title: Make your docs discoverable
weight: 105
description: Wire a sitemap search engines can read, point a robots.txt at it, and know what mdjango leaves to your site root.
---

# Make your docs discoverable

**Goal:** let search engines crawl the docs — a `sitemap.xml` listing every page, a `robots.txt`
that points at it, and a clear line on what mdjango does *not* own.

**You need:** a served Content tree. This is the human-crawler counterpart of
[Publish the LLM artifacts](../publish-llm-artifacts/); the routes are in the
[URLs reference](../../reference/urls/).

The key fact shapes everything below: **mdjango has no domain.** It mounts under a prefix you choose
and emits root-relative URLs, so it stays portable across mounts and static exports. A sitemap needs
*absolute* URLs, and `robots.txt`/`.well-known` are only honoured at your **site root** — which your
project owns, not the docs app. So mdjango ships the one part it alone can (the page list) and leaves
the root to you.

## Add a sitemap

mdjango ships a `Sitemap` class; you mount the standard Django sitemap view at your site root. It
needs no extra package — `django.contrib.sitemaps` is part of Django, and it does **not** require
`django.contrib.sites` (it reads the domain from the request).

```python
# settings.py
INSTALLED_APPS += ["django.contrib.sitemaps"]
```

```python
# urls.py
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from mdjango.sitemaps import DocsSitemap

sitemaps = {"docs": DocsSitemap}

urlpatterns = [
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}),  # at the root, not under docs/
    path("docs/", include("mdjango.urls")),
]
```

`GET /sitemap.xml` now lists every HTML page — the Index page and every Page in navigation order —
as absolute URLs, with the scheme and domain taken from the request. The machine artifacts
(`llms.txt`, `llms-full.txt`, `search-index.json`, the `.md` alternates) are deliberately excluded:
they are for agents, not a search index. Drafts are excluded too.

> Behind a TLS-terminating proxy, set `SECURE_PROXY_SSL_HEADER` so Django builds `https://` URLs.
> This is ordinary Django deployment config, not an mdjango setting.

## Date your pages

A page can declare when it last changed, which becomes its sitemap `<lastmod>`:

```markdown
---
title: Roll back a deploy
updated: 2024-03-15
---
```

The key is optional and per-page: pages without it simply carry no `<lastmod>`. Use an ISO
`YYYY-MM-DD` date; a malformed value is ignored with a build warning. mdjango does **not** fall back
to the file's modification time — a `git clone` or CI checkout stamps every file with the checkout
time, which would make `<lastmod>` identical and wrong across the whole site.

## Add a sitemap to a static export

A [static export](../export-a-static-site/) has no request to read a domain from, so pass one:

```bash
python manage.py mdjango_build dist --base-url https://docs.example.com
```

This writes `dist/sitemap.xml` — at the export **root**, so it is served from your domain root —
with absolute `<loc>`s and `<lastmod>` from any `updated` dates. Without `--base-url` no sitemap is
written. The domain is a build-time argument, never a setting: mdjango stays domain-agnostic
everywhere else.

## Add a robots.txt

`robots.txt` is only read at your domain root, so mdjango can't serve it from under the docs mount —
you add it. A permissive file that points crawlers at the sitemap:

```text
User-agent: *
Allow: /

Sitemap: https://docs.example.com/sitemap.xml
```

Serve it however you serve other root files — a static file, or a small view:

```python
# urls.py
from django.http import HttpResponse
from django.urls import path
from django.views import View


class RobotsTxt(View):
    def get(self, request):
        sitemap_url = request.build_absolute_uri("/sitemap.xml")
        body = f"User-agent: *\nAllow: /\n\nSitemap: {sitemap_url}\n"
        return HttpResponse(body, content_type="text/plain")


urlpatterns += [path("robots.txt", RobotsTxt.as_view())]
```

Leave the LLM artifacts and search index crawlable. Duplicate-content dilution is not a real concern
for docs, and the [llms.txt convention](https://llmstxt.org/) wants those files reachable.

## What mdjango leaves to you

`/.well-known/` (ACME challenges, `security.txt`, and the like) is a site-root concern with nothing
documentation-shaped in it — mdjango neither serves nor documents it beyond this line. The llms.txt
convention puts `llms.txt` at the site root, not under `.well-known`, so there is nothing there to
point at the docs.
