---
title: Settings
weight: 10
description: Every MDJANGO_* Django setting, its type, default, effect, and what happens when it is wrong.
---

# Settings

All configuration is ordinary Django settings. mdjango reads them on every request through
`mdjango.conf.get_conf()`, so there is no restart to pick up a change under `runserver`.
`MDJANGO_CONTENT_DIR` is required. Everything else has a default. The Theme's colours and type are
set in CSS ([theme tokens](../theme-tokens/)), not here — the one setting that touches them,
`MDJANGO_EXTRA_CSS`, only *loads* your stylesheet; it carries no values.

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
| `MDJANGO_EXTRA_CSS` | `str` or iterable of `str` | `()` | Stylesheet `{% static %}` name(s), linked after mdjango's own sheet — the supported way to override the [seven CSS seeds](../theme-tokens/) without shadowing a template. A string is one file; an iterable is several, in order. See [Change the colours and type](../../how-to/change-colours-and-type/). |
| `MDJANGO_ASSET_EXTENSIONS` | iterable of `str` | `png jpg jpeg gif svg webp` | Non-markdown file extensions served as [assets](../../how-to/write-a-page/) from the Content tree (case-insensitive, leading dot optional). Defaults to images; set it to widen (e.g. add `pdf`) or narrow what a page can reference beside itself. |

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
| `MDJANGO_EXTRA_CSS` neither a string nor an iterable of them | `TypeError` |
| `MDJANGO_CACHE_SECONDS` not convertible with `int()` | `ValueError` or `TypeError` |

## Not settings

- `INSTALLED_APPS` must contain `"django_cotton"` and `"mdjango"`. `"django.contrib.staticfiles"` is
  needed to serve the Shell's assets. Order between the two apps does not matter.
- `STATIC_URL` is used by `mdjango_build` as the prefix of the exported static directory.
- There is no setting for the maximum tree depth (fixed at three), for disabling search, for the
  markdown extensions, for a canonical URL, or for a logo. (A stylesheet *does* have one now —
  `MDJANGO_EXTRA_CSS`, above.)
- There is no setting for analytics or other `<head>` scripts — a setting cannot safely carry raw
  markup. Inject them through the head slot instead; see
  [Add analytics and other head tags](../../how-to/add-head-tags/).
- There is no base-URL or domain setting. mdjango emits root-relative URLs, so it stays portable
  across mount prefixes. The sitemap needs absolute URLs, so it derives the domain from the request
  at runtime, or from the `mdjango_build --base-url` flag for the static export — never a setting.
  See [Make your docs discoverable](../../how-to/make-docs-discoverable/).
