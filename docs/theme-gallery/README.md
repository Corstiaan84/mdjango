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
- The **screenshots** (each theme light + dark on the `reference/theme-tokens` page, retina 2×) are
  now **published** in the docs site, as content-tree Assets under
  `site/content/explanation/theme-gallery/` (ADR 0008), where the gallery page embeds them. They
  moved out of this dev tree when the gallery went public; the two contact sheets were dropped.

Each `--font` names a real, recognisable OFL (open-source) typeface. The **rendered** face — body
*and* heading — was verified with `CSS.getPlatformFontsForNode`, so these are what the screenshots
actually show, not what the CSS merely asks for:

| Theme | Accent | Font (`--font`) | Genre |
|---|---|---|---|
| `ocean` | blue | IBM Plex Sans | humanist sans (pairs with the house Plex Mono) |
| `claret` | crimson | Playfair Display | high-contrast didone serif |
| `forest` | green | Roboto Slab | slab serif |
| `graphite` | blue | Inter | neutral geometric-humanist sans |
| `ember` | red | Montserrat | geometric sans |
| `indigo` | indigo | Space Grotesk | grotesque sans |

`--code-font` is not a seed, so code blocks stay IBM Plex Mono in every theme.

### Reproducing the screenshots

These faces are **not vendored** — mdjango ships only IBM Plex Mono and forbids CDN fetches
(ADR 0003), and this gallery is a demo, not shipped. To reproduce the screenshots you need the six
families installed on the render machine; without them each `--font` falls back to a generic
`sans-serif`/`serif`. They were installed here from the OFL sources in
[`google/fonts`](https://github.com/google/fonts):

```bash
# variable TTFs into a user font dir, then refresh the cache
mkdir -p ~/.local/share/fonts/gallery && cd ~/.local/share/fonts/gallery
# Inter, IBM Plex Sans, Playfair Display, Roboto Slab: variable defaults render at 400 as-is.
# Montserrat and Space Grotesk default to a Thin/Light instance and Chromium does not interpolate
# a locally-installed variable font's weight, so their static 400/700 were instanced instead:
#   python -m fontTools.varLib.instancer 'Montserrat[wght].ttf' wght=400 -o Montserrat-Regular.ttf --update-name-table
#   python -m fontTools.varLib.instancer 'Montserrat[wght].ttf' wght=700 -o Montserrat-Bold.ttf    --update-name-table
fc-cache -f ~/.local/share/fonts
```

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

## A note on the aesthetic themes

`graphite`, `ember` and `indigo` began as brand-flavoured drafts (Apple / Tesla / Stripe) — palettes
evoking a look, never logos, wordmarks, or a claim of affiliation. They were **renamed to the
aesthetic** before the gallery went into the published docs, because a brand name on a UI theme in
public can imply endorsement. Keep it that way: aesthetic names only, no logos or wordmarks.
