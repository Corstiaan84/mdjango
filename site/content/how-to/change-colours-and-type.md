---
title: Change the colours and type
weight: 40
description: Load a stylesheet after mdjango's and set the seven CSS seeds, for light and for dark.
---

# Change the colours and type

**Goal:** give the docs your palette, typeface and base size without touching the layout.

**You need:** a directory listed in `TEMPLATES[0]["DIRS"]` and a static directory your project
serves. The token names and shipped defaults are in the [theme tokens reference](../../reference/theme-tokens/).

## 1. Load a stylesheet after mdjango's

mdjango's base component loads one stylesheet and offers no setting or slot for a second. Shadow
the component to add one.

Copy the shipped `mdjango/templates/cotton/docs/base.html` from your installed package to
`templates/cotton/docs/base.html` in a directory listed in `TEMPLATES[0]["DIRS"]`, and add one line
after the existing stylesheet link:

```django
<link rel="stylesheet" href="{% static 'mdjango/mdjango.css' %}">
<link rel="stylesheet" href="{% static 'acme/docs-theme.css' %}">
```

Change nothing else in the copy. Everything else in that file is load-bearing; the list of what it
must keep is in [Replace part of the shell](../replace-the-shell/).

## 2. Set the seeds

mdjango's stylesheet is one flat file with no `@layer`, so a later rule of equal specificity wins.
Create `acme/docs-theme.css` in your static files:

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

`mdjango_build` copies only mdjango's own static tree into the export. Your `acme/docs-theme.css`
is referenced by the exported HTML but not written. Copy it into the export's static directory
yourself after the build. See [Export a static site](../export-a-static-site/).
