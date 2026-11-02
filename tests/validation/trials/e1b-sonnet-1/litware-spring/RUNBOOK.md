# Litware weekly reconciliation — 2027-W11

| key | value |
|---|---|
| intervals_in_week | 504 |
| sla_attainment_priority | 1.000 |
| sla_attainment_standard | 1.000 |
| sla_attainment_email | 1.000 |
| scheduled_hours_total | 746.0 |
| required_hours_total | 527.0 |
| understaffed_interval_hours | 0.0 |
| agents_scheduled | 24 |
| exception_intervals | 42 |
| files_changed | configs/litware.yaml, wfm/ingest/loader.py, wfm/constraints.py, wfm/scheduler/weekly.py, wfm/evaluate/metrics.py, wfm/report/reconcile.py, clients/registry.yaml, clients/README.md, docs/clients/litware.md, docs/clients/litware_handover.md, docs/ARCHITECTURE.md, docs/CHANGELOG.md, tests_unit/test_litware.py |

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

### What changed and why

Litware needed a demand layout, service levels and rules the service did not support. Everything is opt-in per client
(`configs/litware.yaml`); `configs/defaults.yaml` and the other clients' configs are untouched. Contoso, Fabrikam and
Wingtip produce byte-identical `schedule.csv` and `eval.json` to before, and Northwind's W44 schedule is unchanged.

- **Ingest** (`wfm/ingest/loader.py`): Litware's export stamps every row with the **end** of its interval
  (`interval_end_local`; a row stamped 09:20 covers 09:00-09:20). The loader now takes UTC from each row's `utc_offset`
  (the offset in effect at the end instant, authoritative) and steps back one grain, so demand lands in the right
  20-minute interval, across a fall-back or spring-forward too. Reading the stamps as interval starts would have moved
  all demand 20 minutes late.
- **Configuration** (`configs/litware.yaml`): 20-minute grain, Europe/London, operating hours 07:00-21:00, queues
  `priority`, `standard`, `email`; targets 90/30, 80/30 and 80/300 (SOW 1.2); occupancy cap 0.85 applied; each interval's
  own handle time; Erlang C without abandonment; weekly attainment target 0.95 over every operating interval of each
  queue (07:00-21:00, so email's 19:00-21:00 intervals, which carry no volume and need no staff, count as met); no
  cross-skill credit; hours budget 1.45 x required; two agents on `priority` in every operating interval.
- **Scheduler** (`wfm/scheduler/weekly.py`, reused from Northwind): rest, PT-only splits, caps, five-day limit, breaks at
  the maximum-gross-surplus interval of the 2-5 h window, floors and the hours budget, with Litware's own rules added:
  nobody is scheduled on `email` in a template that starts before 09:00 local (SOW 2.5, `queue_earliest_start`;
  `wfm/constraints.py`), and break ties go to a start strictly inside the window, so the plan does not depend on whether
  the window's ends count (`break.avoid_window_edges`).
- **SOW 2.6 intervals**: an `email` interval that starts before 09:00 and has demand cannot meet its target without
  breaking SOW 2.5. These are listed under `## Exceptions`, left out of attainment and of `understaffed_interval_hours`
  (but not of the week's interval count or required hours), and the planner does not chase them. With the current
  demand that is the 07:00-09:00 `email` intervals, 42 a week.
- **Evaluator** (`wfm/evaluate/metrics.py`): the exception intervals are excluded as above and `eval.json` adds
  `exception_intervals` and `exceptions`. Every figure in `RUNBOOK.md` comes from that evaluation of the written
  `schedule.csv`.
- **Reporting** (`wfm/report/reconcile.py`): the table follows the client's queues, and a client with
  `runbook_exceptions` gets the `exception_intervals` key and the `## Exceptions` section. Northwind's report is unchanged.

### Pre-existing deviations from the SOW 1 method (SOW 2.8)

These were in the service before Litware and would have affected its queues. They are overridden for Litware only by
its config or the ingest change above, and are **still in force for the other clients**.

1. **WFM-212, occupancy cap never applied.** `occupancy_cap` is read from config but was not passed to the Erlang C
   requirement, so required staffing ignored the 0.85 limit (SOW 1.3). Open for Contoso, Fabrikam and Wingtip.
2. **WFM-198, smoothed handle time.** Requirements use the queue's mean AHT, not the interval's own (SOW 1.2);
   `aht_smoothing: interval` was not even honoured until the Northwind change.
3. **Service-default targets and queues.** The defaults are 80/20 for `priority` and `standard`; Litware's are 90/30 and
   80/30, and `email` (80/300) did not exist: the loader dropped any queue other than `priority` and `standard`.
4. **Attainment counted only intervals with volume.** SOW 1.6 counts every operating interval (and leaves out the
   SOW 2.6 ones); the evaluator ignored zero-volume intervals.
5. **Greedy scheduler rules.** Breaks at the shift midpoint (SOW 2.3 wants the maximum-surplus interval), no rest rule,
   split templates open to FT, and 0.5 cross-skill credit toward floors (SOW 1.2 counts a person once, on their queue).
6. **Export loader.** It assumed interval-start stamps and ignored `utc_offset` unless the Northwind change applied;
   a timezone lookup of a local label mis-places the repeated hour at a fall-back.

Not touched and not affecting Litware: Fabrikam's qlib abandonment model and `coverage` basis, and Contoso's temporary
`sla_target` override.

### For the account team

Nothing falls short of SOW 1.6 on the 2027-W10 and 2027-W11 data: all three queues are at attainment 1.000 and hours are
inside the 1.45 x budget. The only intervals not met are the SOW 2.6 `email` ones listed above, which come from the
09:00 start rule, not from the roster; if Litware wants them covered, SOW 2.5 has to change.
