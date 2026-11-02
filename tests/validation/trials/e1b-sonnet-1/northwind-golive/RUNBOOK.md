# Northwind weekly reconciliation — 2026-W44

| key | value |
|---|---|
| intervals_in_week | 338 |
| sla_attainment_priority | 1.000 |
| sla_attainment_standard | 1.000 |
| sla_attainment_vip | 0.917 |
| scheduled_hours_total | 1660.0 |
| required_hours_total | 1115.5 |
| understaffed_interval_hours | 15.0 |
| agents_scheduled | 51 |
| files_changed | configs/northwind.yaml, wfm/ingest/loader.py, wfm/staffing/required.py, wfm/scheduler/weekly.py, wfm/evaluate/metrics.py, wfm/report/reconcile.py, wfm/cli.py, clients/registry.yaml, clients/README.md, docs/clients/northwind.md, docs/clients/northwind_handover.md, docs/ARCHITECTURE.md, docs/CHANGELOG.md, tests_unit/test_northwind.py, tests_unit/test_registry.py, tests_unit/test_cli_subcommands.py |

## Handover note

### What changed and why

Northwind needed service levels, rules and a demand layout the service did not support. Everything is opt-in per
client (`configs/northwind.yaml`); `configs/defaults.yaml` and the other clients' configs are untouched, and Contoso,
Fabrikam and Wingtip produce byte-identical `schedule.csv` and `eval.json` to before.

- **Ingest** (`wfm/ingest/loader.py`): the export loader now takes UTC from each row's `utc_offset` (authoritative per
  the export README). W44 contains the fall-back on Sunday 1 November: the 01:00 and 01:30 labels occur twice (CDT then
  CST), the week has 338 intervals (169 h) rather than 336, and a timezone lookup of the label cannot resolve the
  repeated hour. The queue set comes from the config (`queues`), so `vip` is no longer dropped. Off-grid labels are
  snapped to the nearest slot. **Odd rows to raise with Northwind's WFM contact:** W44 has two rows stamped `10:01`
  (2026-10-27 `priority`, 2026-10-29 `standard`) with no `10:00` row for that queue beside them; we treated them as the
  10:00 intervals. Otherwise no gaps, duplicates, negative volumes or volume outside operating hours (vip only
  08:00-20:00) in W42-W44.
- **Staffing** (`wfm/staffing/required.py`): the occupancy cap (SOW 1.3) is applied (`enforce_occupancy_cap`) and
  `aht_smoothing: interval` now really uses each interval's own handle time (SOW 1.2). SLA targets per queue are 90/30,
  80/20 and 90/20 from the SOW, set in the client config.
- **Scheduler** (`wfm/scheduler/weekly.py`, `scheduler: weekly`): a week-aware planner that enforces the rules while
  placing: 11 h rest (elapsed, both neighbours), split shifts only for PT, weekly caps in elapsed hours, at most five
  consecutive local days, skills, the one-vip-agent floor 06:00-24:00 (counted on `vip` itself, no cross-skill credit),
  and one 20-minute break per shift of six hours or more in the 2-5 h window at the interval with the largest gross
  surplus on the queue. A greedy day-by-day base plan is repaired and improved by local search and a seeded annealing
  pass (fixed seed, deterministic) against the attainment net of those breaks, within the 1.57 x required-hours budget.
  `greedy_v2.py` (WFM-231 draft) was not used: its rest test is inverted and it has no break or floor logic.
- **Evaluator** (`wfm/evaluate/metrics.py`): for Northwind, attainment is over every operating interval (vip 08:00-20:00),
  and `eval.json` also reports rest, split-shift and break violations, `required_hours`, `hours_ratio` and whether the
  schedule is inside the hours budget.
- **Reporting** (`wfm/report/reconcile.py`): every Northwind run writes `RUNBOOK.md` (SOW 3 table) and `exceptions.md`
  (SOW 2.7) beside the schedule, from that run's evaluation.

### Pre-existing deviations from the SOW 1 method (SOW 2.8)

These existed in the service before this change and would have affected Northwind's queues; they are now
overridden for Northwind only. They are **still in force for the other clients**.

1. **WFM-212, occupancy cap never applied.** `occupancy_cap` is read from config but not passed to the Erlang C
   requirement, so required staffing ignored the 0.85 limit. Open for Contoso, Fabrikam and Wingtip.
2. **WFM-198, smoothed handle time.** Requirements use the queue's mean AHT, not the interval's own AHT (SOW 1.2).
   Worse, `aht_smoothing: interval` was not honoured: the code collapsed it to the queue mean as well.
3. **Service-default targets.** Priority/standard default to 80/20 and there is no `vip` queue; the loader dropped any
   queue other than priority and standard.
4. **Attainment counted volume intervals only.** The evaluator ignored intervals without volume and a `coverage` basis
   exists for Fabrikam; SOW 1.6 counts every operating interval and the `service_level` rule.
5. **Greedy scheduler rules.** Breaks at the shift midpoint (not the max-surplus interval), no rest rule, split
   templates open to FT, and 0.5 cross-skill credit toward floors; none match SOW 2.1-2.3 and 2.6.
6. **Export loader and DST.** `tz_localize` on the wall-clock label fails on, or misplaces, the repeated hour at the
   November fall-back; the offsets column was ignored.

Not touched and not affecting Northwind: Fabrikam's qlib abandonment model and `coverage` basis, and Contoso's
temporary `sla_target` override (WFM-212 follow-up).

### Open item for the account team

`vip` cannot reach the 0.95 weekly target with the roster provided; see `exceptions.md`. Eleven agents hold the vip
skill (NW-041..051, all FT, capped at 40 h), and covering every vip interval needs more hours than their caps allow,
before shift shapes, breaks and the 06:00-24:00 floor. As a guide, covering all but 8 vip intervals (0.95) in W44 needs
roughly 30 more vip agent-hours than the 440 h available, i.e. at least one more full-time vip-skilled agent, and
covering every interval needs about 95 more (two to three). `priority` and `standard` meet target at 1.000 and hours are
inside the 1.57 x budget.
