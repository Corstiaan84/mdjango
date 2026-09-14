---
title: Content tree rules
weight: 20
description: Directory layout, index files, front-matter keys, ordering, slugs and URLs, and the errors a tree can raise.
---

# Content tree rules

The Content tree is the directory `MDJANGO_CONTENT_DIR` points at. It is the only source of content.
There is no database, no admin and no registration step.

## Layout

| Level | What | Where |
|---|---|---|
| Section | one immediate subdirectory of the root | `content/<section>/` |
| Subsection | one subdirectory of a Section | `content/<section>/<subsection>/` |
| Page | one `.md` file | at the root, in a Section, or in a Subsection |
| Index page | the root `_index.md` | `content/_index.md` |
| Loose page | a Page at the root or directly in a Section | `content/about.md`, `content/<section>/page.md` |

- A directory inside a Subsection raises `ContentError`. There is no fourth level.
- Only `.md` files are read. Other files are ignored and nothing is copied to the export.
- Directories are walked in filename order, then sorted by weight.

## Index files

Recognised stems: `_index` and `index`. A file named `index.md` inside a Section or Subsection is
treated as that group's index file: its body is discarded and it gets no URL. Name a Page anything
else.

| Location | `title` | `weight` | body |
|---|---|---|---|
| content root | Index page title and Home link label | ignored | **rendered** as the mount-root page |
| Section or Subsection | group title | group order | **discarded** |

The root `_index.md` ignores `draft`. It is read unconditionally. A Section or Subsection with no
index file takes its title from the humanised directory name (`-` and `_` become spaces, first
letter capitalised, the rest lower-cased) and weight `100`.

## Front-matter

A leading block fenced by lines that are exactly `---`. Each line is split on its first `:`. The
key is lower-cased and stripped. The value is stripped of whitespace and of surrounding `'` or `"`.
Lines without a colon are skipped. No YAML: no lists, no nesting, no multi-line values. A block
without a closing `---` is treated as body. Unknown keys are ignored.

| Key | Type | Default | Notes |
|---|---|---|---|
| `title` | string | first `#` heading in the body, else humanised filename stem | |
| `weight` | integer | `100` | a non-integer value falls back to the default |
| `draft` | boolean | `false` | accepts `true`/`yes`/`on` and `false`/`no`/`off`, case-insensitive. Anything else is the default. |
| `description` | string | `""` | suffix of the Page's `llms.txt` entry. Page-level only. |
| `updated` | date | none | ISO-8601 `YYYY-MM-DD`. Feeds the Page's sitemap `<lastmod>`; omitted when absent. A malformed value is ignored with a build warning (never file mtime — a checkout would make it wrong). Page-level only. See [Make your docs discoverable](../../how-to/make-docs-discoverable/). |

The first-heading fallback matches a `#` line with up to three leading spaces and optional closing
`#`s.

## Ordering

Siblings sort by `(weight, title.lower())`, lowest weight first, regardless of kind: Pages,
Subsections and Sections in the same parent share one sequence. A run of consecutive Loose pages at
the root renders as one untitled navigation group at its position and as a `## Documentation`
heading in `llms.txt`.

Previous/next links follow the flattened navigation order across Section and Subsection boundaries.
The Index page is not part of that order.

## Visibility

- A Page with `draft: true` is omitted unless `MDJANGO_INCLUDE_DRAFTS` is true.
- A Section or Subsection with no visible Pages is omitted from navigation, search, `llms.txt` and
  the export. This is not an error.

## Slugs and URLs

Slugs come from Django's `slugify` applied to the filename stem (Pages) or directory name (groups).
`slugify` lower-cases, so `Hello.md` and `hello.md` collide.

| Stored at | Path | Served at |
|---|---|---|
| `content/_index.md` | `""` | `/<mount>/` |
| `content/about.md` | `about` | `/<mount>/about/` |
| `content/how-to/deploy.md` | `how-to/deploy` | `/<mount>/how-to/deploy/` |
| `content/how-to/hosts/harden.md` | `how-to/hosts/harden` | `/<mount>/how-to/hosts/harden/` |

Sections and Subsections have no URL. Each Page also has a markdown alternate at the same path with
`.md` in place of the trailing slash (`/<mount>/how-to/deploy.md`; the Index page at
`/<mount>/index.md`).

## Errors

All are `mdjango.features.common.exceptions.ContentError`, raised when the registry is built. In a
running site that is the first request after a process start. No view catches it, so the request
returns a 500. `mdjango_build` catches it and exits with the message.

| Condition | Message contains |
|---|---|
| `MDJANGO_CONTENT_DIR` is not a directory | `content dir does not exist` |
| a directory inside a Subsection | `capped at three levels` |
| two files resolve to the same path | `duplicate page path` |
