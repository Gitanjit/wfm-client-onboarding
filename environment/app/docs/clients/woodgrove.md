# Woodgrove Bank

| | |
|---|---|
| Served | 2025-05-12 (2025-W20) to 2026-01-16 (2026-W03); retired |
| Grain / timezone | 30 minutes / America/Los_Angeles |
| Operating hours | 06:00–21:00 local, seven days |
| Queues | priority (90 % in 30 s), standard (80 % in 20 s) |
| Config | `configs/woodgrove.yaml` (schema 1) |
| Roster | `data/agents/woodgrove.csv`, 40 agents (8 part-time) |
| Data | `data/woodgrove/week_<ISO>.csv`, converted from Woodgrove's local-time export |
| Export layout | `activity_csv` (from 2025-W34) |

## Data

Woodgrove's platform exports Pacific wall-clock time without an offset column. The converter takes
each row's offset from the timezone database and resolves the repeated autumn hour by row order (see
the 2025-W44 incident). The autumn DST week has 338 half-hour intervals.

## Weeks worth knowing

- US public holidays: 2025-W22 (Memorial Day), 2025-W27 (Independence Day), 2025-W48 (Thanksgiving),
  2025-W52 and 2026-W01 (Christmas, New Year).
- 2025-W26: hosted telephony outage on Tuesday 24 June, 07:00–09:00 local without contacts
  (`docs/incidents/2025-07-01-telephony-platform-outage.md`).
- 2025-W44: fall back on 2 November. First converted an hour off, re-cut with 338 intervals
  (`docs/incidents/2025-11-05-woodgrove-dst-fall-back-ingest.md`).

## Offboarding

Woodgrove consolidated its contact centre into another site. The contract ended on Friday 16 January
2026; the last week planned was 2026-W03. Config, roster and data stay in the repository so that past
weeks can be re-run.
