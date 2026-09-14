# Theme gallery

Example consumer palettes for mdjango, each driving the [`MDJANGO_EXTRA_CSS`](../adr/0003-opinionated-self-shelled-theme.md)
seed-override hook. Kept as a reference set — candidate illustrations for the theming docs, and a
visual regression eye-check for the seed contract. **Dev-only:** this tree is outside the wheel
(only `mdjango/` ships), so nothing here is distributed.

## What's here

- `css/` — six themes, each setting a `--font` so all six render in a **different** typeface (the
  point: every theme is visibly distinct, and the seed contract is exercised past colour alone).
  Colours are set for light and both dark selectors; `--font`/`--font-size` sit in the base `:root`
  (typography does not change by theme). `--code-font` is **not** a seed, so code blocks stay in
  IBM Plex Mono in every theme.
- `screenshots/` — each theme light + dark on the `reference/theme-tokens` page (retina, 2×), plus
  two contact sheets (`palettes-contact-sheet.png`, `brands-contact-sheet.png`).

The `--font`s are **system stacks**, not vendored web fonts — mdjango ships only IBM Plex Mono and
forbids CDN fetches (ADR 0003), so a named web font would silently fall back. The committed
screenshots were rendered on Linux, which has none of the real brand faces, so each stack names an
installed family as a fallback to stay visibly distinct here rather than collapsing to one default.
The **rendered** face below was verified with `CSS.getPlatformFontsForNode` — all six differ:

| Theme | Accent | Intended face | Rendered here (Linux) | Genre |
|---|---|---|---|---|
| `ocean` | blue | (system sans) | Noto Sans | humanist sans |
| `claret` | crimson | (system serif) | Noto Serif | serif |
| `forest` | green | (system serif) | Liberation Serif | old-style serif (Times) |
| `apple` | blue | SF Pro Text | Adwaita Sans | Inter-like sans |
| `tesla` | red | Helvetica Neue | Liberation Sans | Helvetica sans |
| `stripe` | indigo | Segoe UI / Sohne | Cantarell | geometric sans |

A viewer who has the intended face sees that instead; the fallbacks only make the *demo* legible.
With only these families installed the split is 4 sans + 2 serif, so `claret` and `forest` share the
serif genre (different families — a modern serif vs Times); every other pair differs in genre too.

## How they were generated

For each theme, a self-contained dist was built with the theme loaded through the real setting, then
screenshotted with Playwright over the served dist (the export uses root-relative `/static/` URLs):

```python
# throwaway settings: the site config + one palette via MDJANGO_EXTRA_CSS
from config.settings import *          # noqa
STATICFILES_DIRS = [".../palette_static"]
MDJANGO_EXTRA_CSS = "palettes/ocean.css"
```

```bash
python manage.py mdjango_build dist-ocean   # palette lands in dist/static/palettes/ocean.css
```

## A note on the brand-flavoured themes

`apple`, `tesla` and `stripe` are **aesthetic homages** — palettes evoking a look, with no logos,
wordmarks, or claim of affiliation or endorsement. If any of these are ever used in **published**
docs, rename them to the aesthetic (e.g. Graphite / Ember / Indigo) and keep brand logos and
wordmarks out; a brand name on a UI theme in public can imply endorsement.
