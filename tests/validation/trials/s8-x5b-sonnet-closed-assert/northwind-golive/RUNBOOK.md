# Northwind weekly reconciliation, 2026-W44

| key | value |
|---|---|
| intervals_in_week | 338 |
| sla_attainment_priority | 1.000 |
| sla_attainment_standard | 1.000 |
| sla_attainment_vip | 0.917 |
| scheduled_hours_total | 1660.0 |
| required_hours_total | 1115.5 |
| understaffed_interval_hours | 15.5 |
| agents_scheduled | 51 |
| files_changed | clients/README.md, clients/registry.yaml, configs/defaults.yaml, configs/northwind.yaml, docs/ARCHITECTURE.md, docs/CHANGELOG.md, docs/clients/northwind.md, tests_unit/test_cli_subcommands.py, tests_unit/test_northwind.py, tests_unit/test_registry.py, wfm/cli.py, wfm/config.py, wfm/constraints.py, wfm/evaluate/metrics.py, wfm/ingest/loader.py, wfm/report/sow.py, wfm/scheduler/weekly.py, wfm/staffing/required.py |

## Handover note

Week 2026-W44. Scheduled 1660.0 h against 1115.5 required h
(ratio 1.488; SOW 1.6 allows 1.57). Rule violations in `eval.json`: 0.

### What changed, and why

Northwind could not be run on the service as it stood, so the service learned the following. Everything
is opt-in per client through `configs/northwind.yaml`; `configs/defaults.yaml` only gained the new keys at
their old behaviour, so Contoso, Fabrikam and Wingtip produce the same output as before.

- **Ingest** (`wfm/ingest/loader.py`): the export's `utc_offset` is used to get UTC (the old path
  localised the wall-clock label, which fails on the repeated 01:00-02:00 of a fall-back day: 2026-W44 has
  169 h and 338 intervals). The week's grid comes from the calendar (`calendar_grid`), the queues come from
  config (`queues`, so `vip` is read; it was silently dropped), and rows outside the week, missing rows,
  duplicates and rows off the 30-minute boundary are reported on stderr.
- **Staffing** (`wfm/staffing/required.py`): the 0.85 occupancy cap is applied (`apply_occupancy_cap`,
  WFM-212) and each interval is staffed on its own handle time (`aht_smoothing: interval`; the old
  `interval` mode averaged it away anyway). Targets per queue are the SOW's (priority 90/30, standard 80/20,
  vip 90/20), in the client file.
- **Scheduler** (`wfm/scheduler/weekly.py`, selected by `scheduler: weekly`; this finishes the WFM-231 draft,
  `greedy_v2.py`, which stays unwired): week-aware rest (11 h elapsed), split shifts for PT only, elapsed-time
  weekly caps, breaks placed by the SOW 2.3 rule (largest gross surplus in the 2-5 h window, ties spread)
  and planning on coverage net of breaks; one agent counts once, on the queue they are scheduled on
  (`cross_skill_weight: 0`) and `vip` has one agent in every interval 06:00-24:00 (`min_cover`).
  The plan is chosen cell by cell (queue, day) within the 1.57 hours bound and what the roster can give, then
  people are assigned and improved by local search.
- **Evaluator** (`wfm/evaluate/metrics.py`): attainment over every operating interval (vip 08:00-20:00),
  `sla_target` 0.95, and audits for rest, split shifts and breaks where the contract sets them.
- **Reports** (`wfm/report/sow.py`): this file and `exceptions.md`, recomputed from `schedule.csv` on each run.

### SOW 2.8: pre-existing deviations from the section 1 method that touch Northwind's queues

1. WFM-212: the occupancy cap was read but not applied in required staffing (SOW 1.3). Fixed for Northwind;
   still open for the other clients.
2. WFM-198: required staffing used the queue's mean handle time, not the interval's own (SOW 1.2). Off for
   Northwind (`aht_smoothing: interval`); and the old `interval` mode collapsed to the mean as well.
3. The service defaults are 80/20 on two queues and `sla_target` 0.90; Northwind's targets differ and `vip`
   did not exist. Set in `configs/northwind.yaml`; defaults untouched.
4. The evaluator counted only intervals with volume as the attainment denominator and took one `sla_target`
   for all queues; SOW 1.6 counts every operating interval. Changed for Northwind only.
5. The loader localised wall-clock labels (ambiguous at fall-back), used the delivered grid rather than the
   calendar, and read only `priority` and `standard`.
6. Minimum-cover credit: an agent on another queue counted 0.5 toward a floor (PR #31); the SOW counts a person
   once. `cross_skill_weight: 0` for Northwind.
7. The greedy scheduler places day by day, with no rest rule, split shifts for any contract, breaks at the shift
   midpoint and coverage counted gross of breaks. Replaced for Northwind by `weekly`.
8. Not applicable to Northwind: Fabrikam's `qlib` abandonment model and `attainment_basis: coverage` (PR #47)
   are not used; Erlang C without abandonment is.

### Data and roster findings

- Export 2026-W44: 2 row(s) are not on a 30-minute boundary (`2026-10-27 10:01 priority`; `2026-10-29 10:01 standard`); each was taken as the interval it falls in. Please confirm with Northwind's WFM contact.
- The roster note says every section 1 target is reachable. Checked against this schedule:

- `vip`: attainment 0.917 against 0.95. The agents who hold the `vip` skill can work at most 440 h a week between them (weekly caps); the schedule uses 436.0 h of that for the queue. This is the best the search found within the roster and the SOW rules; more `vip`-skilled agents (or cross-skilling) are needed to reach the target. To be raised with the account team (SOW 2.7); see `exceptions.md`.
