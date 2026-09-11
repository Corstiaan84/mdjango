# Shared conventions

The engineering conventions for the **Django projects** in this monorepo — currently `mdjango/`,
and `site/` when it lands. They are the reusable law: layering, service design, DTOs, naming,
testing, the django-cotton mechanics, and the no-build frontend approach.

## Provenance

Harvested from the **mfo** project's `docs/guide/` (the origin of this stack), which marks its
reusable conventions for exactly this: extraction "when a second project forces the question."
mdjango is that second project. The mfo domain examples (balance sheets, banking, multi-tenancy,
DaisyUI, Turbo) have been scrubbed; what remains is the portable law. Where a rule depends on the
*shape* of the project, that is called out — a stateless distributable library (mdjango) doesn't
have tenants, forms, or a settings package, so those rules simply don't apply to it.

> **Status: first cut, harvested 2026-09-07.** Expect refinement when `site/` is built and exercises
> the app-shaped rules (multi-tenancy, forms, the DomainError→feedback middleware) that mdjango
> doesn't. Treat divergences a project documents in its own `CLAUDE.md` as deliberate, not drift.

## Files

- [`conventions.md`](conventions.md) — the engineering law: layering, interface-agnostic services,
  return values/DTOs, naming, testing, logging, style.
- [`architecture.md`](architecture.md) — the architectural pattern and file-structure: single app,
  feature packages, where each layer lives; app-project vs distributable-package variants.
- [`frontend.md`](frontend.md) — templates & django-cotton (the page/component taxonomy + the
  verified cotton gotchas), the no-build frontend (Stimulus, one controller per file), and the
  consolidating-styling rule.

## How a project uses these

Each project's `CLAUDE.md` `@`-imports the relevant files so they load into every session, then
records its own **deltas** (what it does differently and why). See `mdjango/CLAUDE.md` for the
worked example — a distributable library diverges from the app-shaped defaults in specific,
documented ways.
