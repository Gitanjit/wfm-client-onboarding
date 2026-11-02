# 0006 — Schedule export layouts

Date: 2025-08-18 · Status: accepted · Author: Mei Lindqvist

## Context

Clients load the weekly schedule into their own workforce tools as the baseline for the coming week.
Until now each export was produced by hand from `out/<client>/schedule.csv`, in whatever shape the
client's tool imports. The shapes in use reduce to three: one row per activity with local times; one
row per agent with a column per day; and a JSON document for tools that import through an API.

## Decision

- Exporters live in `wfm/export/`, one module per layout, behind `python -m wfm export`.
- They read only `out/<client>/schedule.csv` and the client config (for the timezone). They never call
  the planning code, so an exporter cannot change a schedule.
- Local times are computed per row from the client's timezone. A layout that has room for it carries
  the UTC offset of each row.
- Layouts: `activity_csv`, `roster_grid_csv`, `segments_json`, and `agent_ics` (one calendar file
  per agent, for agents who keep their shifts in their own calendars). Output goes to
  `out/<client>/export/`, sorted, so two exports of the same schedule are identical.
- The layout a client uses is agreed at onboarding and recorded in its client notes.

## Consequences

- A new client tool means a new module, not changes to the planner.
- Exports are only as fresh as the last `wfm run` for that week. The exporter checks that
  `eval.json` is for the requested week before writing anything.
