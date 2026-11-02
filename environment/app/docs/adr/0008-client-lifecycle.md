# 0008 — Client lifecycle and the registry

Date: 2026-10-14 · Status: accepted · Author: Tomas Okafor

## Context

Three clients have retired (Tailspin 2025-10-31, Woodgrove 2026-01-16, Adatum 2026-03-27), Proseware
paused at its own request on 2026-08-14, and Northwind is signed for 2026-W44. Status lived in
people's heads and in the weekly ops list. The same questions kept coming back: can a retired client's
files go, should a paused client's drops still be committed, when does a new client's config land.

## Decision

- `clients/registry.yaml` records every client with a status: `live`, `paused`, `retired` or
  `onboarding`, the lifecycle dates, grain, timezone, queues, config schema, export layout and account
  manager. `clients/README.md` is the readable view and is kept in step with it.
- **Retired**: config, roster, data and unit tests stay. No weekly runs. `ended` is the last day served.
- **Paused**: everything stays; no weekly runs; `paused_from` is the first day not served. A restart sets
  the status back to `live` and starts with the next data drop.
- **Onboarding**: an entry with `golive_week`. Config and roster land with the go-live change.
- `python -m wfm clients --check` compares the registry with `configs/`, `data/` and the rosters. An
  onboarding client without a config is reported as pending, not as an error.
- Deleting a client's files needs its own decision record.

## Consequences

- The repository keeps growing with retired clients' data, about 1 MB per client-year at a 30-minute
  grain.
- Schema-1 configs stay supported for as long as a retired client uses one.
- `export` takes the client's layout from the registry when `--layout` is not given.
