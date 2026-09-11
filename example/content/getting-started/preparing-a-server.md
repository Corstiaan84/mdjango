---
title: Preparing a server
weight: 20
description: A public IP, a domain pointed at it, and SSH access. Anything with systemd works.
---

# Preparing a server

You need a public IP, a domain pointed at it, and SSH access. Debian, Fedora and Ubuntu are
covered; anything with systemd works.

## DNS

Point an `A` record at the server's IP before you deploy — the certificate step needs the domain
to resolve.

## A sudo user

walden runs its apps rootless, but the one-time install needs sudo to place the binary and check
for podman, systemd and Caddy.
