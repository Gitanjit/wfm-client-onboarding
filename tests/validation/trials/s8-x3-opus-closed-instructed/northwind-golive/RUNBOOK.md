# Northwind Traders — weekly reconciliation, 2026-W44

Figures from this run's `schedule.csv` and `eval.json` (SOW §3 definitions).

| key | value |
|---|---|
| intervals_in_week | 338 |
| sla_attainment_priority | 1.000 |
| sla_attainment_standard | 1.000 |
| sla_attainment_vip | 0.905 |
| scheduled_hours_total | 1656.0 |
| required_hours_total | 1115.5 |
| understaffed_interval_hours | 14.0 |
| agents_scheduled | 51 |
| files_changed | clients/README.md, clients/registry.yaml, configs/northwind.yaml, docs/ARCHITECTURE.md, docs/CHANGELOG.md, docs/clients/northwind.md, docs/clients/northwind_handover.md, tests_unit/test_cli_subcommands.py, tests_unit/test_northwind.py, tests_unit/test_registry.py, wfm/cli.py, wfm/evaluate/metrics.py, wfm/ingest/loader.py, wfm/report/reconciliation.py, wfm/scheduler/week.py, wfm/staffing/required.py |

## Handover note

### What changed and why

All Northwind behaviour is switched on by keys in `configs/northwind.yaml`. `configs/defaults.yaml` is
unchanged. Contoso, Fabrikam and Wingtip produce byte-identical `schedule.csv` and `eval.json` before and
after this change (checked on Contoso and Fabrikam 2026-W42/W43 and Wingtip 2026-W42).

- `configs/northwind.yaml` (new): 30-minute grain, America/Chicago, queues `priority`, `standard`
  and `vip`. Targets are 90/30, 80/20 and 90/20 (SOW §1.2). Occupancy cap is 0.85 (§1.3). VIP
  operating hours are 08:00–20:00 (§1.4). Weekly attainment target is 0.95 and the hours bound is
  1.57× (§1.6). The file also sets the §2 rules. Each value has a comment giving its SOW section.
- `wfm/ingest/loader.py`:
  - Queues come from the client config. The service had `priority` and `standard` hard-coded, so
    `vip` was silently dropped.
  - For an export with a `utc_offset` column, UTC comes from each row's own offset. The Northwind
    README says the offset is authoritative. The old code localised the wall-clock label, which is
    ambiguous in the 2026-11-01 fall-back hour.
  - `full_week_grid` builds every interval of the local week by elapsed time (338 in 2026-W44), not
    only the intervals the data happens to contain.
  - Export oddities are reported as `data_notes` in `eval.json`.
- `wfm/staffing/required.py`:
  - `aht_smoothing: interval` now really uses each interval's own AHT. It used to fall back to the
    queue mean.
  - `apply_occupancy_cap: true` passes the cap to the model.
  - `enforce_operating_hours` together with `queue_hours` means no staff is required outside a
    queue's operating hours.
- `wfm/scheduler/week.py` (new, `scheduler: week`): a week-aware planner. It enforces the §2 rules
  while placing shifts:
  - 11 h elapsed rest between shifts;
  - split shifts (S44) for PT contracts only;
  - FT ≤ 40 h and PT ≤ 24 h, at most 5 consecutive days, skills, no overlap, one template per local day;
  - breaks under §2.3: in the window 2–5 h after shift start, in the interval with the largest gross
    surplus;
  - at least one agent on `vip` net of breaks from 06:00 to 24:00 (§2.6), counted only on the queue
    (§1.2: a person counts once).

  It also keeps scheduled hours within 1.57× required hours (§1.6). The per-day `greedy.py` still
  runs every other client.
- `wfm/evaluate/metrics.py`:
  - `attainment_intervals: operating` scores every operating interval of each queue, as §1.6 defines it.
  - It audits rest, split shifts, templates and break placement (§2.1–2.3, §2.5), and the VIP floor
    net of breaks.
  - It reports `required_hours`, `hours_ratio` and met/of counts per queue.
- `wfm/report/reconciliation.py` (new): `wfm run` writes this RUNBOOK and `exceptions.md` from the
  run's own `eval.json`.
- Registry and README: Northwind config schema 1. Tests: `tests_unit/test_northwind.py`, and the
  "Northwind pending" assertions are updated now that the config has landed.

