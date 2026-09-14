# Theme gallery

Example consumer palettes for mdjango, each driving the [`MDJANGO_EXTRA_CSS`](../adr/0003-opinionated-self-shelled-theme.md)
seed-override hook. Kept as a reference set — candidate illustrations for the theming docs, and a
visual regression eye-check for the seed contract. **Dev-only:** this tree is outside the wheel
(only `mdjango/` ships), so nothing here is distributed.

## What's here

- `css/` — six themes. The three colour palettes set only the five **colour** seeds (`--background`,
  `--border`, `--foreground`, `--foreground-subtle`, `--accent`), keeping the house mono. The three
  brand palettes also set `--font` (and some `--font-size`). Colours are set for light and both dark
  selectors; `--font`/`--font-size` sit in the base `:root` (typography does not change by theme).
- `screenshots/` — each theme light + dark on the `reference/theme-tokens` page (retina, 2×), plus
  two contact sheets (`palettes-contact-sheet.png`, `brands-contact-sheet.png`).

| Theme | Accent | Body font |
|---|---|---|
| `ocean` | blue | house mono (IBM Plex Mono) |
| `claret` | crimson | house mono |
| `forest` | green | house mono |
| `apple` | blue | SF-style sans stack — 15px |
| `tesla` | red | Helvetica-style sans stack — 14px |
| `stripe` | indigo | UI sans stack — 15px |

The brand `--font`s are **system stacks**, not vendored web fonts — mdjango ships only IBM Plex Mono
and forbids CDN fetches (ADR 0003), so a named web font would silently fall back. `--code-font` is
not a seed, so code blocks stay mono in every theme. The committed screenshots were rendered on
Linux, so the exact face is each stack's Linux fallback (Noto Sans / Liberation Sans / Adwaita Sans);
a viewer with the real face (SF, Helvetica, Segoe UI) sees that instead.

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
