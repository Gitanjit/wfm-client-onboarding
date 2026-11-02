# Tailspin Toys

| | |
|---|---|
| Served | 2025-01-13 (2025-W03) to 2025-10-31 (2025-W44); retired |
| Grain / timezone | 30 minutes / Europe/Dublin |
| Operating hours | 07:00–21:00 local, seven days |
| Queues | priority (80 % in 20 s), standard (80 % in 30 s) |
| Config | `configs/tailspin.yaml` (schema 1) |
| Roster | `data/agents/tailspin.csv`, 30 agents (6 part-time) |
| Data | `data/tailspin/week_<ISO>.csv`, converted from Tailspin's local-time export |
| Export layout | `roster_grid_csv` (from 2025-W34) |

## Data

Tailspin's platform exports Irish wall-clock time with the UTC offset on every row. The converter
derives UTC from that offset. Ireland's clocks follow the EU change dates (last Sunday of March and of
October), so the spring week has 334 half-hour intervals and the autumn week 338.

## Weeks worth knowing

- Irish public holidays, each 15–20 % below the surrounding weeks: 2025-W06 (St Brigid's Day),
  2025-W12 (St Patrick's Day), 2025-W17 (Easter Monday), 2025-W19 (May bank holiday), 2025-W23 (June
  bank holiday), 2025-W32 (August bank holiday).
- 2025-W13: spring forward on 30 March, 334 intervals. 2025-W43: fall back on 26 October, 338 intervals.
- 2025-W26: hosted telephony outage on Tuesday 24 June, 15:00–17:00 local without contacts
  (`docs/incidents/2025-07-01-telephony-platform-outage.md`).

## Offboarding

Tailspin did not renew. The contract ended on Friday 31 October 2025. The last drop was 2025-W43,
processed on 27 October; no drop was requested for the final, partial week. Config, roster and data
stay in the repository so that past weeks can be re-run.
