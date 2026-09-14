---
title: Structure a content tree
weight: 20
description: Set the Index page, order Sections and Pages, group Pages into a Subsection, and hide drafts.
---

# Structure a content tree

**Goal:** shape the left navigation: which page is home, what order things appear in, which Pages
collapse together, and what stays hidden.

**You need:** a Content tree that already serves. The rules this page applies are listed in the
[content tree reference](../../reference/content-tree/).

## Set the Index page

```markdown
<!-- content/_index.md -->
---
title: Acme docs
---

# Acme docs

Start with [installation](getting-started/install/).
```

A root `_index.md` is the **Index page**: it is served at the mount root and appears as the pinned
**Home link** above every Section in the navigation, labelled with its title. Without it, the mount
root serves the first Page in navigation order and there is no Home link.

The root `_index.md` ignores `draft`. It is read whether or not drafts are included.

## Order Sections and Pages

```markdown
<!-- content/getting-started/_index.md -->
---
title: Getting started
weight: 10
---
```

A Section's `_index.md` supplies only its `title` and `weight`. Its body is discarded. Without one,
the Section is titled from its directory name and sorts at weight `100`.

Everything sorts by `(weight, title)` among its siblings, lowest weight first, whatever its kind.
Give explicit weights to anything whose order matters and leave the rest at the default. A Loose
page at the content root sorts among the Sections by the same rule.

## Group Pages into a Subsection

Reach for a Subsection when a Section's page list has stopped being scannable, not by default. A
Section with five Pages is better flat.

```bash
mkdir content/how-to/hosts
git mv content/how-to/provision.md content/how-to/harden.md content/how-to/hosts/
```

```markdown
<!-- content/how-to/hosts/_index.md -->
---
title: Hosts
weight: 40
---
```

A Subsection renders collapsed in the navigation, expanded only while the reader is on one of its
Pages.
It has no URL of its own. It sorts among the Section's Pages by its weight, so it can sit in the
middle of a sequence.

Moving a Page into a Subsection changes its URL from `/docs/how-to/harden/` to
`/docs/how-to/hosts/harden/`. Every relative link aimed at it, and every link from it, shifts by one
segment. Rewrite the links in the same commit. See the link table in
[Write a page](../write-a-page/).

A directory inside a Subsection is an error. There is no fourth level.

## Hide work in progress

```markdown
---
title: Multi-region failover
draft: true
---
```

A draft is omitted from navigation, search, the LLM artifacts and the static export. Drafts are
included when `MDJANGO_INCLUDE_DRAFTS` is true, which defaults to `DEBUG`, so you see them under
`runserver` and not in production.

A Section or Subsection whose Pages are all drafts disappears with them. This is not an error.

## Check the result

```bash
python manage.py mdjango_build --check
```

A nested directory inside a Subsection or two files resolving to the same path fail here with a
message naming the files. In a running site the same fault raises on the first request that reads
the tree and returns a 500. See [Validate content in CI](../validate-content-in-ci/).
