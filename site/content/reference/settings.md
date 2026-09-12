---
title: Settings
weight: 10
description: Every MDJANGO_* Django setting, its type, default and effect.
---

# Settings

All configuration is ordinary Django settings, read on each request through `mdjango.conf.get_conf()`.
`MDJANGO_CONTENT_DIR` is required; everything else has a default. None of these affect the theme's
colours or type — those are CSS ([theme tokens](../theme-tokens/)).

## Content

| Setting | Type | Default | Effect |
|---|---|---|---|
| `MDJANGO_CONTENT_DIR` | `str` or `Path` | — (required) | Root of the Content tree. Missing or falsy raises `ImproperlyConfigured`; a path that is not a directory raises `ContentError` on first use. |
| `MDJANGO_INCLUDE_DRAFTS` | `bool` | `DEBUG` | Include pages marked `draft: true` in the registry, and so in navigation, search, LLM artifacts and the export. |
| `MDJANGO_ALWAYS_REBUILD` | `bool` | `DEBUG` | Re-read the Content tree and rebuild the search index and LLM artifacts on every request. Also disables response caching. |

## Shell

| Setting | Type | Default | Effect |
|---|---|---|---|
| `MDJANGO_BRAND` | `str` | `"docs"` | Wordmark text in the header. Fallback for `<title>`. |
| `MDJANGO_SITE_TITLE` | `str` | `""` | `<title>` and the heading of `llms.txt` / `llms-full.txt`. Falls back to `MDJANGO_BRAND`. |
| `MDJANGO_HOME_URL` | `str` | `"/"` | Target of the wordmark link. |
| `MDJANGO_VERSION` | `str` | `""` | Display string rendered as a chip in the header. Hidden when empty. Not used for routing. |
| `MDJANGO_GITHUB_URL` | `str` | `""` | Renders a header link labelled `github`. Hidden when empty. |
| `MDJANGO_HEADER_LINKS` | iterable of `{"label": str, "url": str}` dicts or `mdjango.conf.HeaderLink` | `()` | Extra header links, in order, between the `llms.txt` links and the GitHub link. |

## LLM artifacts

| Setting | Type | Default | Effect |
|---|---|---|---|
| `MDJANGO_LLM_DOCS` | `bool` | `True` | Master switch for `llms.txt`, `llms-full.txt`, `index.md` and per-page `.md` routes, the header and drawer links, the `<link rel="alternate">`, and the export of those files. `False` returns 404 from all four routes. Search is unaffected. |
| `MDJANGO_DESCRIPTION` | `str` | `""` | One-line summary rendered as a `>` blockquote under the title in `llms.txt` and `llms-full.txt`. |

## Caching

| Setting | Type | Default | Effect |
|---|---|---|---|
| `MDJANGO_CACHE_SECONDS` | `int` | `300` | TTL of the server-side page cache (Django's default cache backend, key `mdjango:page:<path>`) and the value of `Cache-Control: public, max-age=`. `0` disables the page cache and sets `Cache-Control: no-cache`. Ignored while `MDJANGO_ALWAYS_REBUILD` is true. An `ETag` is always emitted. |

## Not settings

- `INSTALLED_APPS` must contain `"django_cotton"` and `"mdjango"`; `"django.contrib.staticfiles"`
  is needed to serve the shell's assets.
- There is no setting for the maximum tree depth (fixed at three), for disabling search, or for
  adding a stylesheet. See [Replace part of the shell](../../how-to/replace-the-shell/).
