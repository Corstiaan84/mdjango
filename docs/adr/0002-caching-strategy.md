# 2. Caching strategy

Status: Accepted
Date: 2026-09-07

## Context

Every docs response is a *pure function of the content tree*: there are no users, no sessions, no
per-request state (ADR 0001), so a given URL renders to the same bytes for every visitor for the
life of the process. Rendering that page is not free — Python-Markdown plus Pygments highlighting
runs on every request unless something remembers the result. The registry is already built once and
held in memory (ADR 0001), but the *rendered HTML* was not cached, and responses carried no HTTP
caching headers, so browsers and CDNs had to re-fetch and Django had to re-render on every hit.

ADR 0001 reserved this slot for a response cache "layered on top of" the registry. This is that
layer.

## Decision

Three cooperating layers, all governed by one knob — `MDJANGO_CACHE_SECONDS` (default `300`;
`0` disables) — and all suppressed whenever the registry rebuilds per request (`DEBUG` /
`MDJANGO_ALWAYS_REBUILD`), so development never serves stale bytes.

1. **Registry cache** (already present, ADR 0001): the parsed content tree, built once per process.

2. **Server-side page cache.** The HTML page views memoise their rendered HTML *string* in Django's
   cache framework (`LocMemCache` by default), keyed by page path. A repeat request returns the
   stored string and skips the markdown + Pygments + template pass entirely. The search index and
   the LLM artifacts have their own build-once caches, so they need no separate response cache.

3. **HTTP caching headers.** Every GET carries a strong `ETag` (an MD5 of the response body) so a
   conditional request (`If-None-Match`) is answered with a `304`, and a `Cache-Control`:
   `public, max-age=<MDJANGO_CACHE_SECONDS>` when caching is on, `no-cache` otherwise. This lets
   browsers and a CDN cache pages without touching Django at all — the largest win of the three.

The response cache lives as **view plumbing** (`views/common/caching.py`), not a service: it is
HTTP-coupled by nature (it reads `request`, builds `HttpResponse`, sets headers, returns `304`),
and the service layer stays interface-agnostic (conventions §"Interface-agnostic services").

## Consequences

- **Cache validity rides on the process lifetime.** The registry, the page cache, and the artifacts
  all assume content is immutable for the life of the worker — true after a deploy restart, false if
  someone edits content on a running non-`DEBUG` server. That is the same assumption ADR 0001
  already makes for the registry; the response cache does not widen it. A `LocMemCache` entry also
  dies with its worker, so a deploy clears it for free — no explicit invalidation step.
- **`Cache-Control: public` is a deliberate default.** mdjango serves trusted, public documentation
  (ADR 0001) — there is no per-user content to leak into a shared cache, so `public` is correct and
  gives CDNs something to work with. A consumer serving docs behind auth sets `MDJANGO_CACHE_SECONDS
  = 0` (headers become `no-cache`, server cache off) and layers their own policy. This is the one
  surprising knob, hence this ADR.
- **`ETag` is always emitted, even with caching off**, so conditional requests still 304. It is a
  content hash, so every worker computes the same tag for the same page and 304s stay consistent
  across a pool — no shared state needed.
- The static export is unaffected: a file server sets its own headers over the dist; mdjango's
  header layer is a runtime-serving concern.

## Alternatives considered

- **Django's `cache_page` decorator / `UpdateCacheMiddleware`.** Rejected. It caches the whole
  `HttpResponse` (pickled), keys on the full `Vary` set, and is awkward to switch off per request
  for `DEBUG`. Caching the HTML *string* and building the response around it is simpler, keeps the
  `304`/header logic explicit, and avoids response-pickling quirks.
- **Cache forever (`timeout=None`).** Rejected as the default. Content is immutable per process so it
  would be safe, but a finite `max-age` is the value a consumer actually wants to tune for their CDN,
  and one knob driving both the server TTL and the header is easier to reason about than two.
- **No server-side cache, HTTP headers only.** Tempting — the CDN/browser cache is the bigger win —
  but the first request behind every cache miss (and every crawler, and the CDN's own revalidation)
  still pays full render cost. The in-process string cache is a few lines and removes that.
