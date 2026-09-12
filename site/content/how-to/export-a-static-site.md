---
title: Export a static site
weight: 70
description: Write the whole site — pages, search index, LLM artifacts and assets — to a directory with mdjango_build, and host it at the prefix it was built for.
---

# Export a static site

**Goal:** produce a directory you can serve from any static file host, identical to the running
site.

**You need:** the consuming project configured as for runtime — the export uses the same settings,
content directory and templates. The command's options are in the
[`mdjango_build` reference](../../reference/mdjango-build/).

## Build the dist

```bash
python manage.py mdjango_build
```

```text
exported 21 pages + 24 text files + 17 static files to dist
```

The output directory defaults to `./dist`; pass a path to change it. The layout mirrors the live
URLs, one directory per page, with file-shaped URLs written as files:

```text
dist/
  docs/
    index.html                          # /docs/
    getting-started/
      install-and-mount/index.html      # /docs/getting-started/install-and-mount/
      install-and-mount.md              # the page's markdown alternate
    search-index.json
    llms.txt
    llms-full.txt
    index.md
  static/
    mdjango/                            # the stylesheet, fonts, controllers, vendored JS
```

`docs/` is your mount prefix; `static/` is your `STATIC_URL`. Existing files under the static
destination are removed and rewritten; page files are overwritten in place.

## Host it at the same prefix

The exported HTML references `/docs/…` and `/static/…` as **absolute paths** — the same ones the
running site uses. Serve `dist/` as the root of a host so that `/docs/` resolves to
`dist/docs/index.html`. Uploading only `dist/docs/` under a different prefix breaks every
stylesheet, script and search request.

To preview locally:

```bash
python -m http.server --directory dist 8000
```

Open <http://127.0.0.1:8000/docs/>. Search works from the exported `search-index.json`; dark mode,
copy buttons and the drawer work from the exported controllers — nothing is fetched from the
network.

## Export without drafts

Drafts are included whenever `MDJANGO_INCLUDE_DRAFTS` is true, and it defaults to `DEBUG`. Run the
export with the settings you deploy with, or override for the build:

```bash
DJANGO_SETTINGS_MODULE=config.settings_production python manage.py mdjango_build
```

`MDJANGO_CACHE_SECONDS` has no effect on the export — the file server sets its own headers.

## Gate content in CI

```bash
python manage.py mdjango_build --check
```

Renders every page, the search index and the LLM artifacts without writing, prints one line per
failure to stderr, and exits non-zero if anything fails. Run it on every change to the content
tree.

## Know the limits

- Links to a URL prefix other than the one built for are not rewritten; the dist is not relocatable.
- Non-markdown files in the content directory are not copied. Images belong in your static files.
- The export runs your Django project. It is a management command, not a standalone tool, so the
  build environment needs the project's settings importable.
