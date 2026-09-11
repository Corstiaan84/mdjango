---
title: Databases and volumes
weight: 10
description: Declare a volume and it becomes a named podman volume, mounted into the container.
---

# Databases and volumes

Declare a volume in `walden.toml` and it becomes a named podman volume, mounted into the
container at the path you give.

```toml
[[volume]]
name = "data"
path = "/var/lib/app"
```

A Postgres database is declared the same way and gets its own managed volume and connection
string, injected as an environment value at unit start.
