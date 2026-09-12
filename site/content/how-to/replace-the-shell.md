---
title: Replace part of the shell
weight: 50
description: Shadow one of mdjango's cotton components — the header, the base document, or the whole page — from your own templates directory.
---

# Replace part of the shell

**Goal:** swap one piece of the Shell (the header, the base `<html>` document, the sidebar) for your
own markup while keeping the rest.

**You need:** a directory listed in your project's `TEMPLATES[0]["DIRS"]`. Every component and the
context it reads is listed in the [templates reference](../../reference/templates/).

## How shadowing works

The Shell is assembled from cotton components under `mdjango/templates/cotton/docs/`. cotton
resolves a component by template name, and mdjango leaves cotton's default component directory in
place, so a file at the same path in your project's templates directory is found first:

```text
your-project/
  templates/
    cotton/
      docs/
        header.html      # replaces <c-docs.header />
```

Template resolution order is `TEMPLATES["DIRS"]` before app directories. Nothing else to register.

## Replace the header

Copy `mdjango/templates/cotton/docs/header.html` to `templates/cotton/docs/header.html` and edit
it. The component receives two attributes from the page template — `conf` (the resolved settings)
and `breadcrumb` (a list of `{label, url}` crumbs) — and can use anything in the outer page
context.

A minimal header that keeps search and the theme toggle working:

```django
<header class="docs-header">
  <div class="docs-header-inner">
    <button class="docs-hamburger" type="button" data-action="disclosure#toggle" aria-label="Open navigation">≡</button>
    <a href="{{ conf.home_url }}" class="docs-wordmark">
      <img src="{% static 'acme/logo.svg' %}" alt="{{ conf.brand }}" height="20">
    </a>
    <div class="docs-header-spacer"></div>
    <button class="docs-search-trigger" type="button" data-action="search#open">search docs</button>
    <button class="docs-theme-toggle" type="button" data-action="theme#toggle" aria-label="Toggle dark mode">◐</button>
  </div>
</header>
```

Add `{% load static %}` at the top if you use `{% static %}`. The `data-action` attributes are
what wire the buttons to the shipped Stimulus controllers; the class names are what the shipped
stylesheet styles. Drop a class and you restyle that element yourself.

## Replace the base document

Shadow `templates/cotton/docs/base.html` to change `<head>` — add a stylesheet, analytics, meta
tags. The component receives `title` and `page_md_url` and renders the page body in `{{ slot }}`.
Whatever else you change, keep these or the corresponding feature stops working:

| Keep | Provides |
|---|---|
| `<link rel="stylesheet" href="{% static 'mdjango/mdjango.css' %}">` | the entire house style |
| the inline `mdjango-theme` script in `<head>` | dark mode without a flash on load |
| the `<script type="importmap">` | resolves `@hotwired/stimulus` and `minisearch` to the vendored files |
| `data-controller="theme search disclosure"` on `<body>` | theme toggle, search palette, mobile drawer |
| `<script type="module" src="{% static 'mdjango/application.js' %}">` | boots the controllers |
| `{{ slot }}` | the page |

## Replace the whole page

Shadow `templates/mdjango/page.html` to change the layout itself — drop the table of contents,
reorder the columns, add a footer. This is the only entry template; it composes the components with
the context listed in the [templates reference](../../reference/templates/). Anything you leave out
of it is simply not rendered.

## Know what you are taking on

Shadowing copies mdjango's markup into your project. The **settings** and the **seven CSS seeds**
are versioned contracts; the components' markup, class names and context keys are not. When you
upgrade mdjango, diff your copies against the shipped templates.

The sidebar reads `conf` and `home` from the page context, not from attributes — a shadowed
`page.html` that renders `<c-docs.sidebar />` outside that context loses the Home link and the
mobile `llms.txt` group without an error.
