---
title: Secrets
weight: 40
description: Environment values live in root-owned files on the server, injected at unit start.
---

# Secrets

Environment values live in root-owned files on the server, injected at unit start. Never in your
repo.

```bash
$ walden secrets set notes-app DATABASE_URL=postgres://…
```
