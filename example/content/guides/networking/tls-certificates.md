---
title: TLS certificates
weight: 20
description: Certificates are issued and renewed for you; bring your own only when you must.
---

# TLS certificates

Certificates are issued on first request for a hostname and renewed well before expiry. There is
nothing to schedule.

```bash
$ walden tls status notes-app
```

If a certificate has to come from elsewhere — an internal CA, or an edge proxy that terminates TLS
itself — place it on the host and point the app at it instead.
