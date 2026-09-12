# 6. mdjango self-hosts its documentation

Status: Accepted
Date: 2026-09-11

## Context

mdjango was extracted from the walden monorepo into this standalone repo (its initial commit is
"django-mdjango extracted from the walden monorepo"). Two things that were true inside the monorepo
are now false: there is no sibling `site/` acting as the "first consumer", and the old plan — *"mdjango
graduates to its own repo/PyPI when a second consumer appears"* (`CONTEXT.md`) — has already been
overtaken, because the graduation happened proactively, without a second consumer.

A standalone docs engine still needs a public web presence of its own: a place that documents
mdjango and, being built with mdjango, demonstrates it. The question is what that presence *is* and
where it lives, given the repo already contains `example/` — a stand-in consumer project that wears
three hats (pytest target, `runserver` dev harness, and the reference sample a reader copies) and
whose content is walden-flavoured filler left over from the monorepo.

The tension: mdjango is "the one distributable, kept pure" (the wheel ships only the `mdjango/`
package; `example/` is excluded). Standing up a website must not compromise that, must not silently
couple the test suite to living prose, and — for a tool whose whole pitch is a fixed, opinionated
house style — should *show* that house style rather than a customised one.

## Decision

mdjango self-hosts its documentation as a **docs-only site**, served by a **single project** in this
repo. mdjango becomes **its own first Consumer**.

1. **Promote `example/` to `site/`.** The former example harness is renamed and repurposed into
   mdjango's real docs site: `MDJANGO_BRAND` flips `walden`→`mdjango`, and `content/` is rewritten
   from walden filler to mdjango's own documentation. One project keeps all four hats — pytest
   target, dev harness, deployed site, and canonical reference mount. It stays **excluded from the
   wheel**; the distributable remains package-only.
2. **Docs-only — no marketing landing.** The site's front door is the docs Index page (the root
   `_index.md` body, which mdjango renders). There is no separate Landing and no separate Chrome; the
   whole site is mdjango's own **Shell**, driven by config. A marketing page is rejected as premature
   for a pre-PyPI, scaffold-status tool — for a docs engine, good docs *are* the advert.
3. **Clean default mount.** `site/` wears the unmodified house style — no **Seed** overrides, no
   shadowed **Shell**. The flagship therefore advertises "adopt the opinion, get this for free", and
   the **Override surface** is taught in the docs prose (a theming page), not demonstrated by
   contorting the flagship into a customisation demo.
4. **Decouple the tests from the living docs.** `mdjango/tests/test_views.py` currently asserts
   against `example/content` as if it were a fixture (`<title>walden docs</title>`,
   `/docs/getting-started/quickstart/`, a `Secrets` nav link). Those end-to-end assertions move onto
   synthetic `tmp_path` trees (the pattern already used elsewhere in the file), so mdjango's real
   documentation is free to evolve without breaking CI.
5. **Runtime-served now; static export later.** The site is deployed as the running Django project
   for now. The eventual target is mdjango's own (forthcoming) static export — docs-only content is
   fully static — and publishing the site is intended to be the forcing function that finishes that
   feature. Its own domain is assumed, not a path under another site.

## Consequences

- **The old "first consumer / graduate on a second consumer" model is retired.** `CONTEXT.md`'s
  `Consumer` entry is rewritten around self-hosting, and a `Self-hosted site` term is added.
- **`example/` → `site/` was not the pure rename expected.** It touches `ROOT_URLCONF`,
  `manage.py`'s `DJANGO_SETTINGS_MODULE`, and the `pyproject` test config — but the project package
  cannot be named `site`: that shadows the standard library's `site` module, so `site.settings` is
  unimportable. Settings and urls moved into a `config/` subpackage (`config.settings`, with `site/`
  on the path) — the same layout walden's `site/` already uses.
- **One content tree serves three purposes at once** — mdjango's documentation, the site's content,
  and the reference sample. It is authored fresh; the reference role is preserved by keeping the
  "this is also the canonical mount" framing in the settings docstring.
- **The wheel stays pure.** As with `example/` before it, `site/` is repo-only; nothing about the
  self-hosted site ships to `pip install`ers.
- **The reference sample no longer demonstrates customisation.** That is deliberate (decision §3);
  it is a documentation gap to fill in prose, not in the harness.

## Alternatives considered

- **A separate `mdjango-site` repo (a distinct second consumer).** Rejected. Inside the monorepo this
  was the natural shape and the documented graduation trigger, but mdjango is *already* its own repo;
  a whole separate repo to serve docs-only, with duplicated mounting glue, is pure overhead.
- **Two projects in this repo — keep `example/` as a minimal stable fixture, add `site/` for the real
  docs.** Rejected in favour of one project. It cleanly separates "teaching example" from "our site"
  and keeps the test fixture stable, but the same decoupling is achieved by moving the end-to-end
  tests onto synthetic trees (decision §4), which is cheaper than maintaining two consumer projects.
- **Ship a runnable project in the wheel (`mdjango serve` + bundled docs).** Rejected. It would make
  "mdjango serves its own site" a literal feature, but it contradicts the wheel-purity rule, bloats
  the distributable with content and a deploy story, and over-builds for a docs-only site.
- **A marketing landing + docs (a second `site/`-shaped project with its own Chrome).** Rejected as
  premature — see decision §2.
