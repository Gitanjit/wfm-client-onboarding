# Northwind Traders — weekly reconciliation, 2026-W44

| key | value |
|---|---|
| intervals_in_week | 338 |
| sla_attainment_priority | 1.000 |
| sla_attainment_standard | 1.000 |
| sla_attainment_vip | 0.917 |
| scheduled_hours_total | 1708.0 |
| required_hours_total | 1115.5 |
| understaffed_interval_hours | 15.5 |
| agents_scheduled | 51 |
| files_changed | clients/README.md, clients/registry.yaml, configs/northwind.yaml, docs/ARCHITECTURE.md, docs/CHANGELOG.md, docs/clients/northwind.md, docs/clients/northwind_handover.md, tests_unit/test_cli_subcommands.py, tests_unit/test_northwind.py, tests_unit/test_registry.py, wfm/cli.py, wfm/evaluate/metrics.py, wfm/hours.py, wfm/ingest/loader.py, wfm/report/reconciliation.py, wfm/scheduler/week.py, wfm/staffing/required.py |

## Handover note

### What changed and why

Northwind is the first client whose contract (`docs/NORTHWIND_SOW.md`) defines service level, rules
and costs more strictly than the service did. Everything Northwind-specific is switched on in
`configs/northwind.yaml`; `configs/defaults.yaml` and the live clients' configs are untouched, and
Contoso, Fabrikam and Wingtip produce byte-identical `schedule.csv` and `eval.json` before and after.

- **Ingest** (`wfm/ingest/loader.py`). Queues come from the client config (`queues`); the loader
  used to hard-code `priority, standard` and silently drop `vip`. For exports with a `utc_offset`
  column, UTC is derived from the row's offset (SOW §1.5, `data/northwind/README.txt`), not by
  localising the wall-clock label: on the fall-back night (Sun 2026-11-01) the two 01:00 hours are
  told apart by their offsets. The grid is the full ISO week in local time, elapsed (2026-W44 has 338
  half-hours, not 336), and missing rows, rows outside the week and off-grid timestamps are reported.
