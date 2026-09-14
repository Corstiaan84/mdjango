# 7. Sitemap and the crawler surface

Status: Accepted
Date: 2026-09-14

## Context

mdjango already publishes machine-readable views for LLM agents — the **LLM artifacts** (`llms.txt`,
`llms-full.txt`, per-page `.md`). Nothing addresses human search engines: there is no sitemap, no
`robots.txt`, and no guidance for the operator who mounts the docs and wants them indexed.

The defining constraint is that **mdjango has no domain, on purpose**. It is an app a Consumer mounts
at a prefix of *their* choosing (`/docs/`, or root in the `site/` harness), and every URL it emits is
root-relative, produced by Django's `reverse()`. There is no `SITE_ID`, no Sites framework, and no
base-URL setting — `reference/settings.md` states the invariant explicitly ("there is no setting for
… a canonical URL"), and the static export is deliberately domain-agnostic so a built tree is
portable to any mount prefix.

That collides with the three things asked for, each differently:

- A **sitemap** requires absolute `<loc>` URLs (protocol + domain) — which mdjango does not have.
- **`robots.txt`** and **`/.well-known/*`** are only honoured at the **domain root**, which the
  Consumer's project owns. mdjango, mounted at `/docs/`, cannot own them; `/docs/robots.txt` is
  invisible to crawlers.

## Decision

1. **Ship the `Sitemap` class; the Consumer owns the route.** mdjango provides
   `mdjango/sitemaps.py::DocsSitemap`, a `django.contrib.sitemaps.Sitemap` subclass whose `items()`
   is `RegistryBuilder.cached().ordered_pages` (plus the index Page) and whose `location()` is
   `page_url(page)`. The Consumer adds `django.contrib.sitemaps` to `INSTALLED_APPS` and mounts the
   standard sitemap view at **their own root** (`/sitemap.xml`). At runtime the domain is supplied by
   Django from the request (or the Sites framework) — **no new mdjango setting**. mdjango ships the
   class because it alone knows the page list (it is opaque behind the registry); the Consumer owns
   the route because only they own the root.

2. **The sitemap lists HTML Pages only.** The index Page and every `ordered_pages` entry, mapped
   through `page_url`. The LLM artifacts, the client-side search index, and the per-page `.md`
   alternates are **excluded** — they are machine files, not pages for a search engine to index.
   Drafts are already filtered out of `ordered_pages` by config, so no extra handling is needed.

3. **`<lastmod>` is optional and author-controlled.** A new optional frontmatter key
   `updated: YYYY-MM-DD` threads onto `Page.updated` (`date | None`); the sitemap emits `<lastmod>`
   only for Pages that set it. **File mtime is explicitly rejected** as the source: a `git clone` /
   CI checkout stamps every file with the *checkout* time, so mtime-based `lastmod` would read
   identical and wrong across all pages in exactly the deployments that matter, and Google discards a
   `lastmod` signal it finds unreliable. A malformed `updated` value is **ignored with a WARNING**,
   never a build error (the drafts-are-invisible-not-invalid spirit).

4. **The domain enters the package at exactly one boundary — the export `--base-url` flag.** The
   static export has no request to derive a host from, so an export sitemap needs a domain from
   somewhere. It is supplied as an `mdjango_build --base-url` **CLI flag, never a Django setting**:
   when passed, the export writes `sitemap.xml` with absolute `<loc>`s (and `<lastmod>` from
   `updated`); when omitted, no sitemap is written. Keeping it a build flag preserves the documented
   "no canonical-URL setting" invariant and keeps `conf.py` domain-agnostic — the domain touches the
   package only at the one place absolute URLs are genuinely unavoidable.

5. **`robots.txt` is documented, not shipped.** Because it is honoured only at the domain root the
   Consumer owns, mdjango cannot serve it for a subpath mount. The docs give a permissive
   copy-paste snippet (`User-agent: *` / `Allow: /` / `Sitemap: …`) that leaves the LLM artifacts and
   search index crawlable — duplicate-content dilution is a non-issue for docs, and the llms.txt
   convention *wants* those reachable. The `site/` harness, which *is* mounted at root, serves its own
   `robots.txt` through a `config/urls.py` entry — doing it the way the docs tell Consumers to.

6. **`/.well-known/*` is out of scope.** Root-only, and nothing a documentation app is responsible
   for (ACME challenges, `security.txt` are operator concerns). The llms.txt convention deliberately
   places `llms.txt` at the site root, not under `.well-known`, so there is nothing docs-shaped to put
   there. One sentence in the docs says so; no code.

## Consequences

- **These are the first absolute URLs mdjango emits.** The `--base-url` export path is the only code
  that produces protocol+domain URLs; everything else stays `reverse()`-relative. A future reader who
  finds it **must not** generalise it into an `MDJANGO_SITE_URL` setting or `<link rel="canonical">`
  tags — that would break the domain-agnostic invariant `reference/settings.md` promises. (Canonical
  and Open Graph URLs in the export are a plausible future built on the *same* flag, deliberately
  deferred, not started here.)
- **`Page` gains an `updated` field**, parsed in `RegistryBuilder._read_page`. This is the first
  frontmatter key kept beyond `title`/`weight`/`draft`/`description` (every other key is still
  discarded), and it is documented for authors beside those four, not in the deployment guide.
  (Cf. ADR 0004 §8, which added `Page.subsection`.)
- **The sitemap needs Consumer wiring** — `INSTALLED_APPS += ["django.contrib.sitemaps"]` and one
  urlpattern. That is documented, not automatic; mdjango cannot mount it for them without owning
  their root.
- **Docs surface:** a new `how-to/make-docs-discoverable.md` (the human-crawler twin of
  `how-to/publish-llm-artifacts.md`), a sitemap-route note in `reference/urls.md`, and the
  `--base-url` flag in `reference/mdjango-build.md`. `reference/settings.md`'s "no canonical-URL
  setting" line stays true and gains a pointer to the build flag.

## Alternatives considered

- **A hand-rolled sitemap view inside mdjango's own URLconf** (`/docs/sitemap.xml`). Rejected: it
  lands under the mount rather than at the root, and forces mdjango to build absolute URLs from the
  request itself — reimplementing what `contrib.sitemaps` already does, at a worse URL.
- **An `MDJANGO_SITE_URL` / base-URL Django setting.** Rejected: it breaks the documented "no
  canonical-URL setting" promise, makes emitted links a function of Consumer config, and puts a domain
  inside a package that is deliberately portable across mount prefixes. The build flag gives the
  export the domain it needs without any of that.
- **`<lastmod>` from file mtime.** Rejected: wrong under git/CI (checkout time, identical across
  pages), and an unreliable `lastmod` is worse than none. Author-set `updated` is accurate or absent.
- **Shipping `robots.txt` (a file or a view) from the package.** Rejected: correct only when mounted
  at root, silently wrong (invisible to crawlers) at a subpath — a distributable app cannot guarantee
  it owns the domain root.
- **Documenting the sitemap too, shipping no class.** Rejected: the page list is the one part that
  isn't trivial for a Consumer to reproduce — it lives behind the registry. Shipping the `Sitemap`
  class is exactly where mdjango adds value; the route, which needs the root, is left to the Consumer.

## Note on placement

`mdjango/sitemaps.py` is HTTP-coupled (it reads `request` to resolve the host), which by ADR 0002's
logic — the response cache lives in `views/common/` *because* it touches `request`/`HttpResponse` —
would argue for `views/common/`. It is placed at the package top level anyway, because a `Sitemap` is
a **framework-defined artifact** with a canonical home every Django developer expects
(`from mdjango.sitemaps import DocsSitemap`), unlike the bespoke response cache. This deviation is
recorded in `CLAUDE.md`'s deltas.
