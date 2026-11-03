# Northwind Traders — 2026-W44 runbook

**Status: not ready for the go-live review.** The run completes and every SOW §2 rule except §2.6 holds,
and the efficiency bound (§1.6) is met. Vip does not meet §1.2: vip attainment is 0.685 against a weekly
requirement of 0.95, and vip has no agent on shift in 72 intervals (§2.6), all on Saturday 31 Oct and
Sunday 1 Nov. The cause is in the vip roster and the packing of vip shifts, not in the reconciliation.
See the handover note below.

Week: 2026-W44 (Mon 26 Oct – Sun 1 Nov 2026, America/Chicago; clocks went back at 02:00 on Sunday 1 Nov).
Run: `python -m wfm run --client northwind --week 2026-W44` → `out/northwind/schedule.csv`, `out/northwind/eval.json`.

## Reconciliation (SOW §3)

| key | value |
|---|---|
| intervals_in_week | 338 |
| sla_attainment_priority | 0.968 |
| sla_attainment_standard | 0.964 |
| sla_attainment_vip | 0.685 |
| scheduled_hours_total | 1638.0 |
| required_hours_total | 1115.5 |
| understaffed_interval_hours | 85.0 |
| agents_scheduled | 51 |
| files_changed | clients/README.md, clients/registry.yaml, configs/defaults.yaml, configs/northwind.yaml, tests_unit/test_cli_subcommands.py, tests_unit/test_registry.py, wfm/config.py, wfm/evaluate/metrics.py, wfm/ingest/loader.py, wfm/scheduler/greedy.py, wfm/staffing/required.py |

Definitions used (SOW §1–§3): an interval meets §1.2 when agents scheduled on the queue, net of breaks, are at
least the Erlang C requirement at the interval's own volume and AHT, with occupancy ≤ 0.85. Attainment is over
operating intervals (06:00–24:00 local; vip 08:00–20:00). `required_hours_total` is the §1.6 sum of required agents over
all intervals and queues × 0.5 h. `understaffed_interval_hours` is the sum over intervals of max(0, required − scheduled net of breaks) × 0.5 h.
Efficiency: 1638.0 / 1115.5 = 1.468 (bound 1.57). Figures are from `out/northwind/eval.json`.

## Handover note

### What changed and why

- **Ingest (`wfm/ingest/loader.py`).** The export's `utc_offset` column is now the source of UTC, as the data README
  asks. The fall-back week has a repeated 01:00 hour; the old `tz_localize` could not resolve it, and the offsets
  are checked against `America/Chicago`. Labels are floored to the planning grain: two rows carry `10:01` (2026-10-27
  priority, 2026-10-29 standard) and are treated as the 10:00 interval. The file is not patched. An export must hold
  exactly one row per queue per interval of the local week (338 for this week); duplicates, missing or unexpected
  intervals stop the run. Queues now come from the client's SLA targets. Before this change `vip` was dropped silently.
- **Staffing (`wfm/staffing/required.py`).** The occupancy cap (SOW §1.3, WFM-212) is now applied; it was read but
  not used. `aht_smoothing: interval` now uses each interval's own AHT; before, it collapsed to a queue mean.
  Neither change moves any live client's requirement (checked: 0 intervals change for Contoso W43, Fabrikam W43
  and Wingtip W42).
- **Config (`configs/northwind.yaml`).** Northwind's targets, rules and roster-driven limits from the SOW: per-queue SLA
  targets, `sla_target` 0.95 (§1.6), `aht_smoothing: interval`, `cross_skill_weight: 0` (a person counts once, §1.2),
  `min_rest_hours: 11` (§2.1), split shifts for PT only (§2.2), break placement by surplus (§2.3), vip floor 06:00–24:00 (§2.6),
  and `trim_shifts` (see below). Service defaults are unchanged. New keys default to the previous behaviour.
- **Scheduler (`wfm/scheduler/greedy.py`).** Rest between shifts, the split-shift contract restriction, and break placement
  by largest gross coverage surplus in the 2–5 h window are config-driven. `trim_shifts` replaces a shift with a
  shorter template for the same agent and day when every interval it gives up stays at its need. This brought
  scheduled hours from 1752 to 1638 and efficiency from 1.571 (over the bound) to 1.468. It is enabled for Northwind only.
- **Evaluator (`wfm/evaluate/metrics.py`).** Attainment denominators follow the SOW when configured
  (`attainment_intervals: operating`). `required_hours` is added to `eval.json`. Shift audits now cover break, rest and
  split rules. Rest and split are counted only when configured.
- **Tests and registry.** The two tests that pinned Northwind as "pending" now expect its config to be present (ADR 0008).
  Registry and `clients/README.md` show Northwind's config schema as 2. Status is still `onboarding`.

### Live clients

Schedules for Contoso W43, Fabrikam W43 and Wingtip W42 are byte-identical to before. `eval.json` gains `required_hours`
and a zero `break` audit. Unit tests: 80 pass.

### §2.8 — pre-existing deviations from the §1 method that affect Northwind's queues

1. Occupancy cap not applied (WFM-212): fixed here for all clients, no effect on live clients.
2. `aht_smoothing: interval` collapsed to the queue mean: fixed here. The service default is still `queue_mean` (WFM-198).
3. Greedy break placement was the shift midpoint, not §2.3: Northwind uses the surplus rule. The default is unchanged.
4. Default `cross_skill_weight: 0.5` counts a cross-skilled agent toward a floor, which §1.2 does not allow: Northwind sets 0.
5. Default evaluator counts only intervals with volume > 0 in attainment: Northwind uses operating intervals.
6. `greedy_v2` (WFM-231) is a draft and is not used. Its rest check is inverted (it accepts shifts that leave less than 11 h
   of rest), so it must not be wired in as it stands.
7. **Open, not a deviation the service can accept:** vip coverage (§1.2, §2.6) is not met. Vip attainment is 0.685
   and there are 72 floor gaps, all on 31 Oct and 1 Nov. The vip roster has 11 FT agents (440 h at 40 h each). Vip
   needs at least 348 h of coverage (required plus floor) and in practice more, because the templates are 8 h blocks
   that cannot match the peaked curve. The greedy packing fills weekdays and leaves weekend floors uncovered.
   The downsize pass recovers hours but does not reach the weekend. A better vip packing, or more vip-skilled
   agents, is needed before go-live. Until then, the vip figures above should not be reported as meeting the SOW.

### Data issues to report to Northwind's WFM contact

- Two rows at `10:01` instead of `10:00` (2026-10-27 priority, 2026-10-29 standard).
- The fall-back week includes 50 intervals on 1 Nov (48 normal plus two repeated hours); this is correct and is handled by
  `utc_offset`, but please confirm the offsets are as intended.

### Next steps before go-live review

1. Fix vip packing so the floor holds every interval and vip attainment reaches 0.95.
2. Re-run `python -m wfm run --client northwind --week <week>` for each week and re-check the reconciliation.
3. Set the Northwind export layout and go-live status in the registry once the vip result is accepted.
