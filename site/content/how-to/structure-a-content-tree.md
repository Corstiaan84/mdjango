---
title: Structure a content tree
weight: 10
description: Lay out sections, subsections and pages; control their order; set the landing page; hide drafts.
---

# Structure a content tree

**Goal:** arrange a set of markdown files so the navigation reads the way you want.

**You need:** mdjango [installed and mounted](../../getting-started/install-and-mount/). The exact
rules this page applies are in the [content tree reference](../../reference/content-tree/).

## Lay out the directories

The Content tree is capped at three levels: **Section → Subsection → Page**. Each immediate
subdirectory of `MDJANGO_CONTENT_DIR` is a Section; a subdirectory of a Section is a Subsection;
each `.md` file is a Page.

```text
content/
  _index.md                 # landing page (optional)
  about.md                  # a loose page          -> /docs/about/
  getting-started/          # a Section
    _index.md               # section title + weight (front-matter only)
    quickstart.md           # a Page                -> /docs/getting-started/quickstart/
  guides/
    networking/             # a Subsection — a nav group, not a page
      _index.md             # subsection title + weight (front-matter only)
      ingress.md            # a Page                -> /docs/guides/networking/ingress/
    secrets.md              # a Page directly in the Section
```

A directory inside a Subsection is a build error — the site refuses to start rather than render an
unreadable sidebar. Filenames and directory names become the URL, so choose them deliberately;
renaming a file moves the page.

## Name and order a group

Give a Section or Subsection an `_index.md` holding only front-matter:

```markdown
---
title: Getting started
weight: 10
---
```

Its body is discarded. Without an `_index.md` the group takes its directory name, humanised
(`getting-started` → "Getting started"), and weight `100`.

Everything sorts by `(weight, title)` among its siblings, lowest weight first. Pages and groups sort
in the **same** list: a Subsection sits among its Section's loose pages wherever its weight puts it,
and a loose page at the root sits among the Sections. To place a group in the middle of a sequence,
give it a weight between its neighbours'.

```text
guides/
  backups.md            weight: 10
  databases.md          weight: 20
  networking/_index.md  weight: 30   <- collapsible group, between databases and jobs
  scheduled-jobs.md     weight: 40
```

Leave weights off when order does not matter; ties break on title.

## Set the landing page

Put an `_index.md` at the content root. Unlike a group's `_index.md`, its **body is rendered** as
the page at the mount root, and a Home link labelled with its title is pinned at the top of the
navigation.

```markdown
---
title: Acme docs
---

# Acme docs

Start with the [quickstart](getting-started/quickstart/).
```

Without a root `_index.md` the mount root serves the first Page in navigation order and there is
no Home link.

## Decide when to use a Subsection

A Subsection renders as a collapsible group, opened only while the reader is on one of its pages.
Reach for one when a Section's list has grown past what a reader scans at a glance; a Section with
four or five pages is better flat. Subsections have no URL of their own, so an overview belongs in
an ordinary Page inside the group.

Moving a Page into a Subsection changes its URL and shifts every relative link aimed at it by one
segment — rewrite the links in the same change. See [Write a page](../write-a-page/) for the link
form.

## Hide work in progress

Mark a page `draft: true`:

```markdown
---
title: Recover onto a new host
draft: true
---
```

Drafts are left out of the navigation, search, `llms.txt` and the export unless
`MDJANGO_INCLUDE_DRAFTS` is on — and it defaults to your `DEBUG` setting, so drafts show while you
develop and disappear in production. A group whose only pages are drafts (or that holds only an
`_index.md`) is omitted entirely; that is not an error.

The root `_index.md` is the exception: it is read regardless of `draft`, so a draft landing page
still renders. If you have nothing to say there yet, leave the file out.

## Check the tree before you deploy

```bash
python manage.py mdjango_build --check
```

This walks the tree, renders every page, and exits non-zero on a fourth level, a duplicate path
(two files that slugify to the same URL) or a missing content directory — the same errors a running
site would raise on its first request.
