---
title: Run in production
weight: 90
description: What changes when DEBUG is off — content read once, drafts hidden, caching on — and the two steps a deploy needs.
---

# Run in production

**Goal:** deploy a Django project that mounts mdjango, knowing which behaviours flip with
`DEBUG = False`.

**You need:** a working production setup for the Django project itself — WSGI/ASGI server, static
file serving. mdjango adds nothing to that stack and has no database tables.

## Collect the static files

The shell loads its stylesheet, fonts, controllers and vendored JavaScript through `{% static %}`.
Run `collectstatic` as for any app with static files:

```bash
python manage.py collectstatic --noinput
```

Everything ships inside the package under `static/mdjango/`; there is no build step and nothing is
fetched from a CDN at runtime.

## Validate the content before you start

A malformed Content tree — a fourth directory level, two files resolving to the same URL, a missing
content directory — raises on the first request that builds the registry, not at startup. Run the
gate in CI or as a release step:

```bash
python manage.py mdjango_build --check
```

## Know what DEBUG = False changes

Three settings default to `DEBUG`, so turning it off flips them together:

| Setting | With `DEBUG = True` | With `DEBUG = False` |
|---|---|---|
| `MDJANGO_ALWAYS_REBUILD` | tree re-read on every request | tree read once per worker process |
| `MDJANGO_INCLUDE_DRAFTS` | drafts visible | drafts hidden |
| response caching | off, `Cache-Control: no-cache` | on, pages cached 300 s, `Cache-Control: public, max-age=300` |

Set any of them explicitly to decouple it from `DEBUG` — see [Tune caching](../tune-caching/).

## Restart on content changes

With the tree read once per process, a content change is a deploy: restart the workers. There is no
file watcher and no cache purge command. If you serve the docs from a checkout that is updated in
place, restart after every pull.

## Prefer the export when you can

If nothing on the domain needs Django at request time, [export a static site](../export-a-static-site/)
and serve the directory instead. The output is the runtime output written to disk, so nothing is
lost, and the process-lifetime and restart concerns above disappear.
