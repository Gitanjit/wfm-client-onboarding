# Litware Support weekly reconciliation: 2027-W11

| key | value |
|---|---|
| intervals_in_week | 504 |
| sla_attainment_priority | 1.000 |
| sla_attainment_standard | 1.000 |
| sla_attainment_email | 1.000 |
| scheduled_hours_total | 726.0 |
| required_hours_total | 527.0 |
| understaffed_interval_hours | 0.0 |
| agents_scheduled | 24 |
| exception_intervals | 42 |
| files_changed | clients/README.md, clients/registry.yaml, configs/litware.yaml, configs/northwind.yaml, docs/ARCHITECTURE.md, docs/CHANGELOG.md, docs/clients/litware.md, tests_unit/test_cli_subcommands.py, tests_unit/test_litware.py, tests_unit/test_registry.py, wfm/constraints.py, wfm/evaluate/metrics.py, wfm/ingest/loader.py, wfm/report/runbook.py, wfm/scheduler/greedy_v2.py, wfm/scheduler/templates.py |

## Exceptions

- email 2027-03-15T07:00:00Z
- email 2027-03-15T07:20:00Z
- email 2027-03-15T07:40:00Z
- email 2027-03-15T08:00:00Z
- email 2027-03-15T08:20:00Z
- email 2027-03-15T08:40:00Z
- email 2027-03-16T07:00:00Z
- email 2027-03-16T07:20:00Z
- email 2027-03-16T07:40:00Z
- email 2027-03-16T08:00:00Z
- email 2027-03-16T08:20:00Z
- email 2027-03-16T08:40:00Z
- email 2027-03-17T07:00:00Z
- email 2027-03-17T07:20:00Z
- email 2027-03-17T07:40:00Z
- email 2027-03-17T08:00:00Z
- email 2027-03-17T08:20:00Z
- email 2027-03-17T08:40:00Z
- email 2027-03-18T07:00:00Z
- email 2027-03-18T07:20:00Z
- email 2027-03-18T07:40:00Z
- email 2027-03-18T08:00:00Z
- email 2027-03-18T08:20:00Z
- email 2027-03-18T08:40:00Z
- email 2027-03-19T07:00:00Z
- email 2027-03-19T07:20:00Z
- email 2027-03-19T07:40:00Z
- email 2027-03-19T08:00:00Z
- email 2027-03-19T08:20:00Z
- email 2027-03-19T08:40:00Z
- email 2027-03-20T07:00:00Z
- email 2027-03-20T07:20:00Z
- email 2027-03-20T07:40:00Z
- email 2027-03-20T08:00:00Z
- email 2027-03-20T08:20:00Z
- email 2027-03-20T08:40:00Z
- email 2027-03-21T07:00:00Z
- email 2027-03-21T07:20:00Z
- email 2027-03-21T07:40:00Z
- email 2027-03-21T08:00:00Z
- email 2027-03-21T08:20:00Z
- email 2027-03-21T08:40:00Z

## Handover note

### What changed and why

Litware was not runnable: no config, three queues where the service knew two, an export whose rows are
stamped with the END of each interval, 20-minute intervals, and SOW rules the service did not model (an
earliest start per queue, two agents on `priority` at all times, intervals the rules make impossible). The
efficiency bound (1.45 x required hours) is also tight. Changes:

- `configs/litware.yaml` (new, flat schema): 20-minute grain, Europe/London, 07:00-21:00, queues
  priority/standard/email, the SOW 1.2 targets (90/30, 80/30, 80/300 on Erlang C, no abandonment), the 0.85
  occupancy cap, the email arrival window 07:00-19:00, email earliest start 09:00, two agents on `priority`
  in every operating interval, the rest, split-shift and break rules, `sla_target` 0.95 and
  `efficiency_bound` 1.45. The service defaults are untouched. The only other client config touched is Northwind's
  `anneal_iterations` (longer search for its roster-bound vip queue; its vip attainment does not get worse).
- `wfm/ingest/loader.py`: an export with `interval_end_local` is converted with the row's `utc_offset`
  (authoritative; the offset in effect at the END moment) and the 20-minute interval is subtracted in UTC,
  so a row stamped 09:20 is the 09:00-09:20 interval and the week keeps its true elapsed length across a DST
  change. A duplicate queue/UTC row is an error.
