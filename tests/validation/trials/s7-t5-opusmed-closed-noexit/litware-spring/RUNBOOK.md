# Litware Support — 2027-W11 reconciliation

| key | value |
|---|---|
| intervals_in_week | 504 |
| sla_attainment_priority | 1.000 |
| sla_attainment_standard | 1.000 |
| sla_attainment_email | 1.000 |
| scheduled_hours_total | 738.0 |
| required_hours_total | 527.0 |
| understaffed_interval_hours | 0.0 |
| agents_scheduled | 24 |
| exception_intervals | 42 |
| files_changed | configs/litware.yaml, wfm/ingest/loader.py, wfm/constraints.py, wfm/scheduler/week.py, wfm/evaluate/metrics.py, wfm/report/runbook.py, wfm/cli.py, clients/registry.yaml, clients/README.md, docs/clients/litware.md, docs/clients/northwind.md, docs/ARCHITECTURE.md, docs/CHANGELOG.md, tests_unit/test_litware.py, tests_unit/test_registry.py, tests_unit/test_cli_subcommands.py |

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

**What changed and why (go-live, 2027-W11).** Every change is opt-in through `configs/litware.yaml`.
Contoso, Fabrikam and Northwind outputs are byte-identical before and after.

- *Config* (`configs/litware.yaml`). SOW §1 values: 20-minute grain, Europe/London, 07:00–21:00 for all three
  queues, 90/30, 80/30 and 80/300, occupancy cap 0.85, interval AHT, Erlang C, attainment over operating
  intervals, efficiency cap 1.45. SOW §2 rules: 11 h rest, PT-only splits, surplus-based breaks, 40/24 h,
  five consecutive days. Litware runs on `scheduler: week`, the scheduler built for Northwind.
- *Ingest* (`wfm/ingest/loader.py`). Litware stamps each row with the interval's END (`interval_end_local`).
  UTC end = label + `utc_offset` (the offset at that moment, authoritative); the interval starts 20 minutes
  earlier. Read as a start label, all demand would sit one interval late. A DST week gets 501 or 507
  intervals (checked on synthetic 2027-W12 and 2027-W43 files); otherwise it gets 504.
- *Priority cover* (§2.4): a `min_cover` floor of 2 agents on `priority`, 07:00–21:00, net of breaks,
  cross-skilled agents counting 0.
- *Email start* (§2.5, new `queue_earliest_start: {email: 9}` in `wfm/constraints.py` and
  `wfm/scheduler/week.py`): no email template starts before 09:00, so email gets only D8, L8, P6b and P4. P6a and
  S44 can't be used on email. `eval.json` audits it (`queue_earliest_start`).
- *Infeasible intervals* (§2.6, new `exceptions: true`). An operating interval is an exception when fewer
  agents than it requires could ever be on the queue then (skills, allowed templates, the email start). In
  practice: every `email` interval 07:00–09:00 local with contacts (42 in 2027-W11). They are listed under
  Exceptions and in `eval.json`, left out of attainment and understaffing (§1.6, §3), and still counted in
  required hours. No rule is broken to cover them.
- *Scheduler aim* (`attainment_aim: 1.0`). The search aims to meet every non-exception interval and stays
  under 1.45 × required hours. In 2027-W11 it meets all of them at 1.40 × required hours. W10 does the same at 1.42 ×.
- *Report* (`wfm/report/runbook.py`). Adds the `exception_intervals` key and the `## Exceptions` section; the
  queues are listed in SOW order.

**Readings of the SOW used here.** Email's operating intervals are 07:00–21:00 (§1.4 gives one set of
operating hours; 19:00–21:00 carries no email and needs no staff). Every non-exception interval is met, so the
attainment figures are the same whether email is counted to 19:00 or 21:00. A break counts as absent for
the 20-minute interval it fills (on this grain, the break is exactly one interval). The break window is
honoured under both the closed and the half-open reading of "between two and five hours". §2.4 is met net
of breaks, which satisfies either reading of "breaks aside".

**§2.8: deviations from the §1 method that existed before go-live and affect Litware's queues.**

1. WFM-198. By default staffing uses the smoothed queue-mean AHT, not the interval's own AHT (§1.2). Until
   the Northwind go-live fix, `aht_smoothing: interval` was silently ignored. Litware runs on interval AHT.
2. WFM-212. The occupancy cap (§1.3) was read but not applied until the Northwind go-live fix. It is applied
   for Litware.
3. By default the evaluator counts attainment over intervals with volume, not operating intervals (§1.6).
   It had no notion of infeasible intervals, so they counted as misses. Litware uses
   `attainment_intervals: operating` and `exceptions: true`.
4. By default `min_cover` counts a cross-skilled agent on another queue as 0.5 (PR #31) and counts floors
   gross of breaks. §1.2 counts a person once, on their own queue. Litware sets `cross_skill_weight: 0` and
   `floor_net_of_breaks: true`. Ten Litware agents are cross-skilled, so this would have mattered.
5. The default greedy scheduler places breaks at the shift midpoint (not §2.3), has no rest rule (§2.1),
   and lets FT agents take the S44 split (§2.2). Litware uses `scheduler: week`. The WFM-231 draft
   (`greedy_v2.py`) is not used: its rest check is inverted.
6. The loader assumed exports were labelled with interval starts (fixed for Litware, above). It also
   dropped queues other than `priority`/`standard` (fixed at the Northwind go-live; `email` is kept).

The fixes in items 1, 2, 3 (operating intervals), 4 and 6 (queues) came with the Northwind go-live
change. That change is in the working tree but not yet committed. Litware depends on it.

**Figures in the table** are recomputed from `schedule.csv`. Scheduled hours are elapsed and include paid
breaks. Required hours are Erlang C under §1.2–§1.3 over every interval and queue, exceptions included.
The §2.4 floor is not counted as required.
