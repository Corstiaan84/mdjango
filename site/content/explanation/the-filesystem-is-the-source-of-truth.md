---
title: The filesystem is the source of truth
weight: 10
description: What you operate when you run mdjango, and what it assumes about the markdown you point it at.
---

# The filesystem is the source of truth

mdjango has no models, no migrations and no admin. Every URL it serves comes from a file in the
Content tree, and nothing else. This page explains what that means for the project that hosts it.

## What you operate

Nothing beyond the Django process you already run. There is no table to migrate, no import command
to schedule, no editing interface to back. The whole tree is parsed once into an in-memory registry
(Sections, Pages by path, a flattened order for prev/next) on the first request after a process
starts, and reused for the life of that worker. Under `DEBUG` the parse happens on every request
instead, so an edit shows up on reload.

The corollary is that the registry is per process. Four gunicorn workers hold four copies, each
built on that worker's first request. They agree because they read the same files, not because they
share state.

`git` is the editing workflow and the audit log. A change to the docs is a commit, a rollback is a
revert, a review is a diff. A content change reaches production the way a code change does: deploy
and restart. There is no file watcher, because the content only changes when the code does.

## What it assumes about your content

The article body is emitted without sanitisation, and markdown inside raw HTML is processed. That is
correct for content your team authors and reviews in the same pull requests as the code. It is
wrong for anything else. mdjango is not a wiki engine. Pointing `MDJANGO_CONTENT_DIR` at
user-writable storage would let anyone who can write a file there run script in your readers'
browsers.

The same assumption is what lets rendered pages be cached and served as identical bytes to every
visitor: a docs page depends on the tree and the settings, never on who is asking. See
[How caching works](../how-caching-works/).

## One pipeline, two outputs

The runtime views and the static export build the same template context and render the same
templates. The export is the runtime output written to disk. There is no second renderer to drift,
which is why `mdjango_build --check` is a faithful test of what the live site will do, and why the
export is a cheap secondary for a docs-only host rather than a separate product.

## What this rules out

A CMS-style editing surface for non-technical authors, a database-backed content model with an
import step, and a static-site generator with Django as a thin wrapper were all considered and set
aside. The first two add a second copy of the truth for data already well represented as files. The
third gives up the reason to use Django at all: the docs living inside a process that also serves
authenticated users, other apps and shared middleware.
