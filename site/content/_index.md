---
title: mdjango
description: A drop-in Django app that renders a tree of markdown into a documentation site.
---

# mdjango

mdjango is a Django app you add to a project that already does other things. You install it, point
it at a directory of markdown files, the **Content tree**, and include its URLs under a prefix. Your
running Django process then serves a documentation site at that prefix: header, section navigation,
article, table of contents, prev/next links, full-text search, dark mode, and the `llms.txt` family
of machine-readable artifacts. The docs sit behind the same middleware, authentication and
deployment as the rest of the project.

There is one fixed **House style**. You set the ends of two colour Ramps, an accent, a font and a
base size. The layout and the rest of the palette are derived and locked.

This site is mdjango documenting itself: a Django project that mounts mdjango with no overrides, so
what you are looking at is the default. Every page has a `.md` alternate, linked from the header.

## Read in this order

1. [Install and mount](getting-started/install-and-mount/) takes an existing project to a rendered
   page.
2. [Write a page](how-to/write-a-page/) and [Structure a content tree](how-to/structure-a-content-tree/)
   cover authoring.
3. [Brand the header](how-to/brand-the-header/) and [Change the colours and type](how-to/change-colours-and-type/)
   make it yours.
4. [Run in production](how-to/run-in-production/) before you deploy. Caching and draft visibility
   change when `DEBUG` is off.

The [reference](reference/settings/) section lists every setting, route, front-matter key and CSS
token. The [explanation](explanation/the-filesystem-is-the-source-of-truth/) section covers the
design choices you will meet when operating it.

If all you need is the docs and nothing else from Django, [Export a static site](how-to/export-a-static-site/)
writes the same site to a directory.
