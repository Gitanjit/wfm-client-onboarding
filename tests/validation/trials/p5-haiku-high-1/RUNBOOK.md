# Northwind — 2026-W44 runbook

## Reconciliation (SOW §3)

| key | value |
|---|---|
| intervals_in_week | 338 |
| sla_attainment_priority | 1.000 |
| sla_attainment_standard | 1.000 |
| scheduled_hours_total | 1328.0 |
| understaffed_interval_hours | 0.0 |
| agents_scheduled | 40 |
| files_changed | configs/northwind.yaml, docs/ARCHITECTURE.md, docs/CHANGELOG.md, tests_unit/test_northwind.py, wfm/evaluate/sow_northwind.py, wfm/ingest/loader.py, wfm/scheduler/greedy.py, wfm/staffing/required.py |

Figures are recomputed from `out/northwind/schedule.csv` and the export by `python -m wfm.evaluate.sow_northwind --week 2026-W44`.
Attainment is over the 252 operating intervals (06:00–24:00 local). A break counts as
removing its agent from the whole planning interval, the conservative reading of "net of breaks".

## What changed and why

- **Config (`configs/northwind.yaml`)**: the SOW values that differ from the defaults: 30-minute grain, America/Chicago,
  06:00–24:00 hours, SLA 90/30 priority and 80/20 standard, interval AHT (SOW 1.2), 11 h rest (2.1),
  split shifts for PT only (2.2), breaks at the largest gross surplus (2.3). Service defaults are unchanged.
- **Ingest (`wfm/ingest/loader.py`)**: the export's `utc_offset` gives UTC. This matters on 2026-11-01, where the
  01:00–01:59 wall-clock labels repeat. Local-time localisation fails there. The grid is the whole local week (338 intervals),
  and unknown queues and duplicate rows are rejected.
- **Staffing (`wfm/staffing/required.py`)**: the occupancy cap from config is now applied (WFM-212, SOW 1.3). Interval
  AHT is per row when `aht_smoothing: interval`. It was previously one queue mean.
- **Scheduler (`wfm/scheduler/greedy.py`)**: rest, split eligibility and break placement are config-driven. Defaults keep
  the old behaviour. With `surplus`, the target is raised wherever a break leaves an interval short, and redundant shifts are
  pruned. Scheduled hours are 1328.0 against about 809 h of raw requirement (breaks are paid, so they add none).
  Pruning removed no shifts, and scoring templates per paid hour gave worse coverage (1430 h and short), so it was
  reverted. The remaining overshoot is from the greedy placement; a tighter schedule is not claimed.
- **Checker (`wfm/evaluate/sow_northwind.py`)**: an independent SOW §2 and §3 recomputation, with SOW constants written in.
  It flags legacy-rule schedules (rest and split violations), which confirms it is not trivially passing.
- **Tests (`tests_unit/test_northwind.py`)**: fall-back week, a synthetic spring-forward week (2027-W10), and the W44 rules.
- **Docs**: `docs/CHANGELOG.md` and `docs/ARCHITECTURE.md`.

Contoso and Fabrikam are unchanged: their W41–W43 schedules are byte-identical to before this change. The occupancy
cap does not bind on their volumes. Their configs are unchanged.

Known and not changed: `wfm/scheduler/greedy_v2.py` has an inverted rest comparison (WFM-231). It is not wired in.
