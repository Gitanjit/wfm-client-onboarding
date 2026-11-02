# Wingtip Toys

| | |
|---|---|
| Onboarded | 2026-02-09 (2026-W07) |
| Account manager | Ruth Abara |
| Grain / timezone | 30 minutes / America/Phoenix |
| Operating hours | 06:00–24:00 local, seven days |
| Queues | priority, standard (80 % in 20 s) |
| Working time | 40 h full-time, 30 h part-time per week |
| Config | `configs/wingtip.yaml` (schema 2) |
| Roster | `data/agents/wingtip.csv`, 36 agents (8 part-time) |
| Data | `data/wingtip/week_<ISO>.csv`, canonical as delivered |
| Export layout | `segments_json`, loaded through their workforce tool's import API |

## Time

Arizona does not observe daylight saving time. Wingtip is on UTC−7 all year, so its clock matches
US Pacific time in summer and US Mountain time in winter, and every week has 336 half-hour intervals.

## Data drop

Wingtip's platform writes the previous week's canonical file on Monday by 09:00 UTC. The
`segments_json` export goes back the same day.

## Contacts

Ruth Abara (account). Wingtip's workforce team owns the drop and the import.