- **Staffing** (`wfm/staffing/required.py`, new `wfm/hours.py`). `aht_smoothing: interval` now really
  uses each interval's own AHT (it used to fall through to the queue mean). `enforce_occupancy_cap:
  true` applies the 0.85 cap (WFM-212, opt-in). `operating_hours_strict` + `queue_hours: {vip: [8, 20]}`:
  no staff required outside a queue's operating intervals (SOW §1.4).
- **Scheduler** (new `wfm/scheduler/week.py`, `scheduler: week`). Week-aware placement with 11 h elapsed
  rest (§2.1), split templates for PT only (§2.2), breaks in the 2–5 h window at the interval of largest
  gross surplus (§2.3), the standard rules (§2.4), ARCHITECTURE templates only (§2.5) and the vip floor
  (§2.6), with cover counted net of breaks and each person once, on their own queue. Construction is
  greedy, then pruning, a hill-climb and a seeded simulated-annealing pass (deterministic; about 30 s a
  week) that minimise intervals short, then hours, under the §1.6 bound as a hard limit.
  `greedy.py` (all other clients) and the WFM-231 draft `greedy_v2.py` are unchanged.
- **Evaluator** (`wfm/evaluate/metrics.py`). `attainment_intervals: operating` uses every operating
  interval of the queue as the denominator (§1.6), and the evaluator audits rest, split shifts and break
  placement for clients that have those rules, plus the vip floor net of breaks (`min_cover_net`).
  `eval.json` also carries `required_hours`, `hours_ratio` and `meets_hours_bound` for Northwind.
- **Reconciliation** (new `wfm/report/reconciliation.py`). Every Northwind run writes this RUNBOOK and
  `exceptions.md` next to `eval.json`, recomputed from the run's own required curve and schedule.
- Registry/docs: `config_schema: 1` for Northwind (status stays `onboarding` until the account team
  moves it to live), client note `docs/clients/northwind.md`, ARCHITECTURE and CHANGELOG, unit tests.

Choices worth knowing:

- Break window: a break may start from 2 h up to and including 5 h after shift start, at the start of
  the 30-minute interval chosen. Among tied intervals (the SOW allows any) the scheduler prefers one
  strictly inside the window, then the one with the most net cover to spare. It also avoids weeks where
  a break can only go exactly at +5 h, so nearly every break (all but about 5 a week) holds even if the
  window is read as ending before 5 h. In 2026-W42 this costs one vip interval.
- §2.6 "breaks aside": the floor is kept **net** of breaks (at least one vip agent not on break in every
  06:00–24:00 interval), which satisfies the rule on either reading.
- S44 (the split template) is not used for Northwind. The rule that only PT agents may get it is
  enforced all the same (`split_shift_contracts: [PT]`). S44 adds nothing on `vip`, where the shortfall
  is, because there are no PT vip agents.
- Data: the 2026-W44 export has two rows stamped `10:01` instead of `10:00` (2026-10-27 priority,
  2026-10-29 standard). They are assigned to the 10:00 interval they fall in. Please raise the
  discrepancy with Northwind's WFM contact, as `data/northwind/README.txt` asks.

### Target not met (SOW §2.7): vip attainment

`vip` can be served only by the 11 agents holding the skill: 7 FT `vip` and 4 FT `priority;vip`.
There are no PT vip agents. That is at most 11 × 5 days = 55 shifts and 11 × 40 h = 440 h a week.
The week needs about 348 net agent-hours on vip: 306 h required in the 08:00–20:00 operating
intervals, peaking at 6–7 agents mid-morning and mid-afternoon, plus the §2.6 floor from 06:00 to 08:00
and from 20:00 to 24:00. Covering that curve needs 8-hour blocks starting no earlier than 06:00, gross
cover above need at every break, and the 11 h rest rule, and 440 h is not enough. The schedule uses
all 440 h available. All 11 vip agents work vip only. In 2026-W44 the 14 intervals still short
are mostly the 08:00–09:00 ramp-up, before the 09:00 shifts start, plus one 15:00 peak. A per-day
enumeration of template mixes under the same break rule gives the same picture (0.89–0.91 for W42–W44).
The schedules reach 0.893, 0.917 and 0.917. Weekly vip attainment of 0.95 needs roughly one
or two more vip-skilled agents (or vip skills for some PT agents). Priority and standard meet their
targets at 1.000.

### SOW §2.8: pre-existing deviations from the §1 method that affect Northwind's queues

These existed in the service before this change. Each is corrected for Northwind as noted, but the
service defaults and the other clients still behave this way:

1. **Occupancy cap not applied (WFM-212, open).** `occupancy_cap` (0.85 by default) is read but not
   passed to the staffing model, so required agents ignore §1.3. Northwind sets
   `enforce_occupancy_cap: true`. The cap did not bind in 2026-W42 to W44, but is applied every week.
2. **Smoothed handle time (WFM-198).** Required staffing uses the queue's mean AHT
   (`aht_smoothing: queue_mean`), not each interval's own AHT as §1.2 requires, and
   `aht_smoothing: interval` was silently ignored (code fixed). Northwind uses `interval`.
3. **Attainment denominator.** The evaluator counted only intervals with volume. §1.6 counts every
   operating interval (06:00–24:00, vip 08:00–20:00). Northwind uses `attainment_intervals: operating`.
4. **Cross-skilled cover (PR #31).** Toward a minimum-cover floor, an agent on another queue holding
   the skill counts 0.5, and floors were checked gross of breaks. §1.2 counts a person once, on the queue
   they are scheduled on. Northwind sets `cross_skill_weight: 0` and `min_cover_net: true`.
5. **Ingest.** The loader dropped every queue other than priority and standard (vip would have been
   unstaffed and unreported). It ignored `utc_offset` and placed wall-clock labels in the configured
   timezone, which mislabels or rejects the repeated 01:00 hour on the fall-back night (§1.5). Fixed
   in code for exports with a `utc_offset` column.
6. **Operating hours.** Required staffing was computed for any interval with volume, inside operating
   hours or not, against §1.4. Northwind sets `operating_hours_strict: true` with vip hours 08:00–20:00.
7. **Breaks at the shift midpoint and no rest rule** (`greedy.py`) are §2 matters rather than §1, but
   they change net cover and so the measured service level. Northwind uses `scheduler: week`.

Not affecting Northwind: the vendored abandonment model (`queueing: qlib`) and
`attainment_basis: coverage` are Fabrikam's only. Contoso's `sla_target: 0.72` is a temporary evaluator
threshold tied to WFM-212. None of them is set for Northwind. The rest check in the WFM-231 draft
(`greedy_v2._rested`) is inverted. The draft is not wired in and Northwind does not use it.
