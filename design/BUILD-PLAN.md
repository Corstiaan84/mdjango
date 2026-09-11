# mdjango theme — build plan

The settled reading of the two docs mocks in this folder (`Walden Docs - Minimal` /
`… - Mobile`, and their `(Tailwind)` variants), from the design grill on 2026-09-07. This is the
implementation plan for mdjango's shell + theme. The *why* behind the non-obvious calls is in
[`../docs/adr/0003-opinionated-self-shelled-theme.md`](../docs/adr/0003-opinionated-self-shelled-theme.md).

**Mock caveat:** the mocks' text/config (`walden.toml`, `curl|sh`, single binary) is fiction —
filler for the design. mdjango renders whatever markdown it is given; content is the site's job.
The Tailwind variants still use the *old* var names (`--paper`, `--ink`, …) and absolute `px` — the
port must rename to the long-form tokens below and convert `px` to a `--font-size`-relative scale.

## 1. Tokens

Consumer override surface — **five seeds**: `--background`, `--foreground`, `--accent`, `--font`,
`--font-size`. Everything else is derived via `color-mix()` and locked.

| role | token | seed / derived |
|---|---|---|
| page background | `--background` | 🔑 seed |
| raised panels (code bg, search box, inline-code) | `--surface` | derived |
| hairlines / rules | `--border` | derived |
| strongest text (headings, wordmark, active nav) | `--foreground` | 🔑 seed |
| running paragraph copy | `--foreground-body` | derived |
| secondary (nav, captions, prev/next) | `--foreground-muted` | derived |
| faint (eyebrow labels, `$` prompt, placeholders) | `--foreground-subtle` | derived |
| optional accent (links/active if used; defaults to `--foreground`) | `--accent` | 🔑 seed |
| search-hit background | `--highlight` | derived |
| code / preformatted (always mono, not `--font`) | `--code-font` | baked |

- Colours are **runtime** CSS custom properties: Tailwind's colour tokens are defined *as*
  `var(--…)` (shadcn pattern), so `bg-background` → `background: var(--background)`. Layout is
  precompiled; the five seeds stay live for consumers.
- The type scale is **relative to `--font-size`** (root em/rem, no absolute px), so `--font-size`
  scales the whole site — chrome + prose — proportionally.
- House style (flat / mono / monochrome / layout) is **fixed**; only the five seeds move.

## 2. Shell & config (hybrid — ADR 0003 §3)

mdjango renders the full page by default; a consumer overrides `base.html` or shadows the header/
footer cotton components to substitute their own chrome. Default shell reads Django settings:
**brand** (title/logo string), **home_url**, **version** (display string), **github_url**, optional
**header links**. `version` is display-only — no version switcher (deferred).

## 3. What's generated vs authored

| chrome | source |
|---|---|
| left section-nav | **generated** from the content tree: `_index.md` sections, pages by `weight`. 2-level cap (section → page). |
| breadcrumb (`/ docs / quickstart`) | **generated** from page path + section title. |
| right TOC ("On this page") | **generated** from in-page headings, **H2 + H3**, with scroll-spy on both. |
| prev/next footer | **generated** — flattened weight order. |
| search index | **generated** at build from the registry (§7). |
| ~~"Where next" / related cards~~ | **cut.** Feature removed; rely on prev/next only. |

## 4. Components & behaviour (all net-new)

**cotton components**

| component | kind | notes |
|---|---|---|
| `base.html` (shell) | structural | `<html>`, head, fonts, `:root` tokens, no-flash script. Overridable. |
| `<c-docs.header>` | structural | brand slot, breadcrumb, search trigger, version, github, **theme glyph**. Overridable. |
| `<c-docs.sidebar>` | nav | left section-nav from registry; rendered in desktop rail **and** mobile drawer (one component, two placements). |
| `<c-docs.toc>` | nav | right "On this page", H2+H3; two renderings (sticky rail ≥lg, inline box <lg). |
| `<c-docs.breadcrumb>` | nav | from path. |
| `<c-docs.pager>` | nav | prev/next, auto. |
| `<c-docs.search>` | feature | ⌘K trigger + modal; two renderings (dropdown desktop / full-screen sheet mobile). |
| `<c-docs.article>` | structural | wraps rendered-markdown HTML. |
| `<c-copy-button>` | **general atom** | copy affordance; reused by code blocks **and** heading anchors. |

(No global footer — desktop mock has none; the footer slot renders nothing by default.)

**Stimulus controllers**

| controller | drives | general? |
|---|---|---|
| `search` | palette open/close (`/`, ⌘K, esc, click-out), MiniSearch query, ↑↓/↵/esc nav, hit highlight | feature |
| `clipboard` | copy code-block text **or** an anchor URL + transient "copied" state | **general** (both jobs) |
| `scrollspy` | IntersectionObserver over H2/H3 → active TOC link | feature |
| `disclosure` | mobile nav toggle (menu/close, close-on-navigate) | **general** |
| `theme` | flip `data-theme` on `<html>`, persist to `localStorage`, default OS | general |

Plus a **pre-paint inline `<head>` script** (not a controller) that sets `data-theme` before first
paint to kill the flash.

**Markdown pipeline extensions** (Python-Markdown + pymdown-extensions + Pygments): heading
**ids + `#` permalink**; **code fences** → Pygments, wrapped with `<c-copy-button>`; **TOC token
tree** (H2+H3) handed to `<c-docs.toc>`.

