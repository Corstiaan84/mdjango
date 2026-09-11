# CLAUDE.md — mdjango

A reusable, drop-in markdown-documentation Django app (`pip install django-mdjango`, `import
mdjango`). See `CONTEXT.md` for the glossary, `docs/adr/` for decisions, `design/BUILD-PLAN.md` for
the implementation plan.

## Conventions

This project follows the shared Django-stack conventions, imported here so they load every session.
They were extracted from the walden monorepo with this app (root ADR 0002 / 0003) and now live in
this repo:

@docs/conventions/conventions.md
@docs/conventions/architecture.md
@docs/conventions/frontend.md

## mdjango's deltas from the app-shaped defaults

mdjango is a **distributable package**, not a deployed app-project — so several conventions apply in
their distributable variant, and a few app-only ones don't apply at all. These are deliberate:

- **Packaging:** `[project]` + hatchling (built, distributed), not PEP-735 run-not-built. The wheel
  ships `mdjango/` (templates + compiled `static/`); it excludes `tests`, `conftest.py`, the theme
  *source* (`theme/`), and the `example/` harness.
- **No `config/` settings package.** Configuration is read from the *consumer's* settings via
  `mdjango/conf.py`. The `example/` project is the dev/test harness (a stand-in consumer).
- **Assets vendored, no CDN, no consumer build, no toolchain.** One shipped stylesheet, built by
  `theme/build.sh` concatenating `theme/src/{fonts,reset,house}.css` through `theme/bundle.py` —
  **no Tailwind** (ADR 0005: it generated zero utilities and cost 2.2KB of `--tw-*` variables, a
  42MB binary download, and the `@layer` flattening that hid a specificity bug). Stimulus is the
  **vendored ESM** build resolved through an import map (`base.html`), not a CDN. Controllers are one-file-per-controller under `static/mdjango/controllers/`.
  **IBM Plex Mono is vendored too** — six `woff2` faces (400, 600, 400-italic × latin, latin-ext,
  87KB) under `static/mdjango/fonts/` with the OFL licence, declared via `@font-face` with paths
  relative to the stylesheet. `mdjango/tests/test_theme.py` fails if anything shipped fetches from
  an external host; that test exists because the Google Fonts `<link>` violated this rule for a
  while and the only symptom was the platform mono quietly replacing Plex.
- **Cotton dir stays default** (`templates/cotton/docs/…`), not `COTTON_DIR="components"` — forcing
  the global would clobber a consumer's own cotton setup.
- **`base` is an overridable cotton component** (ADR 0003), not the `{% extends layouts/base.html %}`
  page-binary — the whole point is a consumer can shadow the shell.
- **The content model is a live object graph, not pure DTOs.** `Page`/`Subsection`/`Section`/
  `Registry` (`features/content/dtos.py`) carry structure + trivial lookups and use
  `@dataclass(eq=False)` (identity — the group↔pages cycles make field-equality recurse). The
  three-level cap (ADR 0004) is enforced by the *shape*: a `Section` holds Pages and Subsections, a
  `Subsection` holds only Pages, so a fourth level is unrepresentable. Pure return DTOs
  (`Rendered`, `TocItem`) are frozen per the rule.
- **Every `services.py` is a class** (the house rule — `docs/conventions/conventions.md`), even the
  stateless ones: `RegistryBuilder` (content), `Renderer` (rendering), `SearchIndexer` (search),
  `DistExporter` (export), `LlmArtifactBuilder` (llm). Context that exists is constructor state
  (`RegistryBuilder(root, include_drafts)`, `DistExporter(output_dir)`); the build-once caches are
  `cached()`/`clear_cache()` classmethods on the owning service. Genuinely-pure helpers live in
  **concept modules**, not `services.py` — the frontmatter parser is `features/content/frontmatter.py`.
- **The response cache is view plumbing, not a service** (`views/common/caching.py`, ADR 0002): it
  is HTTP-coupled (touches `request`/`HttpResponse`, sets `ETag`/`Cache-Control`, returns `304`), so
  it lives in the view layer per the interface-agnostic-services rule — services stay HTTP-free.
- **N/A:** multi-tenancy, forms, migrations, Turbo — mdjango has no users, no DB, no mutations.

## Dev

```bash
./theme/build.sh            # compile the stylesheets (python3 only; --watch to rebuild on change)
python manage.py runserver  # serves example/ + demo content
pytest                      # content + rendering (beside code) + view/integration (mdjango/tests/)
ruff check . && ruff format .
```
