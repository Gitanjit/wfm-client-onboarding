# 0004 — Per-client configuration overlay

Date: 2025-03-05 · Status: accepted · Author: Tomas Okafor

## Context

Contoso runs on the service defaults. Tailspin, live since January, needs a 30-minute grain,
Europe/Dublin, 07:00–21:00 and its own standard-queue target. Adatum, signed for March, needs an hourly
grain and America/Denver. Client differences need a home that cannot change another client's plan.

## Decision

- `configs/defaults.yaml` holds the service-wide settings.
- `configs/<client>.yaml` overrides top-level keys for that client only. A nested value (`sla`,
  `weekly_hours`, `break`) is replaced whole, not merged key by key.
- The file name is the client key. The CLI refuses a client without a config file.
- The defaults are not changed to suit one client. Every client without an override inherits them.

## Consequences

- Adding a client means a config file, a roster and a data directory.
- A client that overrides one queue's target restates the other queue's too.
- Code reads settings from the merged config only, never from `defaults.yaml` directly.
