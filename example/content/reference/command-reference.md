---
title: Command reference
weight: 20
description: up, ls, logs, rollback, backup, secrets, cron, uninstall — flags and exit codes.
---

# Command reference

`up`, `ls`, `logs`, `rollback`, `backup`, `secrets`, `cron`, `uninstall`. Flags and exit codes for
every command.

## up

Builds the image, installs the unit, publishes the route, reloads Caddy.

## rollback

Swaps the running unit back to a kept build under `/var/lib/walden/builds`.
