---
title: Why the house style is fixed
weight: 20
description: One theme, seven knobs, no build step — the reasoning behind mdjango's override surface and its limits.
---

# Why the house style is fixed

mdjango ships exactly one Theme. You can change its colours, its typeface and its size; you cannot
change its layout or its personality without forking templates. This is deliberate, and this page
lays out the trade.

## The drop-in promise

The point of mdjango is that installing it gives you a finished documentation site. A neutral,
fully themeable base would hand you back the work it exists to remove: choosing a type scale,
tuning a palette, designing a sidebar. So the **House style** — flat, monochrome, typographic, one
layout — is fixed, and adopting mdjango means adopting it.

## Two ramps, set by their ends

What *is* open is the **Override surface**: the two ends of each colour Ramp, an accent, the font
and the base size. Seven CSS custom properties.

The interior stops of each Ramp — raised surfaces, body text, muted text — are derived from the
ends and locked. That is what makes the surface safe: you cannot pick a body-text colour that fails
against your background, because you do not pick it. The ladder is computed from the two colours
you did pick.

The derivation mixes *within* a Ramp, never across the palette. An earlier model mixed text toward
the background, which averaged away the chroma of any tinted palette and shipped visibly greyer
than its design. Giving each Ramp its own two ends fixed that, and the exposed set grew from five
tokens to seven as a result. Those seven names are treated as a public API: renaming or dropping
one is a versioned breaking change.

## The shell is included, and overridable

mdjango renders the whole page — header, navigation, article, table of contents, prev/next — from
your settings. Most projects want exactly that. The escape hatch for the rest is template
shadowing: replace one cotton component, or the base document, or the page template. Nothing in the
package uses `{% block %}`, because a block contract would freeze the markup; shadowing a whole
component lets mdjango evolve its own templates while a project that wants different chrome owns a
copy.

## No build step, no CDN

Everything the shell needs ships in the wheel: a precompiled stylesheet, vendored Stimulus and
MiniSearch, six `woff2` faces of the default font. A reusable app cannot assume a consumer has
Node, a bundler, network access at page load, or a permissive content-security policy — and a
static export opened from disk has none of those. A font that only sometimes arrives is not a
house style.

For the same reason there are no utility classes: a stylesheet compiled in mdjango's repository
cannot contain utilities for markup you write in a shadowed template. The package ships tokens and
semantic classes, both of which your own toolchain can build on.

## What you give up

- A different layout, a card-based or bordered restyle, an independent border hue: not reachable
  through the seeds. Fork the templates and stylesheet.
- A proportional body face is reachable (`--font`); code stays monospace.
- A configurable navigation depth: rejected, because it would let a consumer configure their way
  into a sidebar the shell cannot render legibly.
