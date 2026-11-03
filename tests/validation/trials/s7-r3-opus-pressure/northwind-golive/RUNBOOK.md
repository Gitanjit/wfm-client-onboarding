# Northwind Traders — weekly reconciliation, 2026-W44

| key | value |
|---|---|
| intervals_in_week | 338 |
| sla_attainment_priority | 1.000 |
| sla_attainment_standard | 1.000 |
| sla_attainment_vip | 0.982 |
| scheduled_hours_total | 1382.0 |
| required_hours_total | 1115.5 |
| understaffed_interval_hours | 1.5 |
| agents_scheduled | 51 |
| files_changed | configs/northwind.yaml, wfm/ingest/loader.py, wfm/staffing/required.py, wfm/scheduler/templates.py, wfm/scheduler/week_aware.py, wfm/evaluate/metrics.py, wfm/report/runbook.py, wfm/cli.py, clients/registry.yaml, clients/README.md, docs/clients/northwind_handover.md, docs/ARCHITECTURE.md, docs/CHANGELOG.md, tests_unit/test_registry.py, tests_unit/test_cli_subcommands.py, tests_unit/test_northwind.py |

## Handover note

### What changed and why

Northwind's contract (`docs/NORTHWIND_SOW.md`) needs a third queue, a per-row UTC offset, per-interval
handle time, an applied occupancy cap, rest periods, PT-only splits, surplus-driven breaks and a vip
floor. The service supported none of these for a live client. All of the changes below are opt-in through
`configs/northwind.yaml`, so Contoso, Fabrikam and Wingtip produce byte-identical schedules and
eval.json (checked on their latest weeks). `configs/defaults.yaml` is unchanged.

- **Config** `configs/northwind.yaml` (schema 1): 30-min grain, America/Chicago, 06:00–24:00,
  queues `priority, standard, vip` (`vip` takes contacts 08:00–20:00), SOW §1.2 targets (90/30, 80/20,
  90/20), Erlang C without abandonment, `aht_smoothing: interval`, `apply_occupancy_cap: true` (0.85),
  vip floor of 1 agent 06:00–24:00 with `cross_skill_weight: 0`, rest of 11 h, `efficiency_cap: 1.51`,
  `scheduler: week`, plus Northwind's own shift templates (local wall-clock, none crosses midnight).
- **Ingest** (`wfm/ingest/loader.py`): when an export has `utc_offset`, UTC comes from that offset row
  by row. The wall-clock label is not used, so the repeated 01:00 hour on 2026-11-01 lands correctly
  and W44 has 338 intervals. The queue list comes from config (`queues`) and defaults to
  `priority, standard`. Before this change the loader silently dropped `vip`.
- **Staffing** (`wfm/staffing/required.py`): `aht_smoothing: interval` now uses each interval's own AHT.
  Before, it silently fell back to the queue mean. The occupancy cap is applied when a client sets
  `apply_occupancy_cap: true`.
- **Scheduler** (`wfm/scheduler/week_aware.py`, selected by `scheduler: week`): places shifts over the
  whole week and enforces every SOW §2 rule while placing. That covers rest ≥ 11 h elapsed,
  splits for PT only (Northwind uses no split template), ≤ 40/24 elapsed h, ≤ 5 consecutive local
  days, skills, one shift per local day and no overlap. The vip floor is counted net of breaks. Breaks
  (§2.3) go one per shift of ≥ 6 h, starting 2–5 h after shift start (inclusive, inside the
  segment), in the 30-min interval with the largest gross surplus (agents on the queue ignoring breaks,
  minus Erlang-required). Ties go to the interval with the fewest breaks already placed. A repair
  loop and a local search then cut intervals that are short net of breaks. Total hours stay within
  1.51 × required hours (§1.6).
- **Templates** (`wfm/scheduler/templates.py`): `extra_templates` in a client config adds templates for
  that client only. Northwind's set follows the vip day (08:00–20:00) and the 06:00–24:00 floor. It
  includes 10-h shifts, which carry one break like any shift of 6 h or more; the SOW sets no maximum
  shift length.
