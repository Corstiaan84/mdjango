---
title: Settings
weight: 10
description: Every MDJANGO_* Django setting, its type, default, effect, and what happens when it is wrong.
---

# Settings

All configuration is ordinary Django settings. mdjango reads them on every request through
`mdjango.conf.get_conf()`, so there is no restart to pick up a change under `runserver`.
`MDJANGO_CONTENT_DIR` is required. Everything else has a default. None of these affect the Theme's
colours or type; those are CSS ([theme tokens](../theme-tokens/)).

## Content

| Setting | Type | Default | Effect |
|---|---|---|---|
| `MDJANGO_CONTENT_DIR` | `str` or `Path` | required | Root of the Content tree. |
| `MDJANGO_INCLUDE_DRAFTS` | `bool` | `DEBUG` | Include Pages marked `draft: true` in the registry, and so in navigation, search, the LLM artifacts and the export. |
| `MDJANGO_ALWAYS_REBUILD` | `bool` | `DEBUG` | Re-read the Content tree and rebuild the search index and LLM artifacts on every request. Also disables response caching. |

## Shell

| Setting | Type | Default | Effect |
|---|---|---|---|
| `MDJANGO_BRAND` | `str` | `"docs"` | Wordmark text in the header. Fallback for `<title>`. |
| `MDJANGO_SITE_TITLE` | `str` | `""` | `<title>`, and the `#` heading of `llms.txt` and `llms-full.txt`. Falls back to `MDJANGO_BRAND`. |
| `MDJANGO_HOME_URL` | `str` | `"/"` | Target of the wordmark link. |
| `MDJANGO_VERSION` | `str` | `""` | Display string rendered as a chip in the header. Hidden when empty. Not used for routing. |
| `MDJANGO_GITHUB_URL` | `str` | `""` | Renders a header link labelled `github`. Hidden when empty. |
| `MDJANGO_HEADER_LINKS` | iterable of `{"label": str, "url": str}` dicts or `mdjango.conf.HeaderLink` | `()` | Extra header links, in order, between the `llms.txt` links and the GitHub link. |

## LLM artifacts

| Setting | Type | Default | Effect |
|---|---|---|---|
| `MDJANGO_LLM_DOCS` | `bool` | `True` | Master switch for the `llms.txt`, `llms-full.txt`, `index.md` and per-page `.md` routes, the header and drawer links, the `<link rel="alternate">`, and the export of those files. `False` returns 404 from all four routes. Search is unaffected. |
| `MDJANGO_DESCRIPTION` | `str` | `""` | One-line summary rendered as a `>` blockquote under the title in `llms.txt` and `llms-full.txt`. |

## Caching

| Setting | Type | Default | Effect |
|---|---|---|---|
| `MDJANGO_CACHE_SECONDS` | `int` | `300` | TTL of the server-side page cache (Django's default cache backend, key `mdjango:page:<path>`, `@index` for the Index page) and the value of `Cache-Control: public, max-age=`. `0` disables the page cache and sets `Cache-Control: no-cache`. Ignored while `MDJANGO_ALWAYS_REBUILD` is true. An `ETag` is always emitted. |

## Validation

Nothing is checked at startup. There are no Django system checks. A wrong value surfaces on the
first request, as a 500 in a running site or as an error from `mdjango_build`.

| Fault | Raised |
|---|---|
| `MDJANGO_CONTENT_DIR` missing or empty | `django.core.exceptions.ImproperlyConfigured` |
| `MDJANGO_CONTENT_DIR` is not a directory | `mdjango.features.common.exceptions.ContentError` |
| a `MDJANGO_HEADER_LINKS` dict without `label` or `url` | `KeyError` |
| `MDJANGO_CACHE_SECONDS` not convertible with `int()` | `ValueError` or `TypeError` |

## Not settings

- `INSTALLED_APPS` must contain `"django_cotton"` and `"mdjango"`. `"django.contrib.staticfiles"` is
  needed to serve the Shell's assets. Order between the two apps does not matter.
- `STATIC_URL` is used by `mdjango_build` as the prefix of the exported static directory.
- There is no setting for the maximum tree depth (fixed at three), for disabling search, for the
  markdown extensions, for a canonical URL, for a logo, or for adding a stylesheet. See
  [Change the colours and type](../../how-to/change-colours-and-type/) for the stylesheet.
