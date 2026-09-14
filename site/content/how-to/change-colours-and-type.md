---
title: Change the colours and type
weight: 40
description: Point MDJANGO_EXTRA_CSS at a stylesheet that sets the seven CSS seeds, light and dark.
---

# Change the colours and type

**Goal:** give the docs your palette, typeface and base size without touching the layout.

**You need:** a static directory your project serves. The token names and shipped defaults are in
the [theme tokens reference](../../reference/theme-tokens/).

## 1. Point mdjango at your stylesheet

Set `MDJANGO_EXTRA_CSS` in your Django settings to a static path — a string, or a list for several.
mdjango loads each one with a `<link>` after its own sheet, so your rules win without touching any
template:

```python
# settings.py
MDJANGO_EXTRA_CSS = "acme/docs-theme.css"
```

Each value is a `{% static %}` name, resolved through your static files the same way mdjango's own
sheet is, so place the file under a static directory your project serves (e.g.
`acme/static/acme/docs-theme.css`). External/CDN URLs are not supported here — the file must be on a
static path. mdjango's sheet is one flat file with no `@layer`, so a later rule of equal specificity
wins.

## 2. Set the seeds

Create the file you named (`acme/docs-theme.css`) and set your seeds:

```css
:root {
  /* surface ramp: page ground -> hairline */
  --background: #ffffff;
  --border: #e2e6ec;

  /* text ramp: full emphasis -> lowest emphasis */
  --foreground: #14181f;
  --foreground-subtle: #7b8494;

  --accent: #2f6df6;                        /* article links; omit to stay monochrome */
  --font: "Inter", system-ui, sans-serif;   /* body and chrome; code stays monospace */
  --font-size: 15px;                        /* every other size is a fraction of this */
}
```

These are the seven Seed values. Set any subset. The three stops between the ends of each Ramp
(`--surface`, `--foreground-body`, `--foreground-muted`) are Derived values, recomputed from your
ends and locked. Setting them directly is not supported.

The values above are an example, not the shipped defaults. The defaults are the warm palette and
IBM Plex Mono at `14px`.

## 3. Set the dark values twice

Dark mode is applied by two rules of equal specificity: one for a reader who pressed the toggle,
one for a reader whose system is dark and who never touched it. Override both, or the two groups
see different palettes.

```css
:root[data-theme="dark"] {
  --background: #0f1216;
  --border: #262c35;
  --foreground: #e8ebf0;
  --foreground-subtle: #7e8794;
}

@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --background: #0f1216;
    --border: #262c35;
    --foreground: #e8ebf0;
    --foreground-subtle: #7e8794;
  }
}
```

The toggle stores its choice in `localStorage` under `mdjango-theme`. Clear that key to return to
following the system.

## 4. Check both themes

Reload a page, press the theme toggle, and read a paragraph, a muted nav label and a hairline in
each mode. The interior stops carry whatever chroma your ends carry, so a warm or tinted palette
survives, but nothing checks contrast for you. A `--border` very close to `--background` gives faint
hairlines and a faint `--surface`. A `--foreground-subtle` close to `--background` makes muted text
unreadable.

## Use the font on your own pages

The `@font-face` rules for IBM Plex Mono ship separately for templates mdjango does not render:

```django
<link rel="stylesheet" href="{% static 'mdjango/fonts.css' %}">
```

## If you also export a static site

`mdjango_build` resolves each `MDJANGO_EXTRA_CSS` name through the staticfiles finders and copies
the file into the export, so a themed build is self-contained — no extra step. If a name can't be
resolved the build prints a warning and leaves it out; check the file is on a static path the
finders search (an app's `static/` directory or a `STATICFILES_DIRS` entry). See
[Export a static site](../export-a-static-site/).
