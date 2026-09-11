---
title: Backups and restores
weight: 20
description: A snapshot of every declared volume, keeping the last seven by default.
---

# Backups and restores

`walden backup` runs a snapshot of every declared volume and keeps the last seven by default.
Restore any snapshot by name.

```bash
$ walden backup
$ walden restore notes-app data 2026-09-01
```
