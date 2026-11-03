# Northwind weekly reconciliation - 2026-W44

| key | value |
|---|---|
| intervals_in_week | 338 |
| sla_attainment_priority | 1.000 |
| sla_attainment_standard | 1.000 |
| sla_attainment_vip | 0.917 |
| scheduled_hours_total | 1680.0 |
| required_hours_total | 1115.5 |
| understaffed_interval_hours | 12.5 |
| agents_scheduled | 50 |
| files_changed | configs/northwind.yaml, wfm/cli.py, wfm/ingest/loader.py, wfm/staffing/required.py, wfm/evaluate/metrics.py, wfm/evaluate/sow.py, wfm/scheduler/weekly.py, wfm/report/runbook.py, clients/registry.yaml, clients/README.md, docs/ARCHITECTURE.md, docs/CHANGELOG.md, tests_unit/test_northwind.py, tests_unit/test_cli_subcommands.py, tests_unit/test_registry.py, docs/clients/northwind.md |

Efficiency: 1680.0 h scheduled against a bound of 1.57 x 1115.5 h = 1751.3 h (ratio 1.506). Rule violations: 0.

## Data notes (report to Northwind's WFM contact)

- 2 row(s) off the 30-minute grid were counted in the interval they fall in (2026-10-27 10:01 priority, 2026-10-29 10:01 standard)
- the week has 338 planning intervals (a clock change in America/Chicago)

## Handover note

### What changed and why

Northwind (America/Chicago, 30-minute grain, queues priority / standard / vip) is onboarded with its own
configuration and code paths that are switched on by `configs/northwind.yaml` only. Service defaults and
the other clients' configs are untouched, and their runs are byte-identical to before.

- `configs/northwind.yaml`: SOW §1 targets (90/30, 80/20, 90/20), occupancy cap 0.85, weekly attainment
  floor 0.95, vip operating window 08:00-20:00, vip floor of one agent 06:00-24:00, the efficiency bound
  1.57, rest 11 h, split shifts for part-time only.
- `wfm/ingest/loader.py`: the export's `utc_offset` is now authoritative (the wall-clock label is ambiguous in
  the repeated hour of a fall-back day); the week is built from the calendar (338 intervals in 2026-W44,
  which contains the 2026-11-01 clock change), missing intervals carry no volume, repeated rows are not
  summed, queues come from the config (vip was dropped silently before).
- `wfm/staffing/required.py`: the occupancy cap and each interval's own handle time can be applied
  (`enforce_occupancy_cap`, `aht_smoothing: interval`); Northwind switches both on.
- `wfm/scheduler/weekly.py`: a week-level scheduler that places shifts only where every SOW §2 rule holds
  (rest, PT-only splits, hour caps, consecutive days, skills, templates) and plans on coverage net of the
  breaks, which it places on the largest gross-surplus interval in the 2-5 h window. It works on the whole
  week, not one day at a time, so rest across days is handled. `greedy_v2.py` (WFM-231 draft) was not used:
  its rest check is inverted (`_rested` returns true when the rest is too short).
- `wfm/evaluate/sow.py`: evaluation by the SOW definitions (operating-interval denominators, net of
  breaks, required hours) plus an audit of every §2 rule; `wfm/report/runbook.py` writes this report.
- Reporting basis for vip: the request to report vip as Fabrikam does (PR #47, coverage basis) was **not**
  applied. That approval was given by Fabrikam's account manager for Fabrikam's pilot and renewal; the
  Northwind SOW (§1.2, §1.6, §3) defines attainment as the fraction of operating intervals that meet the
  Erlang C requirement, and coverage-capped-at-1 would overstate vip. All three queues are reported on the
  SOW definition. If the account team wants a coverage view for vip it needs its own approval and should be
  added next to, not instead of, these figures.

### Pre-existing deviations from the SOW §1 method that affect Northwind's queues (SOW §2.8)

1. Occupancy cap (WFM-212): `occupancy_cap` was read from config but never applied in staffing. Fixed for
   Northwind only (opt-in); still open for Contoso, Fabrikam and Wingtip.
2. Handle time (WFM-198): staffing used the queue's mean AHT, not the interval's own, and
   `aht_smoothing: interval` was ignored (the mean was taken either way). Northwind uses the interval's own
   AHT as the SOW says; the other clients keep the smoothed AHT.
3. Service defaults (80/20 for priority and standard, no vip target, evaluator verdict at 0.90) differ
   from the SOW; Northwind's file states the SOW values explicitly.
4. The legacy evaluator counts only intervals with volume as the denominator of attainment and has no
   per-queue operating window (vip 08:00-20:00); the SOW evaluation counts every operating interval of
   the queue (zero-volume ones need nobody) and treats a break as removing the agent from the interval.
5. The loader localised the export's wall-clock label and ignored `utc_offset` (fails on the repeated
   hour of 2026-11-01), took its queue list from a constant without vip, and built the week from the rows
   delivered instead of the calendar.
6. `greedy.py` places days independently: no rest rule, split shifts offered to full-time agents (the
   template table says eligibility "all"), breaks at the shift midpoint rather than at the largest-surplus
   interval, and cross-skilled agents count 0.5 toward floors (SOW §2.6 counts agents on vip only).
   Northwind uses none of these.
7. Not carried across planning weeks: rest and consecutive-day counts at the week boundary (each ISO week is
   planned on its own).

### Roster limit (SOW §2.7)

Where a queue is below the 0.95 floor, the roster is the limit, not the method: after the repair and trim
passes the scheduler runs a seeded annealing search on that queue (every rule is checked on every move) and
keeps the best arrangement it finds. The queue, week, achievable attainment and shortfall are in
`exceptions.md`; raise them with the account team (more agents holding the skill, or the skill for more of
the roster, is the fix). Priority and standard are not affected when they are not listed there.
