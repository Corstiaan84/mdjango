---
title: Export a static site
weight: 100
description: Write the whole site to a directory with mdjango_build and host it at the prefix it was built for, when nothing else from Django is needed.
---

# Export a static site

**Goal:** produce a directory a static file host can serve, identical to the running site, for a
deployment that needs the docs and nothing else.

Serving from your Django process is the primary way to run mdjango, and the one the rest of these
docs assume. The export exists for the case where no Django process will run: a docs-only host, a
preview bucket, an offline copy.

**You need:** the project configured as for runtime. The export uses the same settings, Content tree
and templates. The command's options are in the [`mdjango_build` reference](../../reference/mdjango-build/).

## Build the dist

```bash
python manage.py mdjango_build
```

```text
exported N pages + N text files + N static files to dist
```

The output directory defaults to `./dist`. Pass a path as the first argument to change it. The
layout mirrors the live URLs, one directory per page, with file-shaped URLs written as files:

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
    mdjango/                            # stylesheet, fonts, controllers, vendored JS
```

`docs/` is your mount prefix. `static/` is your `STATIC_URL`. The static destination is deleted and
rewritten on every build. Page files are overwritten in place.

## Build with the default static storage

The export copies mdjango's static tree with its plain filenames. If your production settings use a
manifest storage backend (hashed filenames, as WhiteNoise's `CompressedManifestStaticFilesStorage`
does), `{% static %}` writes hashed URLs into the HTML that the export never creates, and every
stylesheet and script 404s.

Run the export with the default `staticfiles` storage. Keep the manifest backend for the runtime
site only, or point `DJANGO_SETTINGS_MODULE` at a settings module that omits it for the build.

## Add your own static files

Only mdjango's own static tree is copied. A stylesheet you load after mdjango's, or an image linked
from a page, is referenced by the HTML but not written. Copy those into `dist/static/` after the
build:

```bash
python manage.py mdjango_build
cp -r acme-static/. dist/static/acme/
```

## Host it at the same prefix

The exported HTML references `/docs/…` and `/static/…` as absolute paths, the same ones the running
site uses. Serve `dist/` as the root of a host so that `/docs/` resolves to `dist/docs/index.html`.
Uploading only `dist/docs/` under a different prefix breaks every stylesheet, script and search
request. Nothing rewrites paths; the dist is not relocatable. To change the prefix, change the mount
in `urls.py` and rebuild.

To preview locally:

```bash
python -m http.server --directory dist 8000
```

Open <http://127.0.0.1:8000/docs/>. Search works from the exported `search-index.json`. Dark mode,
copy buttons and the drawer work from the exported controllers. Nothing is fetched from the network.

## Export without drafts

Drafts are exported when `MDJANGO_INCLUDE_DRAFTS` is true, which defaults to `DEBUG`. Run the export
with the settings you would deploy:

```bash
DJANGO_SETTINGS_MODULE=config.settings_production python manage.py mdjango_build
```

`MDJANGO_CACHE_SECONDS` has no effect on the export. The file server sets its own headers, and
there is no login gate: anything that needs authentication stays on the Django process.

## Know the limits

- Without a root `_index.md` the first Page is written twice: once at `/docs/` and once at its own
  URL. No canonical link is emitted.
- Non-markdown files in the Content tree are not copied.
- The export is a management command, not a standalone tool. The build environment needs the
  project's settings importable.
