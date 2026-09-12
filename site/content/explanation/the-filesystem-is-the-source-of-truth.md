---
title: The filesystem is the source of truth
weight: 10
description: Why there is no database, no admin and no sanitiser, and what that assumes about your content.
---

# The filesystem is the source of truth

mdjango has no models, no migrations and no admin. Every URL it serves comes from a file in the
Content tree, and nothing else. This page explains why, and what the choice asks of you.

## Docs are trusted, finite and already files

Documentation for a project is written by the people who ship the project, reviewed in the same
pull requests as the code, and committed to the same repository. It is not user-submitted. That
removes the usual reasons to put content behind a database: there is no editing UI to back, no
per-request permission check, and no untrusted input to sanitise.

It is also small enough to hold in memory. The whole tree is parsed once into a registry —
sections, pages by path, a flattened order for prev/next — on the first request, and reused for
the life of the worker process. Under `DEBUG` the parse happens on every request instead, so an
edit shows up on reload without a restart. Either way there is no import step and no sync problem:
the file *is* the page.

`git` becomes the editing workflow and the audit log. A change to the docs is a commit; a rollback
is a revert; a review is a diff.

## One pipeline, two outputs

The same registry feeds a running Django site and the static export. Both build the same template
context and render the same templates; the export is the runtime output written to disk. There is
no second renderer to drift, which is why `mdjango_build --check` is a faithful test of what the
live site will do.

## What this assumes about your content

The article body is emitted unsanitised. Raw HTML in a page reaches the browser as written. That is
correct for content your team authors and reviews, and wrong for anything else: mdjango is not a
wiki engine, and pointing `MDJANGO_CONTENT_DIR` at user-writable storage would be a mistake.

The registry is per process and read-only after it is built. In production, a content change is a
deploy — restart the workers. There is no file watcher, because the content only changes when the
code does.

## What was rejected

- **Database-backed content with an import command** — adds migrations, an import step and a
  second copy of the truth, to model data already well represented as files.
- **A static-site generator with Django as a thin wrapper** — the project wants Django as the base
  so runtime features stay reachable; static output is an artifact, not the framework.
- **Separate renderers for runtime and export** — two code paths guarantee drift.

A CMS-style editing surface for non-technical authors is out of scope until a real need appears.
