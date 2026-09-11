---
title: Installing walden
weight: 30
description: The installer places a single binary and checks that podman, systemd and Caddy are present.
---

# Installing walden

The installer places a single binary in `/usr/local/bin/walden` and checks that podman, systemd
and Caddy are present.

```bash
$ curl -fsSL https://walden.sh/install | sh
```

Nothing else is written at install time. Everything walden manages later lives under
`/var/lib/walden` and your user's systemd directory.
