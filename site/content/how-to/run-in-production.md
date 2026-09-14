---
title: Run in production
weight: 90
description: Serve the shell's assets, set the cache, restrict the docs to signed-in users, and ship a content change.
---

# Run in production

**Goal:** serve the docs from your deployed Django process, alongside everything else it does, with
caching that matches who may read them.

**You need:** a project that serves mdjango under `runserver`. Setting defaults are in the
[settings reference](../../reference/settings/). The three cache layers are explained in
[How caching works](../../explanation/how-caching-works/).

## Serve the static assets

The Shell needs mdjango's stylesheet, fonts and controllers from your `STATIC_URL`. Django does not
serve static files with `DEBUG = False`. Collect them and serve them the way you serve the rest of
the project's static, for example with WhiteNoise:

```bash
python manage.py collectstatic --noinput
```

Nothing is fetched from a CDN. If your CSP blocks inline scripts, allow the short inline theme
script in `<head>`, or shadow the base component and move it to a file.

## Know what DEBUG turns off

Two settings default to `DEBUG`:

| Setting | Under `DEBUG = True` | Under `DEBUG = False` |
|---|---|---|
| `MDJANGO_INCLUDE_DRAFTS` | drafts are served | drafts are hidden |
| `MDJANGO_ALWAYS_REBUILD` | the tree is re-read on every request and nothing is cached | the tree is read once per process and pages are cached |

Set either explicitly if you need the other behaviour in an environment.

## Set the cache for public docs

```python
# settings.py
MDJANGO_CACHE_SECONDS = 300   # the default
```

One setting drives two things: the rendered HTML is stored in Django's default cache for that many
seconds, and every response carries `Cache-Control: public, max-age=300`. Browsers and any CDN in
front of you may cache the page and serve it without touching Django. Every response also carries a
strong `ETag`, and a matching `If-None-Match` gets a `304`.

Raise the number for docs that change rarely behind a CDN. `0` turns the server-side cache off and
sends `Cache-Control: no-cache` instead.

## Restrict the docs to signed-in users

mdjango's views are plain class-based views with no authentication of their own. They sit behind
whatever middleware the project has. To require login, use Django's middleware and set the cache to
zero:

```python
# settings.py
MIDDLEWARE = [
    # ...
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.auth.middleware.LoginRequiredMiddleware",
]

MDJANGO_CACHE_SECONDS = 0
```

The second line is not optional. `Cache-Control: public` tells a shared cache it may store the
response and serve it to the next visitor, whoever they are. With the setting at `0` the header is
`no-cache`. The `ETag` is still emitted, so a browser that already holds a page still gets `304`s.

The search index, the `llms.txt` files and the `.md` alternates are routes under the same mount, so
the middleware gates them too. The search palette fetches its index with the visitor's session
cookie.

## Ship a content change

With `DEBUG = False` the Content tree is read once per worker process and held for the life of that
process. A content change is a deploy: restart the workers.

If `CACHES["default"]` is a shared backend such as Redis or Memcached, a restart does not clear it.
Rendered pages keep serving from it for up to `MDJANGO_CACHE_SECONDS` after the deploy, and so does
a page whose header or settings you changed, because the cache key is the page path alone. Either
accept the delay, clear that cache as a deploy step, or set the number low enough not to matter.
With the default in-process cache a restart clears everything.

Run `mdjango_build --check` before the deploy. A broken tree is a 500 on the first request, not a
startup error. See [Validate content in CI](../validate-content-in-ci/).

## Mount constraints

Mount with `path("<prefix>/", include("mdjango.urls"))` and nothing else. The URLconf sets its own
`mdjango` namespace, and the templates and services reverse routes by that name, so passing a
different `namespace=` to `include()` or mounting the URLconf twice breaks every internal link.

## If you only need the docs

A Django process is the right host when the docs share a deployment with the rest of your project.
When a project needs nothing but the docs, [Export a static site](../export-a-static-site/) writes
the same pages to a directory for any static file host. The export has no login gate and no
caching settings. The server that hosts it decides those.
