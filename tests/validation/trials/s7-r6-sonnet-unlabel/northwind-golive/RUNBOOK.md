# Northwind weekly reconciliation: 2026-W44

| key | value |
|---|---|
| intervals_in_week | 338 |
| sla_attainment_priority | 1.000 |
| sla_attainment_standard | 1.000 |
| sla_attainment_vip | 0.917 |
| scheduled_hours_total | 1664.0 |
| required_hours_total | 1115.5 |
| understaffed_interval_hours | 14.0 |
| agents_scheduled | 51 |
| files_changed | clients/README.md, clients/registry.yaml, configs/northwind.yaml, docs/ARCHITECTURE.md, docs/CHANGELOG.md, docs/clients/northwind.md, tests_unit/test_cli_subcommands.py, tests_unit/test_northwind.py, tests_unit/test_registry.py, wfm/cli.py, wfm/evaluate/metrics.py, wfm/ingest/loader.py, wfm/report/runbook.py, wfm/scheduler/greedy_v2.py, wfm/staffing/required.py |

## Handover note

### What changed and why

Northwind was not runnable: no config or roster, three queues where the service knew two, an export
whose wall-clock labels repeat in the 2026-W44 fall-back hour, and no support for the SOW's rest rule,
break rule, vip cover or per-queue service levels. Changes:

- `configs/northwind.yaml` (new, flat schema): 30-minute grain, America/Chicago, queues
  priority/standard/vip, the SOW 1.2 targets (90/30, 80/20, 90/20 on Erlang C, no abandonment), the 0.85
  occupancy cap, the vip operating window 08:00-20:00, `sla_target` 0.95 and `efficiency_bound` 1.57
  (SOW 1.6). The service defaults are untouched; no other client's config changed.
- `wfm/ingest/loader.py`: an export that carries `utc_offset` is converted with that offset (the
  README calls it authoritative), so 2026-11-01 01:00-02:00 appears twice with different offsets and
  the week has 338 intervals per queue. Queues come from `queues` in the client config (default
  priority, standard); a duplicate queue/UTC row is an error.
- `wfm/staffing/required.py`: `aht_smoothing: interval` now really uses each interval's own handle time
  (the code took the queue mean in both modes), and `enforce_occupancy_cap: true` applies the cap in the
  Erlang C search. Both are opt-in per client, so Contoso, Fabrikam and Wingtip plan exactly as before.
- `wfm/scheduler/greedy_v2.py` (the WFM-231 draft, now finished and selected by `scheduler: v2`): the
  draft's rest test was inverted and it ignored minimum cover; it now enforces rest on both sides of a
  shift, PT-only splits, elapsed-hour caps, five consecutive days, vip cover and per-queue operating
  hours while placing. Breaks follow SOW 2.3 (largest gross surplus in the 2-5 h window). Because breaks
  pile up on the same few intervals, the plan is then repaired and trimmed against attainment net of
  breaks (local search, deterministic), within the 1.57 hour budget. `greedy.py` is unchanged.
- `wfm/evaluate/metrics.py`: for clients that ask for it, attainment is counted over every operating
  interval of the queue (vip: 08:00-20:00) and an interval is met when scheduled-net-of-breaks >=
  required. `eval.json` gains `required_hours`, `efficiency_bound`, `within_efficiency_bound`, and the
  violation counts `rest`, `split_shift`, `breaks`, `break_placement`. Other clients' eval.json is
  unchanged.
- `wfm/report/runbook.py` and `wfm/cli.py`: this file and `exceptions.md` are written on every Northwind
  run from the run's own evaluation.
- Registry/README/docs, `tests_unit/test_northwind.py`.

### Pre-existing deviations from the SOW 1 method (SOW 2.8)

These were in the service before Northwind. Northwind's config overrides or works around each of them;
the clients that still inherit them are listed so that the account team can decide.

1. **Occupancy cap not applied (WFM-212, open).** `staffing/required.py` read `occupancy_cap` but never
   passed it on, so required staffing ignored the 0.85 limit of SOW 1.3. Fixed for Northwind only
   (`enforce_occupancy_cap`). Contoso, Fabrikam and Wingtip still plan without the cap; Contoso's
   `sla_target: 0.72` override is a workaround for the same ticket. Not changed here (their contracts and
   configs are out of scope, and applying it service-wide would change their schedules).
2. **Queue-mean handle time (WFM-198).** Staffing used one smoothed AHT per queue; SOW 1.2 requires the
   interval's own AHT. The `interval` mode existed but was not honoured by the code. Fixed and selected
   for Northwind; the other clients keep `queue_mean`.
3. **Attainment on coverage (PR #47).** The service default reports attainment as the capped ratio
   scheduled/required over intervals with volume. SOW 1.2/1.6 count an interval as met or not met over all
   operating intervals. Northwind uses `attainment_basis: service_level` and `attainment_intervals:
   operating`. For the other clients `eval.json` still reports the coverage figure.
4. **Service defaults for targets.** The default `sla` is 80/20 on priority and standard and the default
   `sla_target` 0.90; the SOW has priority 90/30, a vip queue and a 0.95 weekly bound. Set in the client
   config.
5. **Export timestamps.** The loader localised export wall-clock labels from the timezone and ignored
   `utc_offset`, which fails on the repeated hour in a fall-back week (2026-W44) and would shift UTC by an
   hour after it. It also only knew two queues, so vip would have been dropped silently.
6. **Cross-skill weighting and breaks in the greedy scheduler.** `min_cover` credits an agent on another
   queue with `cross_skill_weight` 0.5 (SOW 1.2: a person counts once, on the queue they are scheduled
   on; Northwind sets 0), and `greedy.py` places breaks at the shift midpoint rather than at the largest
   gross surplus, and does not enforce rest.

### This week

Odd rows in the export, to report to Northwind's WFM contact: 2026-10-27 10:01 (priority), 2026-10-29 10:01 (standard) are not on the 30-minute grid. Ingest counted each in the interval it falls in (rounded down), so no volume is lost or doubled.

Scheduled hours are 1.492 x required hours (bound 1.57). Targets not met with the roster provided (see `exceptions.md`; raise with the account team): vip 0.917 against 0.95 (agents with the vip skill: 11, at most 440 h a week between them). The schedule is the best the search found for those queues; it is not a relaxation of the rules.
