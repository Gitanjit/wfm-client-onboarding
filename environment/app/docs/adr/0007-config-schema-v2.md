# 0007 — Client config schema 2

Date: 2025-11-10 · Status: accepted · Author: Tomas Okafor

## Context

Flat client files (0004) mix planning grain, service targets and contract rules in one list of keys.
Proseware's onboarding sheet arrives in sections (service hours, targets, working-time rules) and maps
onto those keys badly. A typo in a flat file (`operating_hour:`) is silently ignored and the client
gets the default.

## Decision

Schema 2 groups the same keys into four sections. A file declares `schema: 2` at the top:

```yaml
schema: 2
name: Proseware
service:                 # grain, timezone, operating hours
  interval_minutes: 30
  tz: Europe/Berlin
  operating_hours: [7, 21]
targets:                 # service-level targets and the evaluator's settings
  sla:
    priority: {target: 0.85, seconds: 20}
    standard: {target: 0.80, seconds: 30}
staffing: {}             # staffing-model settings
scheduling:              # working-time rules
  weekly_hours: {FT: 39, PT: 20}
```

- Keys inside a section are exactly the flat keys; `V2_SECTIONS` in `wfm/config.py` lists which keys
  each section may hold. `load_config` flattens a schema-2 file (`_flatten_v2`) before the overlay, so
  the rest of the service sees flat keys only.
- An unknown section, or a key in the wrong section, stops the run with an error naming it.
- Schema-1 files load exactly as before. Existing clients are not migrated.
- New clients from Proseware on are written in schema 2.

## Consequences

- One flat namespace underneath: a key cannot mean two things in two sections.
- The overlay rule is unchanged: a nested value such as `sla` replaces the default whole.
- Adding a service key means adding it to its section in `V2_SECTIONS`, or schema-2 clients cannot set it.