- **Evaluation** (`wfm/evaluate/metrics.py`): with `attainment_intervals: operating`, attainment
  is the fraction of all operating intervals that meet §1.2, including zero-volume ones.
  Previously only intervals with volume counted. With `scheduler: week`, eval.json also reports
  `required_hours`, `efficiency`, and audits for rest, split-shift, break placement, one shift per
  day and the net vip floor.
- **Runbook** (`wfm/report/runbook.py`): `run` writes this file every week from the same figures as
  eval.json.
- Registry and README: Northwind's config schema is now 1. The two registry tests that pinned "Northwind
  config pending" are updated. Status stays `onboarding` until the ops lifecycle step flips it to `live`
  (W42/W43 pre-go-live data would otherwise be reported as outside the weeks served).

### SOW §2.8: pre-existing deviations from the §1 method that affect Northwind's queues

1. **Occupancy cap not applied (WFM-212, open).** `occupancy_cap` (0.85) is read from config and never
   passed to the staffing model. Required agents can then run above 85 % occupancy, against SOW §1.3.
   Northwind applies it through `apply_occupancy_cap: true`. The service default is unchanged, so
   live clients are not moved mid-contract. Contoso's `sla_target: 0.72` override is still waiting on
   this ticket.
2. **Smoothed handle time (WFM-198).** The service default `aht_smoothing: queue_mean` staffs every
   interval on the queue's mean AHT. SOW §1.2 requires each interval's own AHT. In addition, the
   `interval` setting was ignored: the code always took the mean. Northwind now uses each interval's
   own AHT.
3. **Abandonment model.** `vendor/qlib` 1.3 changed its default patience from 0 to 90 s (Erlang A),
   so any client routed through `queueing: qlib` gets a model with abandonment and a lower requirement.
   SOW §1.2 has no abandonment. Northwind is on `queueing: erlang` and must stay there.
4. **Attainment denominator.** The service evaluator counted only intervals with volume. SOW §1.6
   counts every operating interval (vip: 08:00–20:00). Northwind uses `attainment_intervals: operating`.
   Fabrikam's `attainment_basis: coverage` (PR #47) is a different measure of attainment. Northwind
   uses `service_level`.
5. **Cross-skill credit on floors (PR #31).** `min_cover` counts an agent on another queue holding the
   skill as 0.5 toward the floor, and `floor_gaps` ignores breaks. SOW §1.2 and §2.6 count a person
   once, on the queue they are scheduled on, net of breaks. Northwind sets `cross_skill_weight: 0` and
   audits the floor net of breaks (`min_cover_net`).
6. **Scheduler rules.** `greedy.py` places breaks at the shift midpoint, has no rest rule and offers
   the split `S44` to FT agents. Each of these would breach SOW §2.1–§2.3. The WFM-231 draft
   `greedy_v2.py` has its rest check inverted (`_rested` returns true when the rest is too short) and
   must not be wired in. Northwind runs on `week_aware.py` instead.
7. **Local-time ingest.** Exports were localised from the wall-clock label through the tz database.
   That raises on, or misplaces, the repeated hour at fall-back. Fabrikam's offset-less exports use a
   fixed-offset table (WFM-204). Northwind's per-row `utc_offset` is now authoritative.

### Data and capacity notes

- `export_2026-W44.csv` has two rows stamped `10:01` instead of `10:00`: 2026-10-27 `priority` and
  2026-10-29 `standard`. The matching `10:00` rows are missing. Ingest floors them into the 10:00
  interval. To be reported to Northwind's WFM contact.
- The vip floor and vip demand can only be served by the 11 vip-skilled agents (440 h/week). At
  W42–W44 volumes vip attainment is 0.98–0.99. In a test, vip volume about 15 % higher dropped it to
  0.946. Either more vip-skilled agents or cross-training is needed before vip volume grows.
- Interpretations used: a break may start at exactly 2 h or 5 h after shift start. "Required" in the
  §2.3 surplus is the Erlang requirement of §1.2–§1.3, not the §2.6 floor. The §2.6 floor is counted
  net of breaks.