## 5. Dark mode

Persisted toggle (ADR 0003). A single faint glyph (`--foreground-subtle`) in the header **next to
github**. `theme` controller + localStorage, default `prefers-color-scheme`; `data-theme` on
`<html>`, set pre-paint to avoid flash.

## 6. Responsive — staged ladder

| width | layout |
|---|---|
| **≥ 1024px** (`lg`) | 3-column: sidebar · article · sticky TOC rail. |
| **768–1024px** (`md`) | 2-column: sidebar + article. TOC rail drops → **inline box** (under the intro, before the first H2). |
| **< 768px** | single column: sidebar → **hamburger drawer**, TOC inline box, search → **full-screen sheet**, header condensed. |

Mobile is **fluid** (100% width, ~20px gutter) — the mock's `max-w-[430px]` is just the artboard.

## 7. Search

Client-side **MiniSearch** over a `search-index.json` **generated from the registry during the one
build pass** (fields: `title`, `section`, `body`, `url`), served as a static asset, lazy-loaded on
first palette open. Works **identically in runtime and static-export** modes (just JSON + client
JS). Mock's result UX kept (title · section · preview snippet, keyboard nav); only the matcher
becomes MiniSearch. Deferred: index > ~1–2 MB → swap to Pagefind.

## 8. Prose styling

**Bespoke** prose CSS (not `@tailwindcss/typography`), scoped to the article, styling *all*
markdown output (h1–h6, lists, blockquotes, tables, hr, images, inline code, code blocks…). Written
against the **tokens** (colours via `var(--…)`, body via `--font`, code via `--code-font`) and
**`--font-size`-relative** sizing — so the five overrides stay fully live.

## 9. Port checklist (mock → mdjango)

Done in the scaffold (branch `mdjango-scaffold`):

- [x] Rename `--paper/--paper2/--line/--ink/--body/--sec/--faint/--mark` → long-form tokens (§1).
- [x] Convert absolute `px` type sizes → `--font-size`-relative `rem` scale.
- [x] Drop the hardcoded hex fallbacks (`var(--paper, #f7f3ea)`) — theme always defines the vars.
- [x] Derive the six locked stops via `color-mix()` from the seeds; don't hand-set them.
- [x] Precompile Tailwind (standalone CLI) → one shipped stylesheet; colours as CSS-var tokens.
- [x] Translate DCLogic state/handlers → the five Stimulus controllers (§4).

Note: the mock's derived stops were hand-tuned; the `color-mix()` percentages here approximate
them (and recompute for dark mode / consumer overrides for free). Exact percentage tuning against
the mock is a polish pass, not a blocker.

## 9a. Built vs pending (scaffold status)

**Built & tested (32 tests green):** package + hatchling packaging; config accessor (`conf.py`);
content model + build-once registry; render pipeline with TOC + code-copy wrap; CBV views + URLs;
the full cotton shell (base/header/sidebar/toc/breadcrumb/pager/article/search) with the compiled
stylesheet; all five Stimulus controllers incl. no-flash dark mode; a runnable `example/` project +
demo content. Structured to the stack conventions (`features/{content,rendering,search,export}`,
ESM Stimulus one-file-per-controller). **Search + static export (this increment):** **MiniSearch**
over a build-generated `search-index.json` (full page text, served by a runtime view *and* written
to the dist — same builder, ADR 0001); the earlier inline substring filter is retired. **Static
export** — `mdjango_build [dir]` writes a self-contained dir-per-page dist (mirrors the live URL
tree, incl. the landing page at the index URL, copies vendored assets, writes the search index);
verified serving standalone. **`--check`** renders every page + builds the index without writing —
the CI content gate.

**LLM artifacts + response caching (this increment — 50 tests green):** **LLM artifacts** — the
`llms.txt` family (`features/llm/`): `<mount>/llms.txt` (curated per-section index linking each
page's `.md`), `<mount>/llms-full.txt` (whole corpus in nav order), and per-page raw markdown at
`<page>.md` / `index.md`, discoverable via a `<link rel="alternate" type="text/markdown">` in each
page head. Built from the *same* registry, served at runtime *and* written into the dist (ADR 0001),
markdown-in/markdown-out (no render pass). **Response caching** (mdjango ADR 0002) — a server-side
page cache (LocMemCache) + `ETag`/`304` + `Cache-Control: public, max-age` on every GET, one knob
`MDJANGO_CACHE_SECONDS` (default 300; 0 disables), all suppressed under `DEBUG`/`always_rebuild`.
The response cache is view plumbing (`views/common/caching.py`), not a service.

**Pending increments (next):** exact `color-mix` tuning; heading-anchor *copy* (currently a plain
jump-link); collectstatic integration / relative-link portability for the export (currently absolute
`/docs/…`, `/static/…`). Note: `llms.txt` is served under the mount prefix (`/docs/llms.txt`), not
the site root — a consumer wanting the canonical `/llms.txt` adds a one-line redirect.

## 10. Deferred (unchanged from the initiative)

Multi-version docs · second theme → theme registry · MiniSearch → Pagefind at ~1–2 MB · second
mdjango consumer → extract to own repo/PyPI · auth/articles/authors.
