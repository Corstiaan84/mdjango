---
title: Why the house style is fixed
weight: 30
description: One Theme, seven knobs, no build step. The reasoning behind mdjango's Override surface and its limits.
---

# Why the house style is fixed

mdjango ships exactly one Theme. You can change its colours, its typeface and its size. You cannot
change its layout, its chrome or its personality. This is deliberate, and this page lays out the
trade.

## The drop-in promise

The point of mdjango is that installing it into a project gives that project a finished
documentation site. A neutral, fully themeable base would hand back the work it exists to remove:
choosing a type scale, tuning a palette, designing a sidebar. So the House style, flat, monochrome,
typographic, one layout, is fixed, and adopting mdjango means adopting it.

## Two ramps, set by their ends

What is open is the Override surface: the two ends of each colour Ramp, an accent, the font and the
base size. Seven CSS custom properties.

The interior stops of each Ramp (raised surfaces, body text, muted text) are Derived values,
computed from the ends and locked. That is what makes the surface safe: you cannot pick a body-text
colour that fails against your background, because you do not pick it. The ladder is computed from
the two colours you did pick.

The derivation mixes within a Ramp, never across the palette. An earlier model mixed text toward
the background, which averaged away the chroma of any tinted palette and shipped visibly greyer than
its design. Giving each Ramp its own two ends fixed that, and the exposed set grew from five tokens
to seven as a result.

Those seven names are a public API. Renaming or dropping one is a breaking change and is versioned
as one. The markup of the templates, their class names and their context keys are not part of that
promise, and mdjango may change them in any release.

## The shell is included, not extended

mdjango renders the whole page from your settings: header, navigation, article, table of contents,
prev/next. That is the product. There is no `{% block %}` to fill, no slot for extra chrome, no
plugin point for a footer or a logo. A block contract would freeze the markup into a public API and
take away the freedom to improve the Shell; a partial extension point would produce sites that are
half House style and half something else. A project that needs different chrome has outgrown
mdjango and should fork it.

Overriding the seeds is the exception, and it stays outside that markup: `MDJANGO_EXTRA_CSS` loads
your stylesheet after the Shell's own, so you re-colour and re-type the House style without touching
a template. [Change the colours and type](../../how-to/change-colours-and-type/) shows it.

## No build step, no CDN

Everything the Shell needs ships in the wheel: a precompiled stylesheet, vendored Stimulus and
MiniSearch, six `woff2` faces of the default font. A reusable app cannot assume the project has
Node, a bundler, network access at page load, or a permissive content-security policy. A font that
only sometimes arrives is not a House style.

For the same reason there are no utility classes. The package ships tokens and semantic classes,
and a Consumer's own pages can reuse the font through `fonts.css`.

## What you give up

- A different layout, a card-based or bordered restyle, an independent border hue, a logo in the
  header: not reachable. mdjango is the wrong tool if you need them.
- A proportional body face is reachable through `--font`. Code stays monospace.
- A configurable navigation depth: rejected, because it would let a project configure its way into
  a sidebar the Shell cannot render legibly. See [Why three levels](../why-three-levels/).
