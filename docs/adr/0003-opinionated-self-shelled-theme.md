# 3. Opinionated, self-shelled theme

Status: Accepted
Date: 2026-09-07

(ADR slots 0001 "dual-output render core" and 0002 "caching strategy" are reserved for the
render/serve subsystems and will be written when those are built. This one is written first
because it is the decision the first design forced.)

## Context

mdjango is a **drop-in** docs app: a consumer installs it, points it at a tree of markdown, and
gets a finished documentation site. That promise forces a choice about how much of the look is
fixed versus themeable. A neutral, fully-themeable base would maximise flexibility but reproduce
the "assemble your own docs theme" burden mdjango exists to remove.

The first design (walden's docs — see `../../design/`) is a specific **house style**: a warm
off-white ground, IBM Plex Mono throughout (body included), flat 1px borders, **monochrome — no
accent colour**, light + dark. It also renders the **entire page** — header (wordmark, breadcrumb,
search, version, github, theme toggle), left section-nav, article, right table-of-contents,
prev/next — not just the article body.

## Decision

1. **One baked house style, not a theme system.** mdjango ships exactly one theme (light + dark).
   The flat / mono / monochrome personality *and* the layout are fixed; a consumer adopts them or
   forks. A multi-theme registry is deferred until a real second theme exists.

2. **Two colour ramps, each set by its ends; the middle derived and locked.** *(Revised
   2026-09-10 — see the amendment note below for what this replaced and why.)* The palette is two
   ramps:

   ```
   surface ramp:  --background ..... --surface ..... --border
   text ramp:     --foreground ..... --foreground-body ..... --foreground-muted ..... --foreground-subtle
   ```

   A consumer sets the **four ends** — `--background`, `--border`, `--foreground`,
   `--foreground-subtle` — plus `--accent` (defaults to `--foreground`, keeping it monochrome out
   of the box), `--font` and `--font-size`. The three interior stops (`--surface`,
   `--foreground-body`, `--foreground-muted`) are `color-mix()`-derived **within their own ramp**
   and are **not** overridable, so a consumer cannot break the intermediate contrast steps.

   Mixing inside a ramp rather than across the whole palette is the load-bearing part. Code is
   always `--code-font` (monospace), independent of `--font`. The type scale is expressed
   **relative to `--font-size`**, so one knob scales the whole site — chrome and prose —
   proportionally; `mdjango/tests/test_theme.py` guards both promises against the compiled sheet.

   `--highlight` is **dropped**. It sat on neither ramp (it is the palette's most chromatic stop)
   and nothing referenced it — the design uses that tone to highlight matched substrings in search
   results, which mdjango does not do yet. It returns as a **seed**, not a derived stop, if that
   feature is built.

3. **mdjango owns the whole shell, driven by config, overridable by templates (hybrid).** Out of
   the box mdjango renders `<html>`, header, nav, article, TOC (and an empty footer slot) from
   Django settings: brand title/logo string, `home_url`, `version` (display string), `github_url`,
   optional header links. A consumer who wants their own chrome overrides `base.html` or shadows
   the header/footer cotton components. *(Colour and type do **not** require this — those load via
   the `MDJANGO_EXTRA_CSS` setting; see the 2026-09-14 amendment.)* `version` is a display string
   only — multi-version docs are deferred.

4. **Bespoke prose CSS, not `@tailwindcss/typography`.** All rendered-markdown elements are styled
   by hand against the tokens, so there is no `--tw-prose-*` remapping layer between the plugin's
   palette and ours.

## Consequences

- A consumer gets a finished, coherent docs site from three colours + a font, and **cannot** produce
  a low-contrast mess — the derived stops guarantee the ladder.
- A consumer who needs a fundamentally different look must **fork templates**. A sans body *is*
  reachable through `--font` (code stays mono), but a different layout, a card/bordered restyle, or
  an independent border hue is not. Accepted: this is the price of "drop-in".
- The override contract (`--background` … `--font-size`) is a **public API**. Renaming or dropping a
  seed is a breaking change for consumers and must be versioned as one.
- Porting the mocks is not mechanical: their absolute `px` must become a `--font-size`-relative
  scale, and their `--paper/--ink/...` variables must be renamed to the long-form tokens — or
  `--font-size` becomes a dead knob and colour/size overrides silently fail.
- **Amendment (2026-09-10): decision 2 originally had five knobs and six derived stops, deriving
  every stop from `--background` and `--foreground` alone. That model could not reproduce the
  design and could not have reproduced any tinted palette.** Measured in OKLab, the design's
  mid-tones are *more chromatic than either endpoint* — `--foreground-subtle` `#a2947f` has
  C=0.034 while `--foreground` is 0.018 and `--background` 0.013. A straight line between two
  points cannot bulge outward, so mixing text toward the background necessarily averages its
  chroma down: the whole ladder shipped visibly greyer than the design (up to 10/255 per channel
  on `--foreground-subtle`), and *any* consumer with a warm or tinted palette would have been
  desaturated the same way. It was a model error, not a tuning error.

  The fix was to notice that the design's stops **are** collinear — within each ramp, not across
  the palette. Promoting `--border` and `--foreground-subtle` from derived to seed gives each ramp
  its two ends and makes the three interior stops exact (worst case 2/255 per channel, both
  themes — verified by measuring computed styles in a real browser against the rendered mock, not
  by reading the CSS; 1/255 is the floor, since the design's own interior stops sit a hair off the
  exact OKLab line between its ends). Net effect: consumer-settable tokens 5 → 7, total tokens 11 → 10, and the guarantee is
  *stronger* than before, because the interior stops now genuinely track the ends a consumer set
  — under the old model they tracked the wrong thing. The dark theme re-states the two text ratios
  (48.6% / 18.9% vs 54.9% / 32.6%) because its ladder is deliberately compressed at the
  low-emphasis end; the surface ramp's 59% serves both.
- **Amendment (2026-09-14): the seed override surface loads through a setting, `MDJANGO_EXTRA_CSS`,
  not by shadowing `base.html`.** Decision 2 makes the seven seed *names* a public API, but a
  consumer still has to get their stylesheet into the `<head>`, and originally the only documented
  route was to copy the shipped `base.html` into `TEMPLATES["DIRS"]` and add a `<link>`. That
  contradicted this ADR's own position that the templates' markup and class names are **not** a
  versioned promise: it sent every *theming* consumer to copy a file mdjango may change in any
  release. `MDJANGO_EXTRA_CSS` (a `{% static %}` name, or an iterable of them) is now read in
  `conf.py` and rendered as one `<link>` per entry — after mdjango's own sheet, so an
  equal-specificity `:root` rule wins on the flat unlayered sheet. `mdjango_build` resolves each
  name through the staticfiles finders and copies it into the static export, warning on any it
  cannot resolve so a themed export is never a silent 404. The seed *values* still live in CSS per
  decision 2 — the setting only *loads* the stylesheet, it carries no colour — so this is additive,
  not a reversal. Template shadowing stays the escape hatch for *chrome* (decision 3); it is no
  longer the route for colour and type.
- **Amendment (2026-09-16): a Consumer injects head content — analytics, a verification `<meta>` —
  through one sanctioned, empty, shadowable component (`cotton/docs/head_extra.html`, rendered at the
  end of `<head>`), not through a setting and not by copying `base.html`.** Decision 3 owns the whole
  shell, and mdjango renders the entire `<html>`/`<head>`, so a Consumer has *no seam* into the head —
  even at runtime, inside their own Django — without a hook mdjango provides. The need is a
  third-party tracking `<script>` (external `src`, sometimes with an inline bootstrap, GA4-style).
  Four shapes were weighed:
  - **A raw-HTML string setting** (`MDJANGO_HEAD_HTML` + `mark_safe`) — rejected. It carries any
    snippet and the static export writes it verbatim for free, but it is the first `mark_safe`-on-
    consumer-input precedent and, being unbounded, silently reopens the "Consumer supplies head
    chrome" door this ADR shut: today analytics, tomorrow a chat widget or a cookie banner.
  - **A file-based hook** reusing the `MDJANGO_EXTRA_CSS` static-name→finder→copy machinery —
    rejected. It can only serve *same-origin* vendored JS; a third-party analytics script must load
    from the vendor's host, which is the whole point. Fine for a self-hosted script, useless for the
    stated case.
  - **A structured provider registry** (`MDJANGO_ANALYTICS = {"provider": …}`) — rejected. It keeps
    the invariants (no raw HTML, no `mark_safe`, a CSP hint even) but puts mdjango on a maintenance
    treadmill tracking each provider's snippet, and cannot serve an unnamed/arbitrary tool.
  - **Shadowing the whole `base.html`** — rejected as the *same* regression the 2026-09-14 amendment
    killed for CSS: to add one tag a Consumer would reproduce `<title>`, the no-flash script, the
    stylesheet links, the `MDJANGO_EXTRA_CSS` loop, and the import map — an unversioned chunk mdjango
    may change in any release.

  The chosen shape is a *scoped* shadow: one tiny component whose entire published contract is "your
  head tags go here." It is head-only **by construction** (it renders inside `<head>`, so it cannot
  grow into body chrome the way a raw string would), it needs **no new export code** (the export
  renders through the Consumer's own loaders, so a shadowed copy lands in the exported HTML, and a
  third-party snippet already carries the absolute URLs the no-rewrite export needs), and it keeps the
  no-external-host guard honest — mdjango ships the component **empty**, `test_theme.py` scans it like
  any shipped template, and `test_the_head_slot_ships_empty` pins the emptiness so an "example"
  `<script>` can never sneak a real tag (or an external fetch) into every Consumer's head. This is a
  narrow, deliberate carve-out from the "settings + seven seeds, shadowing unadvertised" stance: the
  Head slot is now the *one* advertised template seam; all other shadowing stays unadvertised, and a
  project needing different *chrome* has still outgrown mdjango.
- **The reset must not out-specify the component rules.** `.docs-body a { color: … }` is (0,1,1)
  and silently beat every single-class rule that colours a link (`.docs-nav-link`,
  `.docs-toc-link`, `.docs-header-link`), rendering the whole sidebar and TOC at full
  `--foreground` while their intended stop sat there dead. `@layer base` did **not** save it —
  Tailwind flattened the at-rule away, so the sheet had no layers and source order could not settle
  a specificity tie. The reset is now `.docs-body :where(a)`, which drops it to (0,1,0). With
  Tailwind since removed (ADR 0005) the sheet is deliberately flat and unlayered and the reset is
  concatenated first, so `:where()` remains the mechanism — a specificity win there would be
  permanent. Any future element-level reset needs the same treatment.
- **The default face ships with the package.** `--font` is a seed a consumer may override, but the
  *default* cannot depend on a network: IBM Plex Mono is vendored as `woff2` and declared with
  `@font-face`, not linked from Google Fonts. While it was CDN-linked, a blocked or slow request
  (strict CSP, offline reader, an export opened from disk) silently fell back to the platform mono
  — SF Mono on macOS, Noto Sans Mono on Linux — changing the letterforms and the metrics by about
  5% while the page still looked fine. A font that only sometimes arrives is not a house style.
- **The prose fills the column out to the TOC rail, capped at 57rem.** Matching the design means
  a deliberate departure from the usual 45–75 character advice: the line runs to about 100
  characters at the widest bound. The mono face plus the 1.7 line-height carry that better than a
  proportional face would.

  The cap earns its place on pages with **no** TOC. `57rem` is exactly the article's width when
  the rail *is* present and the shell is at its `103rem` maximum, so a page with a rail is
  unaffected while a page without one matches it rather than running to ~128 characters. It is a
  **cap, not a reserved column**: the rail's column is dropped when there is no rail, so on a
  narrow window the prose uses that space and shrinks with the viewport instead of being held off
  the edge by a phantom gutter. Reserving the column was tried first and rejected for exactly that
  — it kept ~220px from the text at every width, including the ones that needed it.

  The equality between the cap and the grid is arithmetic, so widening the sidebar or the rail
  invalidates it silently; `test_theme.py` recomputes it from the real column values.
- **The type scale is eight steps, deliberately fewer than the design's ten.** Sizes are exact
  4-decimal fractions of `--font-size` — 2 decimals is not enough (`0.78rem` is 10.92px, missing
  the 11px step). The design carried 12.5px, 13px and 13.5px steps; all three are collapsed into
  **13px**, because a half-pixel distinction is invisible to a reader but forces every new rule to
  choose between three indistinguishable tokens. 11px and 11.5px remain a similar near-pair, kept
  only because a single rule (`.search-foot`) uses the latter; collapse it too if a second one
  ever wants it.
- **The mocks' `rem`s are not our `rem`s.** The mocks are Tailwind, whose spacing utilities
  (`gap-7`, `pt-12`, `mt-16`) are `rem` values resolved against the browser's **16px** root, while
  this theme sets `html { font-size: var(--font-size) }` = **14px**. Copying such a number across
  verbatim silently shrinks it to 87.5% — `gap-7` (28px) became `gap: 1.75rem` (24.5px) and the
  whole shell read as slightly too tight while every *type* size still measured correctly. Convert
  a mock value by its **rendered pixels** (`× 16/14`), never by its digits: `gap-7` → `2rem`.

## Alternatives considered

- **Neutral themeable base + a walden "skin" on top** — rejected. Reintroduces the theme-assembly
  burden mdjango removes; the baked house style *is* the value.
- **A single `--chroma`/`--warmth` multiplier instead of two extra seeds** — rejected. One knob
  rather than two, but it needs relative colour syntax (`oklch(from …)`) in a package that vendors
  everything precisely to avoid assuming a consumer's browser, it cannot reproduce the design's
  hue drift across the ramp, and "set a chroma multiplier" is a worse thing to ask of a consumer
  than "set your hairline colour".
- **Expose the full palette as overrides** — rejected. Lets consumers break the contrast ladder;
  contradicts "opinionated".
- **Consumer supplies all chrome; mdjango renders only the article** — rejected as the default;
  pushes header/search/theme wiring onto every consumer. Kept as the **escape hatch** (template
  override), which is what makes decision 3 a hybrid rather than a lock-in.
- **`@tailwindcss/typography` for prose** — rejected. Its `--tw-prose-*` colour indirection would
  have to be remapped to our tokens on every stop; bespoke CSS binds to them directly and ships
  leaner.

---

Note: the text and config shown in the design mocks (`walden.toml`, `curl … | sh`, a single
binary) is **fiction** — illustrative filler. Real walden content is authored by the `site`
project; mdjango renders whatever markdown it is handed.
