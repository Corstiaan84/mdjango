---
title: walden.toml
weight: 10
description: name, domain, port, volumes, env, timers — the complete file format.
---

# walden.toml

`name`, `domain`, `port`, `volumes`, `env`, `timers` — the complete file format, with defaults
for every key.

```toml
name   = "notes-app"
domain = "notes.example.com"
port   = 3000

[[volume]]
name = "data"
path = "/var/lib/app"
```
