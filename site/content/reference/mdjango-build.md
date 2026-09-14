---
title: mdjango_build
weight: 40
description: The management command that validates the Content tree or exports the site to a static directory.
---

# `mdjango_build`

```bash
python manage.py mdjango_build [output_dir] [--check]
```

Validate the Content tree and every page's render without writing, or export the site to a static
directory. This is the only command mdjango adds. There is no console script.

## Arguments

| Argument | Default | Meaning |
|---|---|---|
| `output_dir` | `dist` | Directory to write into. Created if missing. |
| `--check` | off | Validate content and render every page without writing. |

## Behaviour

1. Clears the in-process registry, search and LLM caches, then builds the registry from
   `MDJANGO_CONTENT_DIR` with the current settings. `MDJANGO_INCLUDE_DRAFTS` decides whether drafts
   are included. A `ContentError` becomes a `CommandError`.
2. Lists the targets: the page served at the mount root (the Index page, or the first Page in
   navigation order when there is none), then every Page in navigation order. Without a root
   `_index.md` the first Page is therefore a target twice, at `/<mount>/` and at its own URL.
3. With `--check`, renders each target through the same template and context the runtime views use,
   builds the search index and, when `MDJANGO_LLM_DOCS` is true, the LLM artifacts. Writes nothing.
   Stops here.
4. Otherwise renders each target and writes, under `output_dir`:
    - `<mount>/…/index.html`, one directory per page, mirroring the URL;
    - `<mount>/search-index.json`, minified;
    - when `MDJANGO_LLM_DOCS` is true: `<mount>/llms.txt`, `<mount>/llms-full.txt`,
      `<mount>/index.md` and one `<mount>/…/<page>.md` per Page;
    - `<STATIC_URL>/mdjango/…`, mdjango's own static tree copied whole. An existing directory at
      that destination is removed first. No other app's static files are copied.
5. Prints `exported N pages + N text files + N static files to <output_dir>`.

`<mount>` and `STATIC_URL` come from the project's URLconf and settings, and the HTML contains them
as absolute paths. The dist must be served at the same prefixes. Static URLs are whatever
`{% static %}` produced under the active storage backend; with a manifest backend they are hashed
names the export does not create.

## Output of `--check`

On success, to stdout:

```text
ok — N pages render, content valid
```

On failure, one line per problem to stderr, then a `CommandError`:

```text
<url>: <error>
search index: <error>
llm artifacts: <error>
CommandError: N page(s) failed to render
```

## Exit status

`0` on success. `1` on a `CommandError`: a content error, a render failure under `--check`. Any
other exception, such as an I/O error while writing or a missing `MDJANGO_CONTENT_DIR`, propagates
as a traceback with a non-zero status.

`MDJANGO_CACHE_SECONDS` has no effect on the command.
