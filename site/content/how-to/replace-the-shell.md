---
title: Replace part of the shell
weight: 50
description: Shadow one of mdjango's cotton components, the base document, or the page template from your own templates directory.
---

# Replace part of the shell

**Goal:** swap one piece of the Shell (the header, the base `<html>` document, the sidebar, the
whole layout) for your own markup while keeping the rest.

**You need:** a directory listed in your project's `TEMPLATES[0]["DIRS"]`. Every component and the
context it reads is listed in the [templates reference](../../reference/templates/).

## How shadowing works

The Shell is assembled from cotton components under `mdjango/templates/cotton/docs/`, composed by
one page template at `mdjango/templates/mdjango/page.html`. A file at the same relative path in your
templates directory replaces the shipped one:

```text
your-project/
  templates/
    cotton/
      docs/
        header.html      # replaces <c-docs.header />
        base.html        # replaces <c-docs.base>
    mdjango/
      page.html          # replaces the whole layout
```

This works because `django_cotton` rewrites your `TEMPLATES` entry when Django starts. It removes
`APP_DIRS`, installs its own loader chain with the filesystem loader (your `DIRS`) ahead of the
app-directories loader (mdjango's files), and wraps both in Django's cached loader. There is nothing
to register.

Two consequences. If your project sets `OPTIONS["loaders"]` itself, cotton leaves it alone and you
must list `django_cotton.cotton_loader.Loader` first yourself. And because the cached loader is
always on, a shadowed template edited while the server runs appears only after Django's autoreload
restarts the process.

## Replace the header

Copy `mdjango/templates/cotton/docs/header.html` from the installed package to
`templates/cotton/docs/header.html` and edit it. The component receives two attributes, `conf`
(the resolved settings) and `breadcrumb` (a list of `{label, url}` crumbs). A complete, working
header with a logo is in [Brand the header](../brand-the-header/).

The `data-action` attributes wire the buttons to the shipped Stimulus controllers. The class names
pick up the shipped styles. Drop a class and you restyle that element yourself.

## Replace the base document

Shadow `templates/cotton/docs/base.html` to change `<head>`: add a stylesheet, analytics, meta tags,
a canonical link. The component receives `title` and `page_md_url` and renders the page in
`{{ slot }}`. Whatever you change, keep these or the named feature stops working, silently:

| Keep | Provides |
|---|---|
| `<title>{{ title }}</title>` | the document title |
| `<link rel="stylesheet" href="{% static 'mdjango/mdjango.css' %}">` | the entire House style |
| the inline `mdjango-theme` script, before the stylesheet | dark mode without a flash on load |
| the `<script type="importmap">`, before any module | resolves `@hotwired/stimulus` and `minisearch` to the vendored files |
| `data-controller="theme search disclosure"` on `<body>` | theme toggle, search palette, mobile drawer |
| `<script type="module" src="{% static 'mdjango/application.js' %}">` | boots the controllers |
| `{{ slot }}` | the page |

## Replace the whole page

Shadow `templates/mdjango/page.html` to change the layout itself: drop the table of contents,
reorder the columns, add a footer. Copy the shipped file as a starting point. It composes the
components with the context keys listed in the [templates reference](../../reference/templates/).
Anything you leave out is not rendered.

The sidebar component reads `conf` and `home` from the page context, not from attributes. A
shadowed page template that renders `<c-docs.sidebar />` outside that context loses the Home link
and the mobile `llms.txt` group without an error.

## Know what you are taking on

Shadowing copies mdjango's markup into your project. The settings and the seven CSS seeds are
versioned contracts. The components' markup, class names and context keys are not. When you upgrade
mdjango, diff your copies against the shipped templates.
