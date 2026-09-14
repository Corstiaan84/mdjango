---
title: How caching works
weight: 40
description: The three layers behind one setting, why an edit on a live server does not show, and why the default is public.
---

# How caching works

A docs page is the same bytes for every visitor. mdjango leans on that in three places, all governed
by one setting, `MDJANGO_CACHE_SECONDS`. This page explains the layers so the behaviour in
[Run in production](../../how-to/run-in-production/) is predictable rather than surprising.

## Layer one: the registry, once per process

The Content tree is read and parsed into a registry on the first request a worker handles, and held
for the life of that process. The search index and the two `llms.txt` artifacts are built the same
way, once, from that registry. Nothing watches the filesystem.

Under `MDJANGO_ALWAYS_REBUILD`, which defaults to `DEBUG`, all three are rebuilt on every request
instead. That is why an edit shows up on reload under `runserver` and does not on a deployed server.
In production, a content change is a deploy: the workers restart and read the tree again.

## Layer two: rendered HTML in Django's cache

Rendering a page means a markdown pass, Pygments over every code block, and a template render. The
result is stored in `CACHES["default"]` under the key `mdjango:page:<path>` for
`MDJANGO_CACHE_SECONDS`. A repeat request for the same path skips the render entirely.

The key is the path alone. That is safe for what a page depends on, the tree and the settings, as
long as neither changes while an entry is live. With the default in-process cache a restart clears
the entries along with the registry. With a shared backend such as Redis, a restart does not: the
old HTML keeps serving for up to the TTL, including a header or setting you just changed. Clear the
cache as a deploy step, or keep the number small.

Only the HTML page views use this layer. The search index and the markdown routes rebuild their
response from layer one on each request.

## Layer three: HTTP headers

Every response carries a strong `ETag`, the MD5 of its body, and `Cache-Control`. When caching is
on the header is `public, max-age=<MDJANGO_CACHE_SECONDS>`. Browsers and any CDN or proxy in front
of you may store the page and serve it without reaching Django. A request carrying a matching
`If-None-Match` gets a `304 Not Modified` with no body.

When caching is off (`MDJANGO_CACHE_SECONDS = 0`, or `MDJANGO_ALWAYS_REBUILD`) the header is
`no-cache`. The `ETag` is still sent, so conditional requests still get `304`s. A browser holding a
page revalidates every time and downloads it only when it changed.

## Why the default is public

For documentation anyone may read, `public` is the right default: it is what lets a CDN absorb the
traffic and what the static export's file server would send anyway. It is also the one setting that
is wrong for docs behind a login. `public` tells a shared cache that the response may be handed to
the next visitor, whoever they are. A project that gates the docs with authentication must set
`MDJANGO_CACHE_SECONDS = 0`. Nothing in mdjango detects that situation for you, because mdjango
knows nothing about your users.

## What is not cached

Settings are read on every request. Nothing about caching applies to the static export, which
writes files and lets the hosting server set its own headers. `mdjango_build` clears layer one
before it starts and ignores the setting.
