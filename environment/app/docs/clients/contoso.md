# Contoso

| | |
|---|---|
| Live since | 2024-12-02 (2024-W49) |
| Account manager | Sam Ferreira |
| Grain / timezone | 15 minutes / UTC |
| Operating hours | 06:00–24:00 UTC, seven days |
| Queues | priority, standard |
| Config | `configs/contoso.yaml` (schema 1) |
| Roster | `data/agents/contoso.csv`, 40 agents (8 part-time) |
| Data | `data/contoso/week_<ISO>.csv`, canonical as delivered |
| Export layout | `activity_csv` (from 2025-W34) |

## Data drop

Contoso's platform writes the previous week's file to the drop folder on Monday by 07:00 UTC. It is
already in the canonical layout and in UTC, so there is no converter. Contoso was the first client and
the canonical layout (`docs/adr/0001-canonical-interval-format.md`) follows its export closely.

## Queues

Priority and standard throughout. An evening chat queue ran from 2025-07-21 to 2025-09-01: the weeks
2025-W30 to 2025-W35 carry `chat` rows, with volume between 16:00 and 24:00 UTC.

## Weeks worth knowing

- 2024-W52 and 2025-W01: Christmas and New Year. Volume about a quarter (W52) and a fifth (W01)
  below the surrounding weeks.
- 2025-W26: hosted telephony outage on Tuesday 24 June, 13:40–16:20 UTC
  (`docs/incidents/2025-07-01-telephony-platform-outage.md`).

## Contacts

Sam Ferreira (account). Contoso's WFM team owns the drop and imports the baseline export.