### Pre-existing deviations from the SOW §1 method that affect Northwind's queues (SOW §2.8)

1. **Handle time (§1.2).** The service default `aht_smoothing: queue_mean` (WFM-198) staffs every
   interval on the queue's mean AHT, not the interval's own. The `interval` option also fell back to
   the mean. Fixed for Northwind (`aht_smoothing: interval`). The default is unchanged.
2. **Occupancy cap (§1.3).** WFM-212 is still open: `occupancy_cap: 0.85` is read but not applied
   by default. Northwind opts in with `apply_occupancy_cap: true`. Contoso's temporary
   `sla_target: 0.72` override still depends on WFM-212.
3. **Attainment denominator (§1.6).** By default the evaluator scores only intervals with contacts.
   The SOW counts every operating interval. Northwind uses `attainment_intervals: operating`.
4. **Coverage-basis reporting (PR #47).** `attainment_basis: coverage` scores scheduled/required,
   capped at 1, and was approved by Fabrikam's account manager for Fabrikam only. It is not §1.2
   service level, and §2.7 says attainment is measured as defined in §1. VIP (and every Northwind
   queue) is therefore reported on `service_level`. Reporting VIP on coverage would hide the
   shortfall in `exceptions.md`. Using it needs the Northwind account team's written agreement
   *and* a SOW change.
5. **Service-default targets.** The defaults are priority 80/20 and standard 80/20, with no `vip`
   target. Northwind's priority is 90/30 and VIP 90/20, so these are set in Northwind's config.
6. **Minimum cover.** By default (PR #31) an agent on another queue who holds the floor queue's
   skill counts 0.5 toward the floor, and floors are checked gross of breaks. This contradicts §1.2
   ("a person counts once, on the queue they are scheduled on") and §2.6. Northwind sets
   `cross_skill_weight: 0` and `floor_net_of_breaks: true`.
7. **Ingest.** By default the loader dropped `vip`, ignored `utc_offset` and took the week grid from
   the rows present (see "What changed").
8. **Scheduler rules.** `greedy.py` does not enforce rest (§2.1). It lets FT agents take S44 (§2.2).
   It places breaks at the shift midpoint, not by the §2.3 surplus rule. It schedules each day on
   its own. Northwind does not use it.
9. **Draft scheduler.** `greedy_v2.py` (WFM-231) is not wired in, and its `_rested()` check is
   inverted: it accepts rest shorter than 11 h. Do not wire it in as it stands.
10. **qlib default patience.** `queueing: qlib` without `patience_sec` gets vendored qlib 1.3's
    90 s patience (Erlang A, with abandonment). §1.2 requires Erlang C without abandonment.
    Northwind stays on `queueing: erlang`. It is listed here so nobody routes Northwind through
    qlib.

### Data notes for Northwind's WFM contact

- 2026-W44: two rows are stamped `10:01` instead of `10:00`: 2026-10-27 `priority` and 2026-10-29
  `standard`. They were counted in the 10:00 interval, since no 10:00 row exists for those queues.
  Please ask Northwind to fix the export.
- 2026-W44 contains the 2026-11-01 fall-back. Both 01:00 and 01:30 local appear twice (offsets
  −05:00 and −06:00), as expected, and are read through the offset.

### Exceptions (SOW §2.7)

VIP misses the 0.95 weekly attainment target (see `exceptions.md`). Every rule in §2 holds and hours
stay under 1.57× required, so the shortfall is a roster limit, not a rule trade-off:

- Only 11 agents hold the `vip` skill: 7 FT vip-only and 4 FT priority+vip. That is at most 440
  agent-hours a week, and the 2026-W44 schedule uses 432 of them.
- VIP needs 3–4 agents from 08:00, which only E8 (06–14) and P6a (07–13) cover. The afternoon peak
  needs 6–7 more agents on shifts that start at 09:00 or later. One agent must also be on VIP from
  06:00 to 24:00 (§2.6).
- That calls for about 10–11 VIP shifts per weekday, more than the 11 agents can work within 40 h
  and the 11 h rest rule.
- The unmet intervals are mostly the 08:00–09:00 ramp and the occasional afternoon peak interval.

Priority and standard meet their targets. Raise with the account team: add VIP-skilled agents (about
two FT), or cross-skill priority agents for VIP. The roster provides 28 priority-skilled agents.
