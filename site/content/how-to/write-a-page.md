---
title: Write a page
weight: 20
description: Front-matter, headings that feed the table of contents, code blocks, tables, and links between pages.
---

# Write a page

**Goal:** write one markdown file that renders well in the shell and links correctly to its
neighbours.

**You need:** a [content tree](../structure-a-content-tree/) to put it in. The full list of enabled
markdown extensions is in the [markdown reference](../../reference/markdown/).

## Start with front-matter

```markdown
---
title: Roll back a deploy
weight: 30
description: Return an app to its previous build with one command.
---

# Roll back a deploy
```

Four keys are read; anything else is ignored silently:

| Key | Effect |
|---|---|
| `title` | Nav label, `<title>`, breadcrumb. Falls back to the first `#` heading, then the humanised filename. |
| `weight` | Position among siblings (lower first; default `100`). |
| `draft` | `true` hides the page outside development. |
| `description` | One line, appended to the page's entry in `llms.txt`. |

The block is parsed as flat `key: value` lines, not YAML: no lists, no nesting, no multi-line
values. Surrounding quotes are stripped. Keys are lower-cased.

Open the body with a `#` heading that repeats the title. The rendered page shows it as the
article's heading, and the `.md` alternate is served as-is when the body already starts with one.

## Structure with H2 and H3

The "On this page" table of contents collects `##` and `###` headings only. `####` headings render
and get a permalink but do not appear in the rail.

```markdown
## Prepare the host
### Open the firewall
## Run the rollback
```

Every heading from `##` to `####` gets an `id` and a `#` permalink; the scroll-spy highlights the
current section as the reader moves.

## Tag every code fence

````markdown
```bash
acme rollback web
```
````

Untagged fences render as plain preformatted text — the highlighter does not guess a language.
Every fence gets a copy button. Fences inside lists or blockquotes work (`superfences`).

Inline code uses backticks as usual. `~~strikethrough~~` is enabled.

## Use tables and definition lists

```markdown
| Flag | Meaning |
|---|---|
| `--keep` | Leave the old build on disk. |

Term
:   Definition indented four spaces.
```

## Link to another page

Pages are **served one level deeper than they are stored**: `how-to/deploy.md` is served at
`/docs/how-to/deploy/`. Relative links therefore start from the page's own URL directory, not its
file's directory. Always end a link with the trailing slash.

| From a page in… | To a sibling in the same group | To a page in another Section |
|---|---|---|
| a Section (`how-to/deploy.md`) | `](../rollback/)` | `](../../reference/cli/)` |
| a Subsection (`how-to/hosts/harden.md`) | `](../provision/)` | `](../../../reference/cli/)` |
| the root `_index.md` | — | `](how-to/deploy/)` |

Writing `](../how-to/rollback/)` from `how-to/deploy.md` doubles the segment and 404s. There is no
link rewriting and no redirect table: a moved page breaks every link that pointed at it until you
update them.

## What is not available

- **Admonitions** (`!!! note`) are not enabled; they render as plain paragraphs. Use a blockquote.
- **Images and other files** in the content directory are ignored. Only `.md` files are read, and
  nothing is copied into the export. Serve images from your project's static files and link them by
  URL.
- **Raw HTML** is passed through untouched (the tree is trusted content), including inside
  `<div markdown="1">` blocks.
