# Adatum

| | |
|---|---|
| Served | 2025-03-10 (2025-W11) to 2026-03-27 (2026-W13); retired |
| Grain / timezone | 60 minutes / America/Denver |
| Operating hours | 06:00–24:00 local (service default) |
| Queues | priority, standard (service default targets) |
| Config | `configs/adatum.yaml` (schema 1), the first client written as a config overlay |
| Roster | `data/agents/adatum.csv`, 30 agents (6 part-time) |
| Data | `data/adatum/week_<ISO>.csv`, converted from Adatum's hourly report |
| Export layout | `activity_csv` (from 2025-W34) |

## Data

Adatum's reporting job writes hourly intervals in Mountain time with the offset per row; the converter
derives UTC from it. US DST weeks have 167 (spring) and 169 (autumn) hourly intervals.

## Weeks worth knowing

- US public holidays: 2025-W22 (Memorial Day), 2025-W27 (Independence Day), 2025-W48 (Thanksgiving),
  2025-W52 and 2026-W01 (Christmas, New Year), 2026-W04 (Martin Luther King Jr. Day).
- 2025-W44: fall back on 2 November, 169 intervals. 2026-W10: spring forward on 8 March, 167 intervals.
- 2025-W26: hosted telephony outage on Tuesday 24 June, 08:00–10:00 local without contacts
  (`docs/incidents/2025-07-01-telephony-platform-outage.md`).
- 2026-W04: the drop arrived three days late (`docs/incidents/2026-01-30-adatum-late-data-drop.md`).

## Offboarding

Adatum moved its planning in-house. The contract ended on Friday 27 March 2026; the last week planned
was 2026-W13. Config, roster and data stay in the repository so that past weeks can be re-run.