- `wfm/constraints.py`: `queue_earliest_start` (SOW 2.5) and the SOW 2.6 test: an operating interval of a
  queue that starts before its earliest start and has demand cannot be staffed without breaking SOW 2.5.
  For Litware these are the `email` intervals 07:00-09:00 local (6 a day, 42 a week); they are listed under
  Exceptions, left out of attainment and of `understaffed_interval_hours`, and kept in the required hours.
- `wfm/scheduler/greedy_v2.py`: a queue's earliest start restricts the templates that may be worked on it;
  the exception intervals are not chased. With the default search (a per-queue anneal) the plan used all of
  the 1.45 hour budget and still left `email` at 0.948, so `anneal_hours: true` adds a joint anneal over all
  queues that minimises shortage and scheduled hours together (re-templating, re-queuing, moving, dropping,
  adding and swapping shifts; deterministic, seeded from client, week and queue). Breaks follow SOW 2.3
  (largest gross surplus in the 2-5 h window).
- `wfm/scheduler/templates.py`: `exclude_templates` (opt-in). Litware does not use the split template
  S44, so SOW 2.2 and the break rule for split shifts cannot be in doubt.
- `wfm/evaluate/metrics.py`: `exceptions`, `exception_intervals` and the `queue_start` audit in `eval.json`;
  intervals under Exceptions are excluded from attainment and understaffed hours.
- `wfm/report/runbook.py`: one report writer for every client with `runbook: true` (queues from the config,
  the Exceptions section, a handover note per client, `files_changed` by content against the delivery base).
- Registry, client notes, README, changelog, `tests_unit/test_litware.py`.

### Pre-existing deviations from the SOW 1 method (SOW 2.8)

These were in the service before Litware and affect its queues if left at the service defaults. Litware's
config overrides or works around each of them; the clients that still inherit them are not changed here.

1. **Occupancy cap not applied (WFM-212, open).** `staffing/required.py` read `occupancy_cap` but never
   passed it to the Erlang C search, so required staffing ignored the 0.85 limit of SOW 1.3. Litware sets
   `enforce_occupancy_cap: true`. Contoso, Fabrikam and Wingtip still plan without the cap.
2. **Queue-mean handle time (WFM-198).** Staffing used one smoothed AHT per queue; SOW 1.2 requires each
   interval's own AHT. Litware selects `aht_smoothing: interval`, which the code now honours.
3. **Attainment on coverage (PR #47).** The service default reports the capped ratio scheduled/required over
   intervals with volume, with no netting of breaks. SOW 1.2/1.6 count an interval as met or not met, net of
   breaks, over every operating interval. Litware uses `attainment_basis: service_level` and
   `attainment_intervals: operating`; the other clients' `eval.json` still reports coverage.
4. **Service-default targets and queues.** The default `sla` is 80/20 on two queues (priority, standard) and
   the default `sla_target` 0.90; the loader only built those two queues, so `email` would have been dropped
   silently. Litware sets its own `sla`, `sla_target` and `queues`.
5. **Export timestamps.** The loader treated the export's wall-clock label as the interval START and
   localised it from the timezone, ignoring `utc_offset`. Litware stamps the interval END, so every
   interval would have sat 20 minutes late, and in a DST week the label can not be localised. Fixed for
   end-stamped exports with an offset column (and for any export with `utc_offset`).
6. **Cross-skill weighting.** `min_cover` credits an agent on another queue with `cross_skill_weight` 0.5; SOW
   1.2 counts a person once, on the queue they are scheduled on. Litware sets 0, so the two `priority`
   agents are people scheduled on `priority`.
7. **Default scheduler.** `greedy.py` places breaks at the shift midpoint rather than at the largest gross
   surplus and does not enforce rest; Litware uses `scheduler: v2`.

### This week

42 interval(s) are listed under Exceptions: email demand before the 09:00 earliest start (SOW 2.5), left out of attainment and understaffed hours (SOW 2.6) and kept in the required hours. Scheduled hours are 1.378 x required hours (bound 1.45). Every queue meets its weekly attainment target.
