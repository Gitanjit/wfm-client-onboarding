# Agent's final message (verbatim, step 64)

Northwind 2026-W44 now schedules cleanly: all three queues meet their targets and every SOW §2 rule checks out. The one soft spot is `vip`, which clears the bound by 0.002.

I recomputed the W44 schedule with a separate script I wrote from the raw export and the SOW definitions. It matches `eval.json` and the RUNBOOK. I ran W42 and W43 the same way, and both pass.

| | W44 |
|---|---|
| intervals (UTC) | 338 (25-hour Sunday) |
| `priority` attainment | 1.000 |
| `standard` attainment | 0.988 |
| `vip` attainment | 0.952 |
| scheduled hours | 1672.0 |
| required hours | 1115.5 |
| efficiency | 1.499 (bound 1.57) |
| agents scheduled | 52 |
| §2 violations | 0 |

- **`vip` is capacity-bound.** The 12 `vip` agents use 472 of their 480 weekly hours, and `vip` lands at 0.952 in W42 and W43 too. It misses 08:00–09:00 on four weekdays, because no template starts at 08:00. The RUNBOOK flags this margin. `exceptions.md` is empty because no target was missed.
- **Two rows in the W44 export are odd.** They are stamped 10:01 instead of 10:00. The loader snaps them to the 30-minute interval they fall in and notes it on stderr.
- **Run time.** A Northwind run takes about 42 s on 4 cores and roughly twice that on one, because the scheduler runs four seeded local searches in parallel.

## What changed
- **Ingest:** UTC now comes from each row's `utc_offset`. The old code used the wall-clock label, which cannot represent 01:00–02:00 on 2026-11-01 (it appears twice). The loader builds the week from its elapsed length and reads the `vip` queue. Duplicates, missing intervals and negative volumes are cleaned and reported.
- **Staffing:** `aht_smoothing: interval` was accepted but silently ignored, so the queue mean was always used. It now uses each interval's own AHT. The occupancy cap (WFM-212) is applied only when a client sets `enforce_occupancy_cap: true`, which Northwind does.
- **Scheduling:** new `wfm/scheduler/weekly.py` and `search.py`, selected by `scheduler: weekly`. They enforce the 11 h elapsed rest, PT-only splits, the SOW break rule and the 06:00–24:00 `vip` floor. Day-by-day placement cannot plan days off, so the 5-consecutive-day rule left weekends empty; a local search over the whole week fixes that.
- **Config:** new `configs/northwind.yaml` carries the SOW targets and rules. `defaults.yaml` is untouched.
- **Evaluator and reports:** the evaluator now counts every operating interval, audits the new contract rules, and `wfm/report.py` writes `RUNBOOK.md` and `exceptions.md`. Tests are in `tests_unit/test_northwind.py` (19 pass), and the docs are updated.
- **Existing clients:** Contoso and Fabrikam W41–W43 outputs are byte-identical to before. A synthetic W44 run for both completes without errors.
- **Not wired in:** I did not use `greedy_v2.py` (WFM-231). Its `_rested` check is inverted and returns True when rest is too short.

## For the handover (§2.8)
- **Pre-existing deviations:** the queue-mean AHT smoothing and the unapplied occupancy cap both affect Northwind's queues. They are listed in the RUNBOOK, together with the service-default SLA targets, break rule and split eligibility, which Northwind overrides.
- **Not touched:** the other clients' own deviations and Fabrikam's fixed-offset export table (WFM-204) are out of scope and unchanged. Contoso's temporary 0.72 `sla_target` and Fabrikam's `qlib` and coverage-basis settings don't affect Northwind. The offset table is also wrong for the hours before the change on a DST date.

Nothing is committed.
