# Conventions — the engineering law

**Scope: the Django projects on this stack** (`mdjango/`, and `site/` when it lands). **Not** the
`walden/` CLI — that is stack-agnostic and keeps its own conventions in `walden/docs/`. Frontend/
template/styling conventions live in [`frontend.md`](frontend.md); the structural pattern in
[`architecture.md`](architecture.md).

## Layering — strict

- **Models:** schema, `__str__`, `get_absolute_url`, lightweight computed properties, custom
  managers/querysets. No business logic. (A library with no database has no model layer.)
- **Views** (`app/views/{feature}.py`): parse input, call a service, render. No business logic, no
  multi-model orchestration. **Always class-based views** (Django generic CBVs); never
  function-based. Non-feature pages live in `app/views/__init__.py`. Parse request body/query input
  through a Django `Form`/`ModelForm` — never read `request.POST`/`request.GET` ad hoc; pass the
  validated `cleaned_data` to services. (URL-path kwargs are already typed by their converter and
  need no form; an input-free view needs none.) Cross-cutting view plumbing (a mixin/helper used by
  more than one feature's views) lives in a **concept-named** module under `app/views/common/`.
- **Services** (`app/features/{concept}/services.py`): **always a class — never bare module-level
  functions.** One concept-named service class per `services.py`, its operations as methods. This
  is a firm house rule: a service is a class *even when it holds no state yet* — a trivial
  `class Renderer: def render(self, body): …` is preferred over a free `render()` function, because
  the class is the consistent, discoverable home for a feature's logic and the natural place state,
  config, or an injected dependency lands the day it appears (no function→class churn later). When
  the service does carry context (an app's `user`/`scenario`/tenant; a build's `output_dir`/root),
  that context is constructor state instead of an argument threaded through every call. A feature
  package is a **cohesive domain area, not strictly one concept** — tightly-coupled concepts sharing
  a lifecycle live together; a concept earns its own package only when its lifecycle is genuinely
  independent. A package holds `models.py`, `services.py`, `dtos.py`, `tests.py`, and other
  **concept-named** modules as needed. Feature packages are HTTP-agnostic.
  *(This is stricter than upstream mfo, which tolerated free functions for concept-module-style
  logic; here `services.py` is uniformly class-based.)*
- **Concept modules** (code that doesn't fit a standard layer — an HTTP client, a retry/backoff
  helper, a value object, a stand-alone parser) live in a module **named for the concept**
  (`clients.py`, `backoff.py`, `frontmatter.py`) — **never** a catch-all
  `utils.py`/`helpers.py`/`utilities.py`, and this is where genuinely-generic **plain functions**
  belong (they are not `services.py`). Promote a concept module to a class once two or more of its
  functions would share the same configuration or injected dependency.

## Interface-agnostic services

Assume from day one that a second adapter — a management command, a background job, a future API —
will sit beside the HTTP views. Every service must be callable from any adapter:

1. **Plain-Python arguments only.** Services take primitives and model instances — never `request`,
   `cleaned_data`, a `QueryDict`, or other framework types. Translating the adapter's native input
   into clean arguments is the adapter's job.
2. **Domain exceptions only.** Services raise domain errors, never HTTP-specific ones (`Http404`)
   and never `ValueError` for domain conditions. A `DomainError`/`<App>Error` base plus genuinely
   cross-cutting errors live in `app/features/common/exceptions.py`; feature-specific errors live in
   `app/features/{feature}/exceptions.py` and subclass the base. Each adapter maps them to its own
   convention (views → status codes, commands → exit codes, jobs → retry/dead-letter).

If code couples a service to HTTP — takes a `request`, returns an `HttpResponse`, raises `Http404`,
reads `request.GET` — that is a layering violation. Push the coupling back into the adapter.

## Return values

Scalars and simple optionals are returned directly — no wrapper. Any result with named fields is a
**frozen `@dataclass`**, never an ad-hoc dict (reserve dicts for genuinely dynamic maps). DTOs live
in the producing feature's `dtos.py`, or `common/` once a second feature returns the same type; they
hold no logic and no business methods, and are named for the concept (no `DTO`/`Schema` suffix).
Fields are primitives, `Decimal`, or nested DTOs so any adapter can serialize them.

## Naming

PascalCase models, snake_case fields and functions. Custom managers expose intent-named methods.
Service classes are PascalCase, named for the concept; the feature package takes the same concept
name (`balance_sheet/`, not `balance_sheet_service/`).

## Multi-tenancy *(app-shaped only)*

For a user-facing app: every query is scoped via a service helper taking `user`; views never query
across the tenant boundary; the site is login-gated fail-closed with explicit `@login_not_required`
opt-outs; the tenant is resolved through one named seam, never `request.user` directly. **N/A to a
stateless library** with no users (e.g. mdjango).

## Testing

pytest-django + coverage.py. **Feature/business tests live beside the code** in
`app/features/{concept}/tests.py`; **view and cross-feature integration tests** live in `app/tests/`
and use Django's test client. Shared fixtures go in `app/conftest.py` (package root). Plain `pytest`
fixtures first; factory-boy only when setup density hurts. This suite is the committed regression
layer; visual/behavioural verification (driving a real browser) is a separate, throwaway workflow
that commits no files.

## Migrations *(app-shaped only)*

Review every auto-generated migration before committing — Django sometimes mis-detects renames as
drop+add. Keep data migrations separate from schema migrations. Do not squash. Don't chase
zero-downtime patterns until real users can be inconvenienced.

## Logging

stdlib `logging`, one logger per module (`log = logging.getLogger(__name__)`), configured centrally
through `LOGGING` in settings — never `print`, never ad-hoc per-call handler setup. **INFO** for a
one-line outcome per operation; **DEBUG** for the per-item decision tree (one prefixed line per
record/branch, greppable); **WARNING/ERROR** for recoverable/fatal faults. Verbosity is a log-level
concern set once on the root `app`/package logger, **never a function parameter** — a `verbose=`
flag on a service is the same layering violation as passing it a `request`.

## Style

Ruff handles lint and format (config in `pyproject.toml`; lint select includes `DJ`). No separate
Black / isort / Flake8.
