---
title: Add analytics and other <head> tags
weight: 50
description: Shadow the head slot to inject a tracking script, a verification tag, or a preconnect — the one supported template override.
---

# Add analytics and other `<head>` tags

**Goal:** get a tracking script, a site-verification tag or a preconnect into every page's `<head>`
without changing anything else about the shell.

**You need:** a `templates/` directory your Django project loads ahead of mdjango. This is the one
template mdjango invites you to override; the rest of the [templates reference](../../reference/templates/)
is a closed surface. Colours and type do **not** go here — they load through a setting, covered in
[Change the colours and type](../change-colours-and-type/).

## 1. Shadow the head slot

mdjango renders an empty component, `cotton/docs/head_extra.html`, at the end of every page's
`<head>`. Override it by creating a file at the same path inside a templates directory your project
loads before mdjango:

```text
your_project/
  templates/
    cotton/
      docs/
        head_extra.html   # your version wins over mdjango's empty one
```

For Django to find yours first, that directory must be ahead of mdjango on the loader path — either
an entry in `TEMPLATES[0]["DIRS"]` (searched before any app), or an app listed before `mdjango` in
`INSTALLED_APPS` with `APP_DIRS` on.

## 2. Put your tags in it

Whatever you write renders verbatim inside `<head>`. A privacy-friendly analytics one-liner:

```django
<script defer data-domain="docs.example.com" src="https://plausible.io/js/script.js"></script>
```

Google Analytics 4 is two tags — an external loader and an inline bootstrap; both go in the slot
together:

```django
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag() { dataLayer.push(arguments); }
  gtag("js", new Date());
  gtag("config", "G-XXXXXXX");
</script>
```

The slot is not only for analytics. A verification `<meta>` or a `preconnect` works the same way:

```django
<meta name="google-site-verification" content="…">
<link rel="preconnect" href="https://plausible.io">
```

## 3. Keep CSS in the setting, not the slot

The two override channels do not overlap — use one each:

- **Colours, type, the seven CSS seeds** → `MDJANGO_EXTRA_CSS`, a setting (see
  [Change the colours and type](../change-colours-and-type/)).
- **Scripts and `<head>` tags** → the head slot.

`head_extra.html` is the *only* template mdjango supports overriding. Shadowing any other component —
the header, the base document, the page — is unsupported: a project that needs different chrome (a
logo, a footer, a different layout) has outgrown mdjango.

## 4. The export picks it up too

If you [export a static site](../export-a-static-site/), `mdjango_build` renders through your
project's own template loaders, so your `head_extra.html` lands in every exported page with no extra
step. One constraint: the export does not rewrite URLs, so tags in the slot must use **absolute**
URLs — as third-party snippets already do. A relative `src` would resolve against the page's own deep
path and 404.

## What the slot cannot do for you

- **A third-party script runs only where its host is reachable.** Opened from disk (a `file://`
  export with no server) or under a Content-Security-Policy that blocks the host, it silently does
  nothing and the page still renders. This is the trade-off for a tag mdjango does not ship — the
  external dependency is yours to accept. If your site sets a strict CSP, add the analytics host to
  it, the way the [production guide](../run-in-production/) notes you must already allow mdjango's own
  inline theme script.
- **The slot is head-only.** It cannot add a footer, change the header, or alter the layout. That is
  by design: it renders inside `<head>`, so it reaches nothing else.
