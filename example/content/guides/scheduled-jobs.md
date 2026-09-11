---
title: Scheduled jobs
weight: 30
description: Cron-style work becomes systemd timers, with the same journald logs as everything else.
---

# Scheduled jobs

Cron-style work becomes systemd timers. A nightly backup gets the same journald logs as
everything else.

```toml
[[timer]]
name     = "nightly-backup"
schedule = "daily"
command  = "walden backup"
```
