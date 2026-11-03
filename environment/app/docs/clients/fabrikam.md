# Fabrikam

| | |
|---|---|
| Pilot | from 2025-08-11 (2025-W33) |
| Renewal | signed 2025-10-06, for 12 months |
| Account manager | Ruth Abara |
| Grain / timezone | 60 minutes / America/New_York |
| Operating hours | 06:00–24:00 local, seven days |
| Queues | priority, standard |
| Config | `configs/fabrikam.yaml` (schema 1) |
| Roster | `data/agents/fabrikam.csv`, 28 agents (6 part-time) |
| Data | `data/fabrikam/week_<ISO>.csv`, hourly |
| Export layout | `activity_csv` |

## Config

Hourly grain and US Eastern time. The config sets `queueing: qlib` (the vendored queueing library,
`vendor/qlib`). Operating hours are 06:00–24:00; SLA targets are the
service defaults.

## Timeline

- 2025-08-11: pilot starts with 2025-W33.
- 2025-10-06: renewal signed for 12 months; planning continues without a break.

## Contacts

Ruth Abara (account). Fabrikam's WFM team owns the drop and imports the baseline export.
