---
title: Content tree rules
weight: 20
description: Directory layout, index files, front-matter keys, ordering, slugs and URLs, and the errors a tree can raise.
---

# Content tree rules

The Content tree is the directory `MDJANGO_CONTENT_DIR` points at. It is the only source of
content: no database, no admin, no registration step.

## Layout

| Level | What | Where |
|---|---|---|
| Section | one immediate subdirectory of the root | `content/<section>/` |
| Subsection | one subdirectory of a Section | `content/<section>/<subsection>/` |
| Page | one `.md` file | at the root, in a Section, or in a Subsection |
| Index page | the root `_index.md` | `content/_index.md` |
| Loose page | a Page at the root or directly in a Section | `content/about.md`, `content/<section>/page.md` |

- A directory inside a Subsection raises `ContentError` ("content is capped at three levels").
- Only `.md` files are read. Other files are ignored; nothing is copied to the export.
- Directories are walked in filename order, then sorted by weight.

## Index files

Recognised stems: `_index` and `index`.

| Location | `title` | `weight` | body |
|---|---|---|---|
| content root | Index page title; Home link label | ignored | **rendered** as the mount-root page |
| Section or Subsection | group title | group order | **discarded** |

The root `_index.md` ignores `draft`; it is read unconditionally. A Section or Subsection with no
`_index.md` takes its title from the humanised directory name (`-` and `_` → space, first letter
capitalised) and weight `100`.

## Front-matter

A leading block fenced by lines that are exactly `---`. Each line is split on its first `:`; the
key is lower-cased and stripped; the value is stripped of whitespace and surrounding `'` or `"`.
No YAML: no lists, no nesting, no multi-line values. A block without a closing `---` is treated as
body. Unknown keys are ignored.

| Key | Type | Default | Notes |
|---|---|---|---|
| `title` | string | first `#` heading in the body, else humanised filename stem | |
| `weight` | integer | `100` | non-integer values fall back to the default |
| `draft` | boolean | `false` | accepts `true`/`yes`/`on` and `false`/`no`/`off`, case-insensitive |
| `description` | string | `""` | suffix of the page's `llms.txt` entry; page-level only |

## Ordering

Siblings sort by `(weight, title.lower())`, lowest weight first, **regardless of kind**: Pages,
Subsections and Sections in the same parent share one sequence. A run of consecutive loose pages
at the root renders as one untitled navigation group at its position and as a `## Documentation`
heading in `llms.txt`.

Previous/next links follow the flattened navigation order across Section and Subsection
boundaries.

## Visibility

- A Page with `draft: true` is omitted unless `MDJANGO_INCLUDE_DRAFTS` is true.
- A Section or Subsection with no visible Pages is omitted from navigation, search, `llms.txt` and
  the export. This is not an error.

## Slugs and URLs

Slugs come from Django's `slugify` applied to the filename stem (Pages) or directory name (groups).

| Stored at | Path | Served at |
|---|---|---|
| `content/_index.md` | `""` | `/<mount>/` |
| `content/about.md` | `about` | `/<mount>/about/` |
| `content/how-to/deploy.md` | `how-to/deploy` | `/<mount>/how-to/deploy/` |
| `content/how-to/hosts/harden.md` | `how-to/hosts/harden` | `/<mount>/how-to/hosts/harden/` |

Sections and Subsections have no URL. Each Page also has a markdown alternate at the same path with
`.md` instead of the trailing slash (`/<mount>/how-to/deploy.md`; the Index page at `/<mount>/index.md`).

## Errors

All are `mdjango.features.common.exceptions.ContentError`, raised when the registry is built: on
the first request in a running site, or immediately by `mdjango_build`.

| Condition | Message contains |
|---|---|
| `MDJANGO_CONTENT_DIR` is not a directory | `content dir does not exist` |
| a directory inside a Subsection | `capped at three levels` |
| two files resolve to the same path (including case-only differences, `Hello.md` vs `hello.md`) | `duplicate page path` |
