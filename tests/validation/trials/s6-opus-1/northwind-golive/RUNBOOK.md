# Northwind — weekly reconciliation, 2026-W44

Produced by `cd /app && python -m wfm run --client northwind --week 2026-W44`
(`out/northwind/schedule.csv`, `out/northwind/eval.json`). Figures recomputed from those outputs and the raw
export using the SOW §1 definitions.

| key | value |
|---|---|
| intervals_in_week | 338 |
| sla_attainment_priority | 1.000 |
| sla_attainment_standard | 1.000 |
| sla_attainment_vip | 0.911 |
| scheduled_hours_total | 1682.0 |
| required_hours_total | 1115.5 |
| understaffed_interval_hours | 14.5 |
| agents_scheduled | 51 |
| files_changed | configs/northwind.yaml, wfm/ingest/loader.py, wfm/staffing/required.py, wfm/scheduler/greedy_v2.py, wfm/evaluate/metrics.py, wfm/cli.py, clients/registry.yaml, tests_unit/test_northwind.py, tests_unit/test_registry.py, tests_unit/test_cli_subcommands.py, docs/ARCHITECTURE.md, docs/CHANGELOG.md, out/northwind/RUNBOOK.md, out/northwind/exceptions.md |

Schedule efficiency (SOW §1.6): 1682.0 / 1115.5 = 1.508 ≤ 1.57. The week has 338 intervals because DST ends
on Sun 2026-11-01 (169 elapsed hours). Exceptions (SOW §2.7): `vip` 0.911 against 0.950, see `exceptions.md`.

## Handover note

### What changed and why

All Northwind behaviour sits behind keys in `configs/northwind.yaml`. Each new key defaults in code to what
the service already did, and `configs/defaults.yaml` is untouched. Contoso, Fabrikam and Wingtip produce
byte-identical `schedule.csv` and `eval.json` for 2026-W41 to W43, before and after. Unit tests: 84 pass.

- **Config** `configs/northwind.yaml` (schema 1): 30-min grain, America/Chicago, operating hours 06–24,
  queues priority/standard/vip with `queue_hours: {vip: [8, 20]}`, SOW §1.2 targets (90/30, 80/20, 90/20),
  occupancy cap 0.85 applied, interval AHT, Erlang C (no abandonment), `sla_target: 0.95`,
  `efficiency_bound: 1.57`, VIP cover floor of 1 from 06 to 24 with `cross_skill_weight: 0`, plus §2 rules
  (11 h rest, split shifts PT only, surplus break placement, 40/24 h, 5 days).
- **Ingest** (`wfm/ingest/loader.py`): the loader dropped `vip` (the queues were hardcoded). It localised
  wall-clock labels, which is ambiguous in the repeated 01:00 hour of 2026-11-01. Now the client's
  `queues` are kept, and when a `utc_offset` column is present each row's offset is used, as Northwind's README asks.
  The grid is now the full ISO week in local time, so any other week, DST or not, gets the right interval
  count. Repeated rows and rows outside the week are dropped with a warning.
- **Staffing** (`wfm/staffing/required.py`): `apply_occupancy_cap` lets a client opt in to the cap
  (WFM-212 is still open for the service). `aht_smoothing: interval` used to fall back to the queue mean
  and now really uses each interval's AHT. `staff_operating_hours_only` means no requirement outside a
  queue's operating hours.
- **Scheduler** (`wfm/scheduler/greedy_v2.py`, WFM-231, wired in with `scheduler: week`): the per-day
  greedy has no rest rule, puts breaks at the midpoint, and lets FT agents take S44. So I finished the
  draft. Fixes: the draft's rest check was inverted. Breaks now follow §2.3 (gross surplus). Rules are
  enforced while placing. Passes: greedy over the whole week, repair of net-of-break shortfalls, prune
  of redundant shifts, local search plus seeded simulated annealing on the queue short by most, and
  moving shifts off the break-window edge (see below). Output is deterministic. A run takes about 15 s.
  The scheduled hours stay at or below 0.98 × 1.57 × required hours. Northwind doesn't use the split
  template S44: only PT agents may take it and none of them hold the vip skill. §2.2 holds either way.
- **Evaluator** (`wfm/evaluate/metrics.py`): `attainment_intervals: operating` counts every operating
  interval (vip 08–20), as SOW §1.6 does. `required_hours`, `hours_ratio` and `within_efficiency_bound` are
  added. `rest`, `split_shift` and `breaks` are audited when the client sets those rules.
- **Registry and tests**: `config_schema: 1` for Northwind (status stays `onboarding` until ops flips it;
  W42/W43 data predates go-live). The two "Northwind pending" tests now expect a clean `clients --check`.
  `tests_unit/test_northwind.py` is new.

### SOW §2.8: deviations from the §1 method that affect Northwind's queues

These are service behaviours that predate this change and differ from the SOW §1 method. Each is
overridden for Northwind as noted, and each is still the service default for other clients.

1. **Occupancy cap not applied** (WFM-212, open). `occupancy_cap: 0.85` is read but never used in
   required staffing. Breaches SOW §1.3. Northwind: `apply_occupancy_cap: true`.
2. **Smoothed handle time** (WFM-198, `aht_smoothing: queue_mean`). Required staffing uses the queue's
   mean AHT, not the interval's own AHT, which breaches §1.2. `aht_smoothing: interval` was also broken
   (still averaged); that's fixed, and Northwind uses it.
3. **Attainment counted on intervals with volume only.** The service evaluator skips zero-volume
   intervals, but §1.6 counts every operating interval. Northwind: `attainment_intervals: operating`,
   `queue_hours`.
4. **Cross-skill credit toward floors** (PR #31, `cross_skill_weight: 0.5`). An agent on another queue
   counts half toward a floor, but §1.2 says a person counts once, on their scheduled queue. Northwind: 0.
5. **Hardcoded queues and wall-clock localisation in ingest.** `vip` would have been dropped, and the
   fall-back hour can't be converted. Fixed in code.
6. **Break placement at the shift midpoint and no rest rule** in the default greedy scheduler, and FT
   agents allowed on split shifts (S44 eligibility "all"). Breaches §2.1–§2.3. Northwind uses the week
   scheduler.
7. **Not applicable to Northwind, listed so nobody copies them:** Fabrikam's `queueing: qlib`
   (abandonment, which §1.2 excludes) and `attainment_basis: coverage` (PR #47), and Contoso's temporary
   `sla_target: 0.72`. Northwind is configured with `queueing: erlang` and `attainment_basis: service_level`.

### Interpretation choices and data notes

- **Break window**: a break may start from 2 h up to and including 5 h after shift start. The scheduler
  avoids putting a break on the 5-hour edge when the surplus there is strictly highest, but only where
  that costs no coverage. 9 breaks in W44 still sit there. If Northwind reads the window's end as
  exclusive, those 9 need a decision.
- **VIP cover (§2.6)** holds both gross and net of breaks in every interval from 06:00 to 24:00.
- **Understaffed hours** use agents net of breaks, over every interval of the week.
- **Data issue in `export_2026-W44.csv`, to raise with Northwind's WFM contact**: two rows are stamped
  `10:01` instead of `10:00`, priority on Tue 27 Oct and standard on Thu 29 Oct. They were placed in the
  10:00 interval (floored to the 30-minute grain).
- **Rest across weeks**: §2.1 is enforced within the planning week only, as the SOW states. The previous
  week's last shifts are not carried in.
