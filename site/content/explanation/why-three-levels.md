---
title: Why three levels
weight: 20
description: The Content tree stops at Section, Subsection, Page. A legibility contract, not a parser limit.
---

# Why three levels

A Content tree may nest three deep: Section, Subsection, Page. A fourth directory level is an error.
This page explains what the cap buys and why it is a hard error rather than a setting.

## The cap is a promise about the sidebar

The walker could recurse to any depth. The limit was never about parsing. It is a contract between
the content and the Shell: the navigation can show the whole tree legibly, and an author who exceeds
what it can show is told when the tree is read, not left with a site that quietly degrades at depth
five.

The cap was originally two, Section and Page. It moved to three when a real Section grew long enough
that a flat, weight-ordered list could no longer say that several of its Pages were one family. The
number changed; the error-not-degradation property did not.

## Subsections are labels, not destinations

A Subsection groups Pages and nothing more. It has no URL. Its `_index.md` supplies only a title and
a weight. Every URL is still a Page, and every Page is still a file. Making groups addressable would
open a new URL class and a new collision (`cli.md` and `cli/` in one Section both wanting `…/cli/`),
so that remains an open question rather than a hidden feature. If a group needs an overview, write
an ordinary Page inside it.

## Interleaving by weight

A Subsection sorts among its Section's own Pages by the same `(weight, title)` key, so a group can
sit in the middle of a curated sequence. The same rule lets a Loose page at the root sit between
Sections. The navigation keeps its top level uniform by coalescing a run of Loose pages into one
untitled group.

`llms.txt` cannot follow the interleaving. Markdown headings are sequential, and once a `###` opens
there is no way back to Section level without repeating the heading. So inside a Section it lists
the Section's own Pages first, then each Subsection. `llms-full.txt` and the navigation keep the
true order.

## Collapsing, and why open state is not remembered

Subsections render as native `<details>` elements, open only for the group containing the current
page. Sections never collapse: they are the site's map. The open state is computed on the server
from the current page alone, because rendered pages are cached and served identically to every
visitor. Per-visitor state cannot exist in that HTML. Remembering it in `localStorage` was
rejected: with a full page load on every navigation it would flash the wrong state on each click.

## Why not a setting

A `MDJANGO_MAX_DEPTH` setting was considered and rejected. It would make the navigation's legibility
a function of Consumer configuration and hand you a knob whose other positions produce a
broken-looking site. The Theme's stance is that you cannot configure your way into a bad result. The
depth cap is part of that.

## What the cap costs you

Moving a Page into a Subsection changes its URL, and there is no redirect table. Every relative link
aimed at it shifts by one segment. Restructure in a single change and update the links in the same
commit. [Structure a content tree](../../how-to/structure-a-content-tree/) walks through the move.
