---
title: Tune caching
weight: 60
description: One setting governs the page cache and the HTTP headers; turn it off for docs behind a login, and know when a restart is needed.
---

# Tune caching

**Goal:** get the caching behaviour you want from a docs site whose every response is the same
bytes for every visitor.

**You need:** a running mount with `DEBUG = False` — caching is off entirely while `DEBUG` (or
`MDJANGO_ALWAYS_REBUILD`) is on, so edits show up immediately in development.

## Understand the three layers

1. **The content registry** — the parsed Content tree, built on the first request and held in
   memory for the life of the worker process.
2. **The page cache** — each page's rendered HTML string, stored in your project's *default* Django
   cache backend (`LocMemCache` unless you configured another) under the key `mdjango:page:<path>`.
3. **HTTP headers** — a strong `ETag` on every response, answering `If-None-Match` with `304`, and a
   `Cache-Control` header.

One setting governs layers 2 and 3:

```python
MDJANGO_CACHE_SECONDS = 300   # the default
```

With it on, pages are cached for that many seconds and every docs response — HTML, `search-index.json`,
`llms.txt`, per-page `.md` — carries `Cache-Control: public, max-age=300`. Set it to `0` and the page
cache is skipped and the header becomes `Cache-Control: no-cache`; the `ETag` stays, so browsers
still revalidate cheaply.

## Turn it off for docs behind a login

`Cache-Control: public` tells shared caches and CDNs they may store the response. If your docs sit
behind authentication, that is the wrong instruction:

```python
MDJANGO_CACHE_SECONDS = 0
```

Then apply your own policy in middleware or at the proxy.

## Match a CDN's expectations

The `max-age` is what a CDN honours. Raise it if content changes rarely; the ETag lets clients
revalidate against the origin for free. There is no cache-busting or purge hook — a deploy is the
invalidation event.

## Change content on a running site

The registry (layer 1) is built once per worker and never re-read while the process lives. Editing
a file under `MDJANGO_CONTENT_DIR` on a running `DEBUG = False` server changes nothing until the
process restarts. Each worker in a pool holds its own copy; `LocMemCache` is per worker too, so a
restart clears everything at once.

If you need edits to appear without a restart, turn on per-request rebuilding — and accept that it
also disables the page cache and the `public` header:

```python
MDJANGO_ALWAYS_REBUILD = True
```

This re-parses the whole tree on every request; it is a development setting.

## Share the page cache across workers

Point your project's default cache at a shared backend (for example Redis) and every worker reads
the same rendered pages. The cache key is the page path alone — safe because a page's HTML depends
on nothing but the content tree and settings. Restart all workers together after a content change,
or a worker with a stale registry can re-populate the shared cache with old HTML.
