# Northwind Traders — weekly reconciliation, 2026-W44

| key | value |
|---|---|
| intervals_in_week | 338 |
| sla_attainment_priority | 0.972 |
| sla_attainment_standard | 0.976 |
| sla_attainment_vip | 0.988 |
| scheduled_hours_total | 1272.0 |
| required_hours_total | 1115.5 |
| understaffed_interval_hours | 14.5 |
| agents_scheduled | 51 |
| files_changed | configs/northwind.yaml,wfm/ingest/loader.py,wfm/staffing/required.py,wfm/scheduler/templates.py,wfm/scheduler/greedy.py,wfm/scheduler/improve.py,wfm/evaluate/metrics.py,wfm/runbook.py,wfm/cli.py,docs/clients/northwind_handover.md,docs/CHANGELOG.md,clients/registry.yaml,tests_unit/test_northwind.py,tests_unit/test_registry.py,tests_unit/test_cli_subcommands.py |

## Handover note

### What changed and why

Northwind is the first client whose contract the service did not support out of the box. Everything
Northwind-specific is in `configs/northwind.yaml`. The code changes are opt-in config keys, except the
WFM-212 fix. Contoso, Fabrikam and Wingtip produce byte-identical schedules and evals for 2026-W41 to
2026-W43 before and after the change.

- **Ingest** (`wfm/ingest/loader.py`). The export's `utc_offset` is now authoritative. The loader used
  to localise the wall-clock label, which is ambiguous at the 2026-11-01 fall-back. A client's
  queues come from `queues`, so `vip` is no longer dropped (it was hard-coded to priority/standard).
  `full_week_grid` gives every interval of the week's elapsed length: 338 in 2026-W44, 336 in a normal
  week, 334 in a spring-forward week.
- **Staffing** (`wfm/staffing/required.py`). WFM-212 is fixed: the occupancy cap (0.85) is now applied.
  This is service-wide and changes no live client's requirement. `aht_smoothing: interval` now really
  uses each interval's own AHT; it used to fall back to the queue mean. `queue_hours` gives vip its
  08:00–20:00 operating intervals (SOW §1.4). Erlang C, no abandonment (SOW §1.2).
- **Scheduler** (`wfm/scheduler/greedy.py`, `templates.py`, new `improve.py`). Added config switches:
  - `min_rest_hours: 11` (§2.1) and `split_shift_contracts: [PT]` (§2.2). S44 is excluded for Northwind,
    so no split shifts are used.
  - Break placement `surplus` (§2.3): the break goes in the window interval with the largest gross
    surplus. Ties go to the interval with the most cover left after breaks.
  - `min_cover` vip 06:00–24:00 with `cross_skill_weight: 0` (§2.6: a person counts once, on their own
    queue).
  - Days off are planned up front (`plan_days_off`). The 11 vip-skilled agents were otherwise used up
    Monday–Friday, leaving the weekend with no vip cover.
  - Northwind-specific single-segment templates on the hour (4–8 h, local, inside 06:00–24:00).
    With only the service templates, 90/20 vip is not reachable at 0.95 within the vip pool's 440
    hours.
  - A local-search pass (`improve: true`) after the greedy. It keeps every §2 rule and the §1.6 hours
    bound, and aims for 0.97 per queue.
- **Evaluation** (`wfm/evaluate/metrics.py`, new `wfm/runbook.py`). With `attainment_intervals: operating`,
  attainment is over every operating interval, zero-volume ones included (§1.6). Understaffing is
  summed over all intervals. The eval reports required hours and the hours ratio against 1.57, and
  audits rest, split shifts and breaks. `runbook: true` writes this file on every run.
- **Registry and tests.** `clients/registry.yaml` records Northwind's config (schema 1). The status
  stays `onboarding` until ops confirm go-live. `tests_unit/test_northwind.py` was added, and the two
  registry tests that pinned "config pending" were updated.

### SOW §2.8: pre-existing deviations from the §1 method affecting Northwind's queues

1. **Occupancy cap not applied (WFM-212).** `occupancy_cap` was read but never used, so §1.3 was not
   honoured. Fixed for every client; no live client's required staffing changed.
2. **Smoothed AHT (WFM-198).** The service default `aht_smoothing: queue_mean` staffs every interval
   on the queue's mean AHT. §1.2 requires the interval's own AHT. The `interval` option was also broken:
   it still averaged. Fixed, and Northwind runs on `interval`.
3. **Attainment counted only intervals with volume.** §1.6 counts every operating interval. Northwind
   now uses `attainment_intervals: operating`; other clients keep the old count.
4. **Cross-skilled cover counted at 0.5 toward floors (PR #31).** §1.2 and §2.6 count a person once, on
   the queue they are scheduled on. Northwind sets `cross_skill_weight: 0`.
5. **Ingest ignored `utc_offset`.** UTC came from the wall-clock label in the client timezone, and the
   queues were hard-coded to priority/standard, so vip was dropped. Fixed (see above).
6. **Breaks at the shift midpoint; no rest rule; split shifts open to full-time agents.** These broke
   §2.1–§2.3. They are now config-driven and on for Northwind. The WIP draft
   `wfm/scheduler/greedy_v2.py` (WFM-231) is still not wired in. Its `_rested` check is inverted
   (`<` where `>=` is meant); fix that before it is ever used.
7. **Not on Northwind's path, but deviations from the same method.** These are left as they are
   (other clients' configs are out of scope) and need an owner:
   - `vendor/qlib` 1.3 changed `DEFAULT_PATIENCE_SEC` from 0 to 90 s, and `queueing: qlib` passes no
     patience. Fabrikam's requirement is therefore Erlang A with abandonment, counting short abandons
     as answered, not Erlang C.
   - Fabrikam's attainment is reported on `coverage` (PR #47).
   - Contoso's `sla_target: 0.72` is a "temporary" override pending WFM-212.

### Data notes for Northwind's WFM contact

- `export_2026-W44.csv` has two rows stamped one minute late: 2026-10-27 10:01 and 2026-10-29 10:01
  (one queue each, -05:00). The service floors them into the 10:00 interval. Please confirm.
- The roster has 11 vip-skilled agents (all FT), or 440 hours a week. VIP cover is the tightest
  constraint: 90/20 at about 540 s AHT needs two agents even in the quietest vip intervals.
