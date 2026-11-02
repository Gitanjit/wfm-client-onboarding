# Proseware

| | |
|---|---|
| Onboarded | 2025-11-17 (2025-W47) |
| Paused | from 2026-08-14 at Proseware's request; last week planned 2026-W33 |
| Account manager | Sam Ferreira |
| Grain / timezone | 30 minutes / Europe/Berlin |
| Operating hours | 07:00–21:00 local, seven days |
| Queues | priority (85 % in 20 s), standard (80 % in 30 s) |
| Working time | 39 h full-time, 20 h part-time per week; at most 5 consecutive days |
| Config | `configs/proseware.yaml`, the first schema-2 config |
| Roster | `data/agents/proseware.csv`, 34 agents (7 part-time) |
| Data | `data/proseware/week_<ISO>.csv`, canonical as delivered by Proseware's BI team |
| Export layout | `roster_grid_csv` |

## Data

Proseware's BI team delivers canonical files in UTC on Monday mornings. Germany follows the EU change
dates; the spring week 2026-W13 has 334 half-hour intervals.

## Weeks worth knowing

- Public holidays (Berlin): 2025-W52 (Christmas), 2026-W01 (New Year), 2026-W14 (Good Friday),
  2026-W15 (Easter Monday), 2026-W18 (1 May), 2026-W20 (Ascension Day), 2026-W22 (Whit Monday).
- 2026-W13: spring forward on 29 March, 334 intervals.
- 2026-W16: contact-centre tenant outage on Tuesday 14 April, 15:00–17:30 local without contacts
  (`docs/incidents/2026-04-21-contact-centre-tenant-outage.md`).

## Pause

Proseware paused the service from Friday 14 August 2026 while it reviews its service model. The last
week planned was 2026-W33. Config, roster and data stay as they are; a restart needs the next data
drop and nothing else from us.
