# 5. No Tailwind — a hand-written reset and a 40-line minifier

Status: Accepted
Date: 2026-09-10
Amends: ADR 0003 §4 (which rejected `@tailwindcss/typography` but kept Tailwind itself)

## Context

mdjango was built with Tailwind's standalone CLI compiling `theme/src/input.css` into the one
shipped stylesheet. ADR 0003 §4 had already rejected `@tailwindcss/typography`, so the prose was
bespoke; the rest of the sheet followed, and the question "why isn't this Tailwind?" was never
answered with numbers.

It is now. Measured against the templates as they stand:

- **Tailwind generated zero utilities.** Not "few" — none. The five utility rules in the output
  (`.static`, `.inline`, `.hidden`, `.block`, `.filter`) are Tailwind matching those *words* in
  `{% static %}`, a `hidden` attribute and a `display: inline` declaration. No template contains a
  utility class.
- What it did contribute was **preflight (4.7KB) plus 2,228 bytes of `--tw-*` custom properties**
  — 102 of them, on `*` and `::backdrop`, existing solely to feed the utility system nothing uses.

Of the 162 rules in the sheet, 53 target markup mdjango does not author (Python-Markdown's
`<p>`/`<h2>`/`<table>`, Pygments' token spans, the render pipeline's `.code-block`/`.copy-btn`) and
22 more are built by the search controller in a JS string. Utility classes cannot reach any of
them. The remaining 52 — the shell layout — *could* be utilities, but must not be: mdjango ships
**precompiled** CSS with no consumer build step, and ADR 0003 §3 deliberately lets a consumer
shadow `base.html` or the header. Tailwind emits only what it sees when *mdjango* builds, so a
consumer's shadowed template — never scanned — would need utilities that do not exist in the
shipped sheet. Semantic classes ship complete and stay reusable from a shadowed template.

Tailwind was also actively costing correctness. `@layer base` looked like it ordered the cascade,
but Tailwind flattens the at-rule away, so the layer offered no protection while appearing to:
that is why `.docs-body a` silently out-specified `.docs-nav-link` and rendered the whole sidebar
and TOC at full `--foreground`. The purge behaviour needed a seven-line warning comment in the
sheet, because custom CSS placed inside `@layer components`/`utilities` is deleted.

## Decision

Drop Tailwind.

1. **`theme/src/reset.css`** — the subset of preflight this sheet relies on, hand-written: 25
   rules against preflight's 41. Dropped: both `--tw-*` blocks, and the form-widget rules for
   elements a docs page never renders (progress, fieldset/legend, textarea, dialog, number
   spinners, search decorations, file-upload buttons, `-moz-focusring`/`-ui-invalid`).
2. **`theme/src/input.css` → `theme/src/house.css`.** "input.css" was a Tailwind-ism, and the
   build now names its three sources plainly: `fonts.css`, `reset.css`, `house.css`.
3. **No cascade layers.** `@layer base` is unwrapped. Without Tailwind it would become a *real*
   layer, which loses to every unlayered rule regardless of specificity — a different model again.
   One flat, source-ordered sheet is the one that needs no explanation.
4. **`theme/bundle.py`** — concatenate, remove comments, drop the blank lines that leaves. Nothing
   else: no trimming of indentation, no collapsing whitespace inside declarations, no merging or
   reordering rules, no shortening colours, nothing touching a quoted string. Every transformation
   is one a human could do by hand and check by eye.

   It is not a minifier and should not grow into one. The entire saving is the comments, which are
   **40% of the authored source** — deliberately, since they carry the reasoning for the ramps, the
   measure cap and the `<details>` gap — and the stylesheet is the only asset that blocks first
   paint: 8,224 → 3,603 bytes gzipped. Trimming indentation as well would save a further 100 bytes
   and cost the readable output anyone debugging in devtools actually reads, so it is not done.
5. **`theme/build.sh`** concatenates the three sources through it. `--watch` polls mtimes. There is
   no toolchain to fetch, so `.gitignore` no longer excludes a binary.

## Consequences

- **The output is smaller: 17,415 → 16,850 bytes, 4,079 → 3,603 gzipped.** Losing a real minifier
  costs less than the `--tw-*` blocks did.
- **The committed artifact is now checked against its sources.** A build step whose output is
  committed can fall out of step silently, and every other test here reads the *compiled* file — so
  they would all keep passing against a stale copy. `test_theme.py` rebuilds from `theme/src/` and
  compares, which is the only thing that catches a forgotten `./theme/build.sh`. Without that
  guard, not having a build step at all would have been the safer choice.
- **The build no longer downloads a 42MB platform binary from a GitHub release.** For a package
  that vendors its font and its JS precisely so it need not assume a consumer's network, fetching
  a build tool over the wire was the last contradiction of that rule.
- **Verified equivalent, not assumed.** Both stylesheets were injected into four real docs pages in
  Chromium and the computed styles of every element compared — 83,496 values. A reset matching
  preflight exactly produced **0 differences**. The shipped reset differs deliberately in two
  places and nowhere else: `border-color: var(--border)` instead of Tailwind's hardcoded `#e5e7eb`
  (observable only on borders whose width is `0` — no rule in the sheet sets a border-width without
  its own colour) and `html { font-family: var(--font) }` instead of a sans stack (affecting
  `<html>` and non-rendered `<head>` children).
- **Two tests were resting on the old minifier's behaviour**, which only surfaced when it changed:
  cssnano stripped the quotes from `[data-theme="dark"]` and merged `padding` + `padding-left` into
  a shorthand. Both assertions now normalise formatting before matching, so they test CSS rather
  than a tool's habits.
- If utility classes are ever wanted for a *consumer's* own pages, that is the consumer's
  toolchain, not mdjango's — the package ships tokens and semantic classes, both of which a
  Tailwind consumer can use from their own config.

## Alternatives considered

- **Keep Tailwind for preflight only** — rejected. It is the status quo, and it means the project
  reads as a Tailwind project, carries the purge and layer hazards, and downloads a build tool, all
  to obtain a reset that is 25 rules long.
- **Use Tailwind properly, converting the 52 shell rules to utilities** — rejected. They are the
  half a consumer is invited to shadow, and utilities cannot survive that (see Context).
- **Serve the sources as-is, with no build step at all** — rejected, but it was close. It removes
  the drift hazard entirely and needs no script. It costs **+4,621 bytes gzipped** (8,224 vs 3,603)
  on the only render-blocking asset, to ship comments no browser reads. With the drift guard in
  place the build step is cheap enough that the bytes win; without it, this option was better.
- **A real minifier as a dev dependency** (`csscompressor`, `lightningcss`) — rejected for now.
  The conservative script already produces a smaller sheet than Tailwind did; adding a dependency
  to shave bytes gzip mostly recovers is the wrong trade. Revisit if the sheet grows a lot.
