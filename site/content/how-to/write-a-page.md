---
title: Write a page
weight: 10
description: Front-matter, headings the table of contents picks up, tagged code fences, and relative links that resolve.
---

# Write a page

**Goal:** add one markdown file that renders with the right title, a table of contents, highlighted
code and working links.

**You need:** a Content tree that already serves. The full key list and parser rules are in the
[content tree reference](../../reference/content-tree/); the extension list is in the
[markdown reference](../../reference/markdown/).

## Start with front-matter and an H1

````markdown
---
title: Roll back a deploy
weight: 30
description: Return a host to the previous release.
---

# Roll back a deploy
````

Front-matter is a block of `key: value` lines between two lines that are exactly `---`. It is not
YAML: no lists, no nesting, no multi-line values. Five keys are read.

| Key | Effect |
|---|---|
| `title` | navigation label and `<title>`. Falls back to the first `#` heading, then the filename. |
| `weight` | position among siblings, lowest first. Default `100`. |
| `draft` | `true` hides the page unless drafts are included. |
| `description` | the suffix of the page's `llms.txt` entry. |
| `updated` | an ISO date (`2024-03-15`) for the page's sitemap `<lastmod>`. Optional; a typo is ignored with a build warning. |

Put an H1 in the body too. The article title is the body's `#` heading, and the `.md` alternate of a
page without one gets a synthesised heading.

## Use H2 and H3 for the table of contents

```markdown
## Stop traffic

### Drain the pool

## Restore the previous build
```

The "On this page" rail lists H2 and H3 headings only. H4 gets an anchor and a permalink but is not
listed. Every heading from H2 to H4 gets a `#` permalink.

## Tag every code fence

````markdown
```bash
acme rollback web
```
````

Untagged fences render as plain preformatted text. The highlighter does not guess a language. Every
fence gets a copy button.

To show a fence inside a fence, make the outer fence four backticks. A three-backtick outer fence is
closed by the inner one and the rest of the example leaks out as headings and paragraphs.

## Use a blockquote for a callout

```markdown
> Rolling back does not restore the database. See the restore guide.
```

Admonitions (`!!! note`) are not enabled and render as a paragraph. Tables, definition lists,
`~~strikethrough~~` and `~subscript~` are enabled.

## Link to another page

Pages are served one level deeper than they are stored: `how-to/deploy.md` is served at
`/docs/how-to/deploy/`. Relative links start from the page's URL directory, not its file's
directory. End every link with a trailing slash.

| From a page in… | To a sibling | To a page in another Section |
|---|---|---|
| a Section (`how-to/deploy.md`) | `](../rollback/)` | `](../../reference/cli/)` |
| a Subsection (`how-to/hosts/harden.md`) | `](../provision/)` | `](../../../reference/cli/)` |
| the root `_index.md` | — | `](how-to/deploy/)` |

Writing `](../how-to/rollback/)` from `how-to/deploy.md` doubles the segment and 404s. Nothing
rewrites links and there is no redirect table. Moving a page breaks every link aimed at it until you
update them.

## Reference images by URL

Only `.md` files in the Content tree are read. Images and other files placed beside a page are
ignored and never served. Put them in your project's static files and link them by their served
URL:

```markdown
![Deploy pipeline](/static/acme/pipeline.svg)
```

Markdown is not a Django template. `{% static %}` is not evaluated in a page.

## Check the result

```bash
python manage.py mdjango_build --check
```

This renders every page without writing and exits non-zero on a broken tree. See
[Validate content in CI](../validate-content-in-ci/).
