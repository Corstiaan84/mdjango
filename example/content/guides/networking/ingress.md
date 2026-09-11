---
title: Ingress
weight: 10
description: One shared ingress fronts every app on the host and routes by hostname.
---

# Ingress

A single shared ingress fronts every app on the host. It routes by hostname, so an app declares
the domains it answers on and nothing else has to change.

```bash
$ walden ingress show notes-app
```

Requests that match no declared hostname are refused at the edge rather than falling through to
an arbitrary app.
