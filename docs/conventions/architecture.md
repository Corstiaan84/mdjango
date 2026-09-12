# Architecture & file structure

**Scope: the Django projects on this stack** — **not** the `walden/` CLI. Two shapes share this
pattern: an **app-project** (a deployed Django site — e.g. `site/`) and a **distributable package**
(a reusable app shipped to other projects — e.g. `mdjango/`). They differ only where noted.

## Architecture

Server-rendered Django. Sprinkle JS via Stimulus. Business logic is organized by concept into
**feature packages** under `app/features/{concept}/` — plain Python packages, **not** Django apps
(no `migrations/`, no `apps.py` under a feature). Layers: `models.py` (ORM) is the data layer,
`features/` the business layer, `app/views/{feature}.py` the HTTP layer, `tasks.py` the async layer.
`features/` is HTTP-agnostic — no views, no `HttpResponse`, no `request` inside a feature. Each
feature exposes service classes; models hold schema and trivial helpers only; views handle HTTP
only. A package is a **cohesive domain area, not strictly one concept** (see `conventions.md`).

## App-project layout (deployed site)

```
.
├── manage.py
├── pyproject.toml           # Ruff + pytest config + PEP 735 dependency groups; run, not built
├── config/                  # Django project settings package (settings, urls, wsgi, asgi)
├── app/
│   ├── apps.py              # discovers feature models
│   ├── urls.py
│   ├── views/               # HTTP layer — CBVs, co-located by feature
│   │   ├── __init__.py      # non-feature pages (HomeView, …)
│   │   └── common/          # cross-cutting view plumbing (concept-named modules)
│   ├── conftest.py          # shared pytest fixtures
│   ├── features/            # business layer — one plain package per concept
│   │   ├── common/          # cross-feature DTOs / helpers + the DomainError base
│   │   └── {concept}/       # models.py, services.py, dtos.py, exceptions.py, tests.py
│   └── tests/               # view / cross-feature integration tests
├── templates/               # layouts/base.html, components/, non-feature pages
└── static/js/               # first-party JS only (Stimulus controllers)
```

## Distributable-package variant (reusable app)

A pip-installable app inverts a few things — it is **built**, not run, and has no project of its
own:

- **Packaging:** `[project]` + `[build-system]` (hatchling), not PEP-735 dependency groups. The
  wheel ships the package and its assets; it excludes tests and the theme *source*.
- **The app *is* the top-level package** (`mdjango/mdjango/`); there is **no `config/` settings
  package** — configuration is read from the *consumer's* Django settings via a `conf.py` accessor.
- **`templates/` and `static/` live *inside* the package** (`mdjango/mdjango/templates/`,
  `.../static/`), so Django's app-dirs loaders find them in any consumer and hatchling ships them.
- **Assets are vendored, never CDN-loaded** — a distributable can't assume a consumer's network or
  CSP, and must work in a static export. Ship a precompiled stylesheet and vendored JS; require **no
  consumer build step**. (An app-project may instead pull libs from a CDN via an import map.)
- **A dev/test harness** (`site/` + `manage.py`) stands in for the missing project: it's an
  example consumer that configures the app and serves its docs content, and is the pytest target. It is
  dev-only — excluded from the wheel.
- App-shaped concerns that don't apply: multi-tenancy, forms, migrations, a project `settings.py`.

Everything else — the feature-package layering, CBVs, the concept-named-module rule, DTOs, testing
homes, naming — is identical.
