---
title: mdjango
description: A drop-in Django app that renders a tree of markdown into a documentation site.
---

# mdjango

mdjango is a reusable Django app. You install it into a Django project, point it at a directory of
markdown files — the **Content tree** — and include its URLs. It renders that tree as a complete
documentation site: header, section navigation, article, table of contents, prev/next, full-text
search, dark mode, and the `llms.txt` family of machine-readable artifacts. The same tree can be
served by your running Django process or exported as a static directory.

There is one fixed house style. You set a handful of colours, a font and a base size; the layout
and the rest of the palette are derived and locked.

This site is mdjango documenting itself: a Django project that mounts mdjango with no overrides, so
what you are looking at is the default. Every page here has a `.md` alternate — follow the
`llms.txt` link in the header.

## Start here

- [Install and mount](getting-started/install-and-mount/) — from `pip install` to a rendered page
  in one sitting.

## Do a task

- [Structure a content tree](how-to/structure-a-content-tree/) — sections, subsections, ordering,
  the landing page, drafts.
- [Write a page](how-to/write-a-page/) — frontmatter, headings, code, tables, links between pages.
- [Brand the header](how-to/brand-the-header/) — wordmark, version, links.
- [Change the colours and type](how-to/change-colours-and-type/) — the seven CSS seeds.
- [Replace part of the shell](how-to/replace-the-shell/) — shadow a template.
- [Tune caching](how-to/tune-caching/) — one setting, and when to turn it off.
- [Export a static site](how-to/export-a-static-site/) — `mdjango_build`.
- [Publish the LLM artifacts](how-to/publish-llm-artifacts/) — `llms.txt`, `llms-full.txt`, per-page
  markdown.
- [Run in production](how-to/run-in-production/) — what changes when `DEBUG` is off.

## Look something up

- [Settings](reference/settings/) · [Content tree rules](reference/content-tree/) ·
  [URLs](reference/urls/) · [`mdjango_build`](reference/mdjango-build/) ·
  [Theme tokens](reference/theme-tokens/) · [Templates](reference/templates/) ·
  [Markdown](reference/markdown/)

## Understand the design

- [The filesystem is the source of truth](explanation/the-filesystem-is-the-source-of-truth/)
- [Why the house style is fixed](explanation/why-the-house-style-is-fixed/)
- [Why three levels](explanation/why-three-levels/)
