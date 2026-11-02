# 0001 — Canonical interval format

Date: 2024-11-08 · Status: accepted · Author: Dana Vexley

## Context

The service plans from interval demand: contacts arriving per queue per planning interval, with their
average handle time. Every contact-centre platform exports this differently: local or UTC stamps,
interval start or interval end, one file per queue, rows missing where nothing arrived. The planning
code should not need to know any of that.

## Decision

Demand enters the service as one canonical file per client per ISO week,
`data/<client>/week_<YYYY>-W<ww>.csv`:

| column | meaning |
|---|---|
| `client` | client key, the same as the config file name (`contoso`) |
| `queue` | queue name |
| `interval_start_utc` | interval start, ISO 8601 with `Z` |
| `interval_minutes` | the client's planning grain: 15, 30 or 60 |
| `volume` | contacts that arrived in the interval, three decimals |
| `aht_sec` | average handle time of those contacts, seconds, three decimals |

- One row per queue per interval for the whole ISO week in the client's timezone, including intervals
  with no volume. A missing row is a data problem, not a quiet interval.
- Rows are ordered by interval, then queue.
- A zero-volume row carries the queue's base handle time, so that the column has no gaps.
- Converting a client's own export into this layout is part of that client's onboarding and happens
  before the file is committed.

## Consequences

- Ingest reads one layout. Resampling to the client's grain is the only transformation it applies.
- The row count of a week follows from the grain and the timezone: 7 × 24 × 60 / grain rows per queue,
  give or take the DST hour (0002).
- A client whose export cannot be converted mechanically needs its converter described in its client
  notes (`docs/clients/<client>.md`).
