---
title: Files walden writes
weight: 30
description: One systemd unit per app, one Caddy block per domain, kept builds under /var/lib/walden.
---

# Files walden writes

One systemd unit per app, one Caddy block per domain, kept builds under
`/var/lib/walden/builds`.

| Path | What it is |
|---|---|
| `~/.config/systemd/user/<app>.service` | the unit |
| `/etc/caddy/walden.d/<app>.caddy` | the route |
| `/var/lib/walden/builds/<app>/` | kept builds, for rollback |
