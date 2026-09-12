---
title: Why three levels
weight: 30
description: The content tree stops at Section, Subsection, Page — a legibility contract, not a parser limit.
---

# Why three levels

A Content tree may nest three deep: Section, Subsection, Page. A fourth directory level is a build
error. This page explains what the cap buys and why it is a hard error rather than a setting.

## The cap is a promise about the sidebar

The walker could recurse to any depth; the limit was never about parsing. It is a contract between
the content and the Shell: the navigation can show the whole tree legibly, and an author who
exceeds what it can show is **told at build time**, not left with a site that quietly degrades at
depth five.

Originally the cap was two — Section and Page. It moved to three when a real Section reached
fifteen pages held in order by nothing but a hand-maintained weight sequence, with no way to say
that several of them were one family. The number changed; the build-time-error property did not.

## Subsections are labels, not destinations

A Subsection groups Pages and nothing more. It has no URL; its `_index.md` supplies only a title
and a weight. Every URL is still a Page, and every Page is still a file. Making groups addressable
would open a new URL class and a new collision (`cli.md` and `cli/` in one Section both wanting
`…/cli/`), so that remains an open question rather than a hidden feature. If a group needs an
overview, write an ordinary Page inside it.

## Interleaving by weight

A Subsection sorts among its Section's own pages by the same `(weight, title)` key, so a group can
sit in the middle of a curated sequence. The same rule lets a loose page at the root sit between
Sections. The navigation keeps its top level uniform by coalescing a run of loose pages into one
untitled group.

`llms.txt` cannot follow the interleaving exactly: markdown headings are sequential, and once a
`###` opens there is no way back to Section level without repeating the heading. So inside a
Section it lists the Section's own pages first, then each Subsection. `llms-full.txt` and the
navigation keep the true order.

## Collapsing, and why open state is not remembered

Subsections render as native `<details>` elements, open only for the group containing the current
page. Sections never collapse: they are the site's map. The open state is computed on the server
from the current page alone, because rendered pages are cached and served identically to every
visitor — per-visitor state cannot exist in that HTML. Remembering it in `localStorage` was
rejected: with full page loads on every navigation it would flash the wrong state on each click.

## Why not a setting

`MDJANGO_MAX_DEPTH` was considered and rejected. It would make the navigation's legibility a
function of consumer configuration and hand consumers a knob that produces a broken-looking site.
The Theme's stance is that you cannot configure your way into a bad result; the depth cap is part
of that.

## What the cap costs you

Moving a Page into a Subsection changes its URL, and there is no redirect table. Every relative
link aimed at it shifts by one segment. Restructure in a single change and update the links in the
same commit.
