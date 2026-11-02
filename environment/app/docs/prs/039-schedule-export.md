# PR #39 — Schedule exports in the clients' layouts

Merged 2025-08-20 · Author: Mei Lindqvist · WFM-093

## Problem

Each client imports the weekly schedule into its own workforce tool as next week's baseline. The
files were made by hand from `schedule.csv`, in local time, five times a week.

## Change

- `python -m wfm export --client <c> --week <week> --layout <layout>`, writing to
  `out/<client>/export/` (ADR 0006).
- `wfm/export/`: `activity_csv` (one row per work or break activity, local times and offset),
  `roster_grid_csv` (one row per agent, a column per local day), `segments_json` (agents and
  segments for tools that import through an API), `agent_ics` (one iCalendar file per agent).
- Exports read `schedule.csv` and the client config only, and refuse a week whose `eval.json` is
  for another week. Each export has a small manifest beside it (row count, agents, paid hours,
  sha256) for the client to check the import against.

## Approved by

Dana Vexley and Tomas Okafor (review).

## Outcome

From 2025-W34, Contoso, Adatum, Woodgrove and Fabrikam get `activity_csv`, Tailspin
`roster_grid_csv` plus `agent_ics` for its agents' calendars. The first exports matched the
hand-made files for 2025-W33 apart from row order.
