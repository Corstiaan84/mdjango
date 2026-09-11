# Frontend, templates & components

**Scope: the Django projects on this stack** (`mdjango/`, and `site/` when it lands) — **not** the
`walden/` CLI, which has no frontend.

The template page-vs-component taxonomy, the django-cotton mechanics (the verified gotchas), the
no-build frontend, and the consolidating-styling rule. Portable; a project's specific component
inventory, CSS framework (Tailwind/DaisyUI), and whether it uses Turbo are project choices layered
on top.

## Templates

Feature **page** templates live in `app/templates/{feature}/`, auto-discovered (`APP_DIRS: True`);
template names omit the `app/` prefix. The root `templates/` tree holds cross-cutting files only:
`layouts/base.html` (the page shell, extended by every page), non-feature pages, `admin/` overrides.

**Page vs. component is a hard binary.** A template is either a **page** — has a URL route and
`{% extends "layouts/base.html" %}` — or a **component**, invoked as a `<c-… />` tag (or
`cotton.render_component(request, name, ctx)` from a view). There is no third "view-rendered
partial" category and **no `_`-prefixed include partials**. Component layout: `components/ui/*` for
cross-cutting design-system atoms, `components/*` for structural shells, `components/{feature}/*` for
feature components (folder named for the Python feature package, underscored). Declare optional props
with defaults via `<c-vars>`; `{{ attrs }}` passthrough is strict — only on leaf atoms that get
JS/behaviour hooks at the call site, never on structural shells.

> **Distributable variant:** a reusable app keeps its components under the default cotton dir
> (`templates/cotton/…`) rather than forcing `COTTON_DIR="components"` — a global that would clobber
> a consumer's own cotton setup. It may also ship an **overridable `base` as a cotton component**
> (so a consumer substitutes chrome by shadowing it) rather than the `{% extends %}` page-binary.
> Both are deliberate, documented in the project's `CLAUDE.md`.

**Reach for a component early** — it's a way of building, not just a DRY payoff; a single-use
component is fine. Every inline `<svg>` is an icon component (`components/ui/icons/<name>.html`),
never pasted raw. When porting a mock, the **component breakout is a first-class step**: inventory
the screen and, per piece, **reuse → extend additively → build new**; classify each new component
general-purpose vs feature-specific; name what it retires. The existing tokens, semantic classes,
and components **win** over a mock's inline styles / arbitrary values.

## django-cotton mechanics (verified against 2.7.x — each silently misbehaves otherwise)

1. **Filenames are snake_case**; the kebab in a multi-word tag maps to an underscore —
   `<c-ui.stat-card>` → `components/ui/stat_card.html` (cotton never looks for `stat-card.html`).
2. **`:prop="expr"` does not evaluate template filters** — a filtered value comes through empty.
   Pass a pre-formatted *string* prop with interpolation (`value="{{ x|floatformat:0 }}"`); pass raw
   numerics/model instances with `:prop="x"` so the type (and `Decimal`/`None`) is preserved.
3. **An optional numeric prop guarded by `{% if p != None %}` needs an explicit `<c-vars p=None />`**
   (an omitted attr is `""`, which is `!= None`).
4. **Components are context-isolated from caller *locals*** (loop vars, `{% with %}`) but **do**
   inherit context-processor vars like `request`. Markup that must reach a caller loop var or
   `{% csrf_token %}` goes through a **named slot** (`<c-slot name="x">…</c-slot>`, read as
   `{{ x }}`), which renders in the call-site context.
5. **`render_component(request, "feature.name", ctx)` returns a string** — a view returns
   `HttpResponse(render_component(...))`; the dotted name maps hyphens→underscores in the filename.
6. **A bare `{% … %}` tag inside a `<c-…>` opening tag is NOT evaluated** — cotton captures it as
   literal attribute text. A **conditional attribute** (`checked`/`disabled`/…) must be a boolean
   prop resolved in the component body (`<c-vars checked=False />` + `{% if checked %} checked{% endif %}`),
   never a bare `{% if %}` in the call tag. (A `{% … %}` inside a *quoted* attr value is fine.)
7. **`:prop="expr"` does a plain variable/attribute lookup, not a Python expression** — operators
   don't evaluate (`:disabled="not dirty"` yields falsy). Precompute the boolean and pass the name.

## Frontend (no build)

**Stimulus controllers, one file per controller** under `static/js/controllers/`, named
`{name}_controller.js`, each exporting a `default class extends Controller`. A small
`application.js` boots the app and registers them. The server returns **HTML, never JSON**, for
in-app interactions.

No bundler is needed. Two no-build ways to load ES modules, by project shape:

- **App-project:** libraries via a CDN import map (`application.js` + controllers as modules).
- **Distributable:** the same, but the import map points at **vendored** ESM files (`{% static %}`
  URLs), so nothing depends on a CDN and it works under a consumer's CSP and in a static export.
  mdjango vendors Stimulus's ESM build and maps `@hotwired/stimulus` to it.

Turbo (page transitions / partial replacement) is an **app-project** choice; a content-static
distributable like mdjango doesn't use it.

## Consolidating styling

A cotton component is the **first home** for a repeated class mix — the component owns the markup +
classes, one source of truth, no CSS class needed. Reach for a **semantic class** in the project's
one stylesheet only when a mix is shared across many components and is awkward as a wrapper. Write
semantic classes as **plain CSS over the design tokens**, never re-derive the mix inline. The design
system is a frozen `design/` handoff — **reference only, never loaded at runtime**; it is
*translated* into the app's stylesheet, not wired in. Light/dark is a persisted toggle with a
no-flash `<head>` script applying it before first paint. Use `{% comment %}` for multi-line template
comments — multi-line `{# #}` leaks as page text and breaks parsing if it contains a `{% %}` tag.
