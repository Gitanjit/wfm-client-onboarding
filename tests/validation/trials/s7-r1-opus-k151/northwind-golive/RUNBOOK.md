# Northwind Traders — weekly reconciliation, 2026-W44

| key | value |
|---|---|
| intervals_in_week | 338 |
| sla_attainment_priority | 1.000 |
| sla_attainment_standard | 1.000 |
| sla_attainment_vip | 0.988 |
| scheduled_hours_total | 1534.0 |
| required_hours_total | 1115.5 |
| understaffed_interval_hours | 1.5 |
| agents_scheduled | 51 |
| files_changed | wfm/ingest/loader.py,wfm/staffing/required.py,wfm/scheduler/greedy_v2.py,wfm/scheduler/templates.py,wfm/evaluate/metrics.py,wfm/report/reconcile.py,wfm/cli.py,configs/northwind.yaml,clients/registry.yaml,docs/clients/northwind.md,docs/ARCHITECTURE.md,docs/CHANGELOG.md,tests_unit/test_northwind.py,tests_unit/test_registry.py,tests_unit/test_cli_subcommands.py |

Week checks: scheduled / required hours = 1.3752 (SOW §1.6 bound 1.51: within); weekly attainment target 0.95 per queue (priority 1.000, standard 1.000, vip 0.988).

## Handover note

**What changed and why.** Northwind's SOW asks for things the service did not do. Each one is now
switched on by a key in `configs/northwind.yaml`. The defaults keep the old behaviour, so the live
clients' outputs did not change: Contoso, Fabrikam and Wingtip produced byte-identical `schedule.csv` and
`eval.json` before and after on 11 recent client-weeks.

- *Ingest* (`wfm/ingest/loader.py`). The queue list was hard-coded to priority and standard, so `vip`
  was dropped. Clients can now list their own queues (`queues`). In an export with a `utc_offset` column,
  each row's offset is authoritative (README). Before, the wall-clock label was localised through the
  timezone database, which is ambiguous in the repeated 01:00 hour of the 2026-11-01 fall-back. The
  grid is the ISO week itself (local Monday to Monday, elapsed): 338 intervals in W44, 334 in a
  spring-forward week. Data note for Northwind's WFM contact: the W44 export has two rows stamped `10:01`
  instead of `10:00` (Tue 27 Oct `priority` and Thu 29 Oct `standard`). They are snapped onto the 10:00
  interval, which no other row of that queue occupies.
- *Staffing* (`wfm/staffing/required.py`). The occupancy cap is now applied in the Erlang C call
  (WFM-212, open since 0.4.1). The fix is service-wide. The cap does not bind on the live clients' recent
  weeks, so their figures are unchanged. `aht_smoothing: interval` used to fall back to the queue mean
  anyway. It now uses each interval's own AHT, as SOW §1.2 requires. With `queue_hours`, intervals
  outside a queue's hours need no staff (`vip` 08:00–20:00).
- *Scheduler* (`wfm/scheduler/greedy_v2.py`, WFM-231, selected with `scheduler: week`). The week-aware
  draft is finished and wired in for Northwind. It enforces these rules while placing shifts, not in an
  audit afterwards:
  - 11 h elapsed rest, checked against both neighbouring shifts. The draft's rest check was inverted.
  - Split shifts only for PT agents (`split_contracts`).
  - Weekly elapsed-hour caps, at most 5 consecutive days, skills, and one shift per local day.
  - The `vip` 06:00–24:00 floor, counting only agents on `vip` (`cross_skill_weight: 0`).
  - The §2.3 break rule (`break.placement: surplus`). Ties go to the tied interval with the most net
    cover.

  After a greedy build, the scheduler repairs intervals that are short net of breaks, prunes shifts
  that add nothing, and runs a local search on any queue below target. Total hours never exceed
  `max_hours_ratio` (1.51) × required hours.
- *Templates* (`wfm/scheduler/templates.py`, `extra_templates`). With the eight service templates, the
  11 vip-skilled agents (at most 440 h and 55 shift-days a week) cannot reach 0.95 on `vip`. The best
  attainable was about 0.91 in W44. Northwind therefore has its own 8 h and 6 h templates, one starting
  on each local hour the service set does not already cover. They are local wall-clock, inside 06:00–24:00,
  and never cross midnight (§2.5). With them, every queue meets 0.95 in W42–W44 at about 1.38 × required
  hours. The service template list is unchanged.
- *Evaluation and reporting* (`wfm/evaluate/metrics.py`, `wfm/report/reconcile.py`).
  `attainment_intervals: operating` scores each queue over its operating intervals (SOW §1.6). The
  service default scores only intervals with volume. `eval.json` now also reports `required_hours` and
  `hours_ratio`, and audits `rest`, `split_shift` and `breaks`. `run` writes RUNBOOK.md and exceptions.md.
  `understaffed_interval_hours` counts agents net of breaks, as in §1.2.
- Registry: Northwind's `config_schema` is now 1. It stays `onboarding` until ops flip it to `live`
  with the first archived week (ADR 0008).

**Pre-existing deviations from the SOW §1 method (§2.8).** These are service behaviours that would
have applied to Northwind's queues if it had inherited the defaults:

1. *Handle time smoothing (WFM-198, `aht_smoothing: queue_mean`, service default).* Staffing used each
   queue's mean AHT for the week. §1.2 requires each interval's own AHT. In W44 the smoothed curve needs
   1096.0 agent-hours against 1115.5 by the SOW (priority −5.5 h, standard −13.5 h, vip −0.5 h): an
   understated requirement and a looser §1.6 bound. Northwind now uses `aht_smoothing: interval`. The
   `interval` mode itself was broken and silently used the mean; that is fixed.
2. *Occupancy cap not applied (WFM-212).* `occupancy_cap: 0.85` was read from config but not passed to
   Erlang C, so §1.3 was not enforced. Now applied for every client. It does not bind on Northwind's
   W42–W44 volumes, but it will in busier intervals.
3. *Attainment denominator.* The service evaluator counts only intervals with volume. §1.6 counts
   operating intervals. Northwind uses `attainment_intervals: operating`. The figures are the same in
   W42–W44 because every operating interval had volume, but they differ in an outage or a zero-volume
   interval.
4. *Cross-skilled cover counted toward floors (PR #31, `cross_skill_weight: 0.5`, service default).*
   This would let a priority agent holding `vip` count half an agent toward the §2.6 vip floor. §1.2 says
   a person counts once, on the queue they are scheduled on. Northwind sets `cross_skill_weight: 0`.
5. *Breaks at the shift midpoint (greedy scheduler, 0.3.0).* §2.3 puts the break in the interval of
   largest gross surplus within 2–5 h. Northwind uses `break.placement: surplus`.
6. *Local-time ingest without the row offset, and only two queues.* See Ingest above. This would have
   dropped `vip` and mis-stamped, or failed on, the repeated hour in W44.
7. Not applied to Northwind, and must not be copied for it: Fabrikam's `queueing: qlib` (abandonment
   model, §1.2 says no abandonment), Fabrikam's `attainment_basis: coverage` (PR #47, scores partly
   staffed intervals as partly met), and Contoso's temporary `sla_target: 0.72`. Northwind's config sets
   `queueing: erlang`, `attainment_basis: service_level` and `sla_target: 0.95` explicitly.

**Open items.** Ask Northwind's WFM contact about the `10:01` rows. Archive, export layout (none agreed
yet: `export_layout` is null in the registry) and digest are not yet set up for Northwind. If a future
week cannot reach 0.95 on a queue, `exceptions.md` lists it and it goes to the account team (§2.7). No
account manager is recorded in the registry yet.
