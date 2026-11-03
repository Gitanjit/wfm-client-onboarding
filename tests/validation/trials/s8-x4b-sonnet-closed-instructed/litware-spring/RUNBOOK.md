# Litware weekly reconciliation - 2027-W11

| key | value |
|---|---|
| intervals_in_week | 504 |
| sla_attainment_priority | 0.997 |
| sla_attainment_standard | 1.000 |
| sla_attainment_email | 1.000 |
| scheduled_hours_total | 760.0 |
| required_hours_total | 527.0 |
| understaffed_interval_hours | 0.3 |
| agents_scheduled | 24 |
| exception_intervals | 42 |
| files_changed | configs/litware.yaml, wfm/cli.py, wfm/constraints.py, wfm/ingest/loader.py, wfm/scheduler/weekly.py, wfm/evaluate/sow.py, wfm/report/runbook.py, clients/registry.yaml, clients/README.md, docs/ARCHITECTURE.md, docs/CHANGELOG.md, docs/clients/litware.md, tests_unit/test_litware.py, tests_unit/test_cli_subcommands.py, tests_unit/test_registry.py |

## Exceptions

- email 2027-03-15T07:00:00Z
- email 2027-03-15T07:20:00Z
- email 2027-03-15T07:40:00Z
- email 2027-03-15T08:00:00Z
- email 2027-03-15T08:20:00Z
- email 2027-03-15T08:40:00Z
- email 2027-03-16T07:00:00Z
- email 2027-03-16T07:20:00Z
- email 2027-03-16T07:40:00Z
- email 2027-03-16T08:00:00Z
- email 2027-03-16T08:20:00Z
- email 2027-03-16T08:40:00Z
- email 2027-03-17T07:00:00Z
- email 2027-03-17T07:20:00Z
- email 2027-03-17T07:40:00Z
- email 2027-03-17T08:00:00Z
- email 2027-03-17T08:20:00Z
- email 2027-03-17T08:40:00Z
- email 2027-03-18T07:00:00Z
- email 2027-03-18T07:20:00Z
- email 2027-03-18T07:40:00Z
- email 2027-03-18T08:00:00Z
- email 2027-03-18T08:20:00Z
- email 2027-03-18T08:40:00Z
- email 2027-03-19T07:00:00Z
- email 2027-03-19T07:20:00Z
- email 2027-03-19T07:40:00Z
- email 2027-03-19T08:00:00Z
- email 2027-03-19T08:20:00Z
- email 2027-03-19T08:40:00Z
- email 2027-03-20T07:00:00Z
- email 2027-03-20T07:20:00Z
- email 2027-03-20T07:40:00Z
- email 2027-03-20T08:00:00Z
- email 2027-03-20T08:20:00Z
- email 2027-03-20T08:40:00Z
- email 2027-03-21T07:00:00Z
- email 2027-03-21T07:20:00Z
- email 2027-03-21T07:40:00Z
- email 2027-03-21T08:00:00Z
- email 2027-03-21T08:20:00Z
- email 2027-03-21T08:40:00Z

## Handover note

This week: 42 interval(s) are listed under Exceptions (SOW §2.6): email demand before 09:00 local cannot be staffed under the earliest-start rule (§2.5). efficiency 760.0 h scheduled against 1.45 x 527.0 h required (ratio 1.442); rule violations 0.

### What changed and why (Litware, go-live 2027-W11)

Litware (Europe/London, 20-minute grain, queues priority / standard / email) is onboarded with its own
configuration plus opt-in switches, so service defaults and every other client's run are unchanged
(Contoso, Fabrikam, Wingtip and Northwind produce the same schedules as before).

- `configs/litware.yaml`: SOW §1 targets (priority 90/30, standard 80/30, email 80/300), occupancy cap 0.85
  applied, the interval's own handle time, 20-minute grain, operating hours 07:00-21:00 London (email
  07:00-19:00), the earliest email start (09:00), the priority floor of two agents on shift with breaks
  aside, efficiency bound 1.45, attainment floor 0.95, rest 11 h, split shifts for part-time only.
- `wfm/ingest/loader.py`: Litware's export stamps each row with the END of its interval
  (`interval_end_local`). The loader now recognises that column and takes the interval start as the row's
  UTC time (label plus the row's own `utc_offset`) minus 20 minutes, so a clock change cannot misplace
  a row. Read as start-stamped, all demand would sit 20 minutes late (and the column name was not known).
- `wfm/constraints.py`, `wfm/scheduler/weekly.py`: per-queue earliest start (`queue_earliest`, email 09:00,
  SOW §2.5); intervals the rule makes impossible (email demand before 09:00) are left out of the plan and
  listed under Exceptions (§2.6), not covered by breaking the rule; floors can be counted on shift, breaks
  aside (`min_cover_basis: gross`, SOW §2.4) where Northwind counts them net of breaks (unchanged).
- `wfm/evaluate/sow.py`: attainment, understaffed hours and the exception list leave the §2.6 intervals out
  of the denominators as SOW §1.6 says; the audit also checks the earliest-start rule and the gross floor.
  eval.json and this report come from the same evaluation of the written schedule.
- `wfm/report/runbook.py`, `wfm/cli.py`: this report in SOW §3 layout, plus `exceptions.md` (§2.7).
- Registry, docs, `tests_unit/test_litware.py` and the registry/CLI tests are updated for the new client.

### Pre-existing deviations from the SOW §1 method that affect Litware's queues (SOW §2.8)

1. Occupancy cap (WFM-212): the service reads `occupancy_cap` but does not apply it in staffing for clients
   that have not opted in. Litware opts in (`enforce_occupancy_cap`); WFM-212 stays open for Contoso, Fabrikam
   and Wingtip. For this week, left as the service default it would change the requirement in 0 queue-interval(s) (+0.0 required agent-hours).
2. Handle time (WFM-198): staffing uses the queue's mean handle time rather than the interval's own, which
   SOW §1.2 requires. Litware uses `aht_smoothing: interval`; the others keep the smoothed value. For this week, left as the service default it would change the requirement in 48 queue-interval(s) (-2.7 required agent-hours).
3. Loader: assumes the export stamps the interval START and has no `interval_end_local` column; its queue
   list was a constant (priority, standard) and silently dropped `email`; the week was built from the rows
   delivered rather than the calendar. All three are handled for Litware by its config (`queues`,
   `full_week_grid`) and the end-stamp support above.
4. Service defaults differ from the SOW (15-minute grain, UTC, hours 06:00-24:00, 80/20 for priority and
   standard, no email target, verdict at 0.90); Litware's file states the SOW values explicitly.
5. Legacy evaluator: attainment over intervals with volume only, no per-queue operating window, breaks not
   netted off, and Fabrikam's coverage basis (PR #47) for some clients. Litware is evaluated on the SOW
   definition (every operating interval of the queue, net of breaks, Erlang C at the interval's own AHT and
   volume, §2.6 intervals left out). The coverage basis is not used for any Litware queue.
6. Legacy `greedy.py` plans each day alone: no rest rule, split shifts offered to full-time agents, breaks
   at the shift midpoint instead of the largest-surplus interval, cross-skilled agents counted at 0.5 toward
   floors. Litware uses none of it (`scheduler: weekly`). `greedy_v2.py` (WFM-231) is not used: its rest
   check is inverted.
7. Queueing is the service's Erlang C (`wfm/staffing/erlang.py`, no abandonment) as SOW §1.2 says; the
   vendored `qlib` abandonment model is not used.
8. Rest and consecutive-day counts are not carried across planning weeks (each ISO week is planned alone).

No target is missed this week (§2.7): `exceptions.md` lists none.
