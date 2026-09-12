---
title: mdjango_build
weight: 40
description: The management command that exports the site to a static directory or validates the content tree.
---

# `mdjango_build`

```bash
python manage.py mdjango_build [output_dir] [--check]
```

Export the documentation site to a static directory, or validate it without writing. This is the
only command mdjango adds; there is no console script.

## Arguments

| Argument | Default | Meaning |
|---|---|---|
| `output_dir` | `dist` | Directory to write into. Created if missing. |
| `--check` | off | Render every page, the search index and (when enabled) the LLM artifacts without writing anything. |

## Behaviour

1. Clears the in-process registry, search and LLM caches, then builds the registry from
   `MDJANGO_CONTENT_DIR` with the current settings (`MDJANGO_INCLUDE_DRAFTS` decides whether drafts
   are exported). A `ContentError` becomes a `CommandError`.
2. Renders each target through the same template and context the runtime views use: the landing
   page at the index URL, then every Page in navigation order.
3. Writes, under `output_dir`:
    - `<mount>/…/index.html` — one directory per page, mirroring the URL;
    - `<mount>/search-index.json`;
    - when `MDJANGO_LLM_DOCS` is true: `<mount>/llms.txt`, `<mount>/llms-full.txt`, `<mount>/index.md`
      and one `<mount>/…/<page>.md` per page;
    - `<STATIC_URL>/mdjango/…` — the package's static tree, copied whole. An existing directory at
      that destination is removed first.
4. Prints `exported N pages + N text files + N static files to <output_dir>`.

The `<mount>` prefix and `STATIC_URL` are taken from the project's URLconf and settings, and the
HTML contains them as absolute paths. The dist must be served with the same prefixes.

## `--check`

Performs steps 1 and 2 only, plus building the search index and LLM artifacts. Each failure is
written to stderr as `<url>: <error>`; if any occur the command raises
`CommandError("N page(s) failed to render")` and exits non-zero. On success it prints
`ok — N pages render, content valid`.

## Exit status

`0` on success; non-zero (Django's `CommandError` handling) on a content error, a render failure
under `--check`, or an I/O error while writing.
