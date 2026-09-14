---
title: Theme tokens
weight: 50
description: The seven CSS seeds a Consumer may set, the three derived values that are locked, their shipped defaults, and the dark-mode selectors.
---

# Theme tokens

The Theme's palette is two colour Ramps. Each is defined by its two ends, which are Seed values a
Consumer sets. The stops between them are Derived values, computed with `color-mix()` in OKLab from
the ends of their own Ramp. All are CSS custom properties on `:root` in `mdjango.css`.

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
| `--accent` | article links only | `var(--foreground)` | `var(--foreground)` |
| `--font` | body and chrome typeface | `"IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace` | same |
| `--font-size` | root size; every other size is a fixed fraction of it | `14px` | same |

## Derived (locked)

| Token | Role | Light | Dark |
|---|---|---|---|
| `--surface` | raised surfaces: code blocks, inline code, search trigger, inline TOC | `color-mix(in oklab, var(--background) 59%, var(--border))` | same |
| `--foreground-body` | prose | `color-mix(in oklab, var(--foreground) 55%, var(--foreground-subtle))` | `48.6%` |
| `--foreground-muted` | nav links, TOC links, pager, blockquotes, table headers | `color-mix(in oklab, var(--foreground) 33%, var(--foreground-subtle))` | `19%` |

The dark theme restates the two text ratios because its ladder is compressed at the low-emphasis
end. Setting a derived token directly is not supported.

## Outside the contract

| Token | Value | Notes |
|---|---|---|
| `--code-font` | `"IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace` | Code, `kbd`, `pre` and `samp`. Declared on `:root` beside the seeds, so it can be set, but it is not one of the seven and its name is not versioned. |

There are no spacing or layout-width tokens. Shell width, column widths, header height and the
two breakpoints (`1023px` drops the TOC rail; `767px` drops the sidebar into a drawer) are literals
in the stylesheet. There is no `--highlight` token.

## Dark mode selectors

The dark values are applied by two rules of equal specificity:

```css
:root[data-theme="dark"] { … }                                  /* reader pressed the toggle */
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { … } }   /* system dark, no toggle */
```

The toggle sets `data-theme` on `<html>` and stores `"dark"` or `"light"` in `localStorage` under
`mdjango-theme`. An inline script in `<head>`, before the stylesheet, applies the stored value
before first paint. Once pressed there is no "follow the system" state until the key is cleared. A
Consumer's dark override must target both selectors.

## Type scale

Sizes are 4-decimal fractions of `--font-size`, giving 11 / 11.5 / 12 / 13 / 14 / 15 / 16 / 26 px at
the default, plus 10px for the nav caret and 18.2px for the mobile hamburger. Changing `--font-size`
scales chrome and prose together.

## Fonts

IBM Plex Mono is vendored: six `woff2` faces (400, 600 and 400 italic, each in latin and latin-ext
subsets, about 89KB) under `static/mdjango/fonts/`, licensed under the SIL Open Font License 1.1.
The `@font-face` rules are inside `mdjango.css` with paths relative to the stylesheet, so they work
from a static export on disk. `static/mdjango/fonts.css` carries the `@font-face` rules alone
(about 2KB) for pages mdjango does not render:

```django
<link rel="stylesheet" href="{% static 'mdjango/fonts.css' %}">
```

Nothing is loaded from a CDN. Stimulus and MiniSearch are vendored ESM files resolved through an
import map in the base component.
