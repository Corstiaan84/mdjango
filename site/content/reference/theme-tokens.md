---
title: Theme tokens
weight: 50
description: The seven CSS seeds a consumer may set, the three derived values that are locked, and their shipped defaults.
---

# Theme tokens

The Theme's palette is two colour Ramps. Each is defined by its two ends, which are **Seed values**
a Consumer sets; the stops between them are **Derived values**, computed with `color-mix()` in
OKLab from the ends of their own Ramp. All are CSS custom properties on `:root`.

```text
surface ramp:  --background ..... --surface ..... --border
text ramp:     --foreground ..... --foreground-body ..... --foreground-muted ..... --foreground-subtle
```

## Seeds

The Override surface. These seven names are a versioned contract: renaming or removing one is a
breaking change.

| Token | Role | Light default | Dark default |
|---|---|---|---|
| `--background` | page ground; lightest surface | `#f7f3ea` | `#211c15` |
| `--border` | hairlines; darkest surface tone | `#e0d7c6` | `#3b3426` |
| `--foreground` | full-emphasis text | `#2b241c` | `#eae3d2` |
| `--foreground-subtle` | lowest-emphasis text | `#a2947f` | `#8a7f6b` |
| `--accent` | article links | `var(--foreground)` | `var(--foreground)` |
| `--font` | body and chrome typeface | `"IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace` | same |
| `--font-size` | root size; every other size is a fixed fraction of it | `14px` | same |

`--accent` defaulting to `--foreground` is what makes the shipped palette monochrome.

## Derived (locked)

| Token | Role | Light | Dark |
|---|---|---|---|
| `--surface` | raised surfaces | `color-mix(in oklab, var(--background) 59%, var(--border))` | same |
| `--foreground-body` | body text | `color-mix(in oklab, var(--foreground) 55%, var(--foreground-subtle))` | `48.6%` |
| `--foreground-muted` | secondary text | `color-mix(in oklab, var(--foreground) 33%, var(--foreground-subtle))` | `19%` |

The dark theme restates the two text ratios because its ladder is compressed at the low-emphasis
end. Setting a derived token directly is not supported; it is recomputed from its Ramp's ends.

## Fixed

| Token | Value | Notes |
|---|---|---|
| `--code-font` | `"IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace` | Code is always monospace, independent of `--font`. |

There is no `--highlight` token.

## Dark mode selectors

The dark values are applied by two rules of equal specificity:

```css
:root[data-theme="dark"] { … }                                  /* reader toggled dark */
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { … } }   /* system dark, no toggle */
```

The toggle stores its choice in `localStorage` under `mdjango-theme` (`"dark"` or `"light"`) and
an inline script in `<head>` sets `data-theme` before first paint. A Consumer's dark override must
target both selectors.

## Type scale

Sizes are 4-decimal fractions of `--font-size`, giving 11 / 11.5 / 12 / 13 / 14 / 15 / 16 / 26 px at
the default. Changing `--font-size` scales chrome and prose together.

## Fonts

IBM Plex Mono is vendored: six `woff2` faces (400, 600, 400 italic × latin, latin-ext) declared
with `@font-face` inside `mdjango.css`. `static/mdjango/fonts.css` carries the `@font-face` rules
alone (~2 KB) for use on pages mdjango does not render:

```django
<link rel="stylesheet" href="{% static 'mdjango/fonts.css' %}">
```

Nothing is loaded from a CDN.
