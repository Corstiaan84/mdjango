---
title: Quickstart
weight: 10
description: Takes a fresh VPS to a running application in about ten minutes, and explains every file it creates along the way.
eyebrow: getting started
---

# Quickstart

This page takes a fresh VPS to a running application in about ten minutes, and explains every
file it creates along the way. You need a server with a public IP, a domain pointed at it, and
SSH access.

## Install

On the server, as a user with sudo:

```bash
$ curl -fsSL https://walden.sh/install | sh
```

The installer places a single binary in `/usr/local/bin/walden` and checks that podman, systemd
and Caddy are present, installing any that are missing from your distribution's own repositories.

## Describe your app

In your project directory, `walden init` writes a minimal `walden.toml`:

```toml
name   = "notes-app"
domain = "notes.example.com"
port   = 3000
```

## Deploy

```bash
$ walden up
  building notes-app from Containerfile…
  ok  image built         4.2s
  ok  unit installed      notes-app.service
  ok  route published     notes.example.com
  ok  certificate issued  Let's Encrypt

  live at https://notes.example.com
```

That's the whole deploy. Walden built the image with podman, installed a systemd unit to keep it
running, appended a Caddy block for the domain, and reloaded. Every file it wrote is printed to
the terminal.

## Look around

Everything walden created is a plain file:

| Path | What it is |
|---|---|
| `~/.config/systemd/user/notes-app.service` | the unit |
| `/etc/caddy/walden.d/notes-app.caddy` | the route |
| `/var/lib/walden/builds/notes-app/` | kept builds, for rollback |
