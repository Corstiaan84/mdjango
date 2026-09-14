---
title: Markdown
weight: 70
description: The Python-Markdown extensions and options in effect, what the renderer adds, and what is not enabled.
---

# Markdown

Pages are rendered by Python-Markdown with a fixed extension set. There is no setting to change it.
Output is HTML5 (`output_format="html"`), tab length 4, one fresh parser per page.

## Extensions

| Extension | Provides |
|---|---|
| `toc` | heading `id`s and `#` permalinks, `toc_depth="2-4"`, permalink title "Link to this section" |
| `tables` | pipe tables |
| `attr_list` | `{: .class #id }` attribute lists on block and inline elements |
| `def_list` | definition lists (`Term` / `:   Definition`) |
| `md_in_html` | markdown inside `<div markdown="1">` blocks |
| `sane_lists` | list numbering follows the source; a list does not continue across a different marker |
| `pymdownx.superfences` | fenced code anywhere, including nested in lists and blockquotes |
| `pymdownx.highlight` | Pygments highlighting; `guess_lang=False`, `pygments_lang_class=True` |
| `pymdownx.betterem` | stricter emphasis parsing |
| `pymdownx.tilde` | `~~strikethrough~~` and `~subscript~` |
| `pymdownx.saneheaders` | `#` starts a heading only when followed by a space |

## What the renderer adds

- **Table of contents**: H2 and H3 headings only, in document order, as `TocItem(id, label, level)`.
  An H4 gets an id and a permalink but is not listed.
- **Code fences**: each Pygments block is wrapped as `<div class="… highlight code-block"
  data-controller="clipboard">` with a `copy` button inserted as its first child. The button copies
  the block's text at click time. An untagged fence is not highlighted.
- **Permalinks**: `<a class="headerlink" href="#id">#</a>` after each H2 to H4. Anchored headings
  clear the sticky header.

## Not enabled

- `admonition` and `pymdownx.blocks`. `!!! note` renders as text. Use a blockquote.
- `footnotes`, `abbr`, `pymdownx.tasklist`, `pymdownx.tabbed`, `pymdownx.emoji`,
  `pymdownx.arithmatex`.
- Mermaid or any diagram rendering.
- Link rewriting. Relative links are emitted as written.
- HTML sanitisation. The Content tree is treated as trusted. Raw HTML in a page, including inside
  `<div markdown="1">`, reaches the browser as written.

## Front-matter

Stripped before rendering; see [content tree rules](../content-tree/). The body is what is rendered,
and also what the `.md` alternate and `llms-full.txt` publish.
