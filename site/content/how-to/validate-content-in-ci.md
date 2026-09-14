---
title: Validate content in CI
weight: 70
description: Fail a build on a broken Content tree before it reaches a running server.
---

# Validate content in CI

**Goal:** catch a malformed Content tree, a page that fails to render, or a broken search index at
build time instead of as a 500 on the first request.

**You need:** a CI job that can install the project and import its Django settings. The command's
full behaviour is in the [`mdjango_build` reference](../../reference/mdjango-build/).

## Run the check

```bash
python manage.py mdjango_build --check
```

```text
ok — N pages render, content valid
```

The command clears mdjango's in-process caches, reads the Content tree, renders every page through
the same template the runtime views use, and builds the search index and the LLM artifacts. It
writes nothing to disk.

On a render failure it prints one `<url>: <error>` line per page to stderr, then exits with
status 1:

```text
CommandError: N page(s) failed to render
```

A structural fault in the tree fails before any page renders, with the message naming the files:

```text
CommandError: content is capped at three levels (section -> subsection -> page); found a nested directory content/how-to/hosts/cloud inside subsection 'hosts'
```

```text
CommandError: duplicate page path 'how-to/deploy': content/how-to/deploy.md and content/how-to/Deploy.md
```

## Run it with production settings

Drafts are included when `MDJANGO_INCLUDE_DRAFTS` is true, which defaults to `DEBUG`. Run the check
with the settings you deploy so it validates exactly the pages production will serve:

```bash
DJANGO_SETTINGS_MODULE=config.settings_production python manage.py mdjango_build --check
```

The check needs no database, no secret beyond what your settings module insists on, and no network.

## Why this is the only gate

In a running site the Content tree is read on the first request after a restart. A fault there
raises `ContentError`, which no view catches, so the request returns a 500 and every request after
it does too until the tree is fixed. There is no startup check and no system check. Run the command
on every change to the Content tree and before every deploy.
