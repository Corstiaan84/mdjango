---
title: Change the colours and type
weight: 40
description: Set the seven CSS seeds — two colour ramps, an accent, a font and a base size — and load them after mdjango's stylesheet.
---

# Change the colours and type

**Goal:** recolour the site and change its typeface without breaking the contrast ladder.

**You need:** a place to load a stylesheet after `mdjango.css` — see
[Load your overrides](#load-your-overrides) below, which currently means shadowing the base
template. The tokens and their defaults are listed in the [theme tokens reference](../../reference/theme-tokens/).

## What you can set

The palette is two colour **Ramps**, each defined by its two ends. You set the ends; the interior
stops are computed from them and locked.

```text
surface ramp:  --background ..... --surface ..... --border
text ramp:     --foreground ..... --foreground-body ..... --foreground-muted ..... --foreground-subtle
```

Seven **Seed values** make up the whole Override surface:

```css
:root {
  /* surface ramp: page ground -> hairline */
  --background: #ffffff;
  --border: #e2e6ec;
  /* text ramp: full emphasis -> lowest emphasis */
  --foreground: #14181f;
  --foreground-subtle: #7b8494;

  --accent: #2f6df6;                        /* article links; defaults to --foreground */
  --font: "Inter", system-ui, sans-serif;   /* body and chrome */
  --font-size: 15px;                        /* scales every size on the page */
}
```

`--surface`, `--foreground-body` and `--foreground-muted` are **Derived values**: setting them has
no lasting effect because they are recomputed from the ends of their own Ramp. Code always uses
`--code-font` (monospace) regardless of `--font`.

## Cover dark mode

The shipped dark palette is applied two ways: by `data-theme="dark"` on `<html>` when the reader
has toggled it, and by `prefers-color-scheme: dark` when they have not chosen. Override both, or a
system-dark reader keeps mdjango's dark seeds while a toggled reader gets yours:

```css
:root[data-theme="dark"] {
  --background: #0f1216;
  --border: #262c35;
  --foreground: #e6e9ee;
  --foreground-subtle: #6f7885;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --background: #0f1216;
    --border: #262c35;
    --foreground: #e6e9ee;
    --foreground-subtle: #6f7885;
  }
}
```

## Pick the ends deliberately

Because interior stops are mixed *within* a Ramp, they carry whatever chroma the ends have. A warm
or tinted palette survives; a very light `--border` produces faint hairlines *and* a faint
`--surface`; a `--foreground-subtle` too close to `--background` makes muted text unreadable, and
nothing will stop you. Check both themes after a change.

## Load your overrides

mdjango's base template loads `mdjango.css` and nothing else; there is no setting or slot for an
extra stylesheet. To load one today, shadow the base component and add a `<link>` after mdjango's:

```django
{# templates/cotton/docs/base.html — a copy of mdjango's, plus one line #}
<link rel="stylesheet" href="{% static 'mdjango/mdjango.css' %}">
<link rel="stylesheet" href="{% static 'acme/docs-theme.css' %}">
```

Copy the shipped `mdjango/templates/cotton/docs/base.html` into a directory listed in your
`TEMPLATES["DIRS"]` and change only that. [Replace part of the shell](../replace-the-shell/)
explains what the base must keep for search, the theme toggle and the drawer to work.

The seed names are a public contract: renaming or removing one is a breaking change and is
versioned as one. The markup you copy when shadowing the base is not.
