# Northwind — weekly reconciliation, 2026-W44

| key | value |
|---|---|
| intervals_in_week | 338 |
| sla_attainment_priority | 1.000 |
| sla_attainment_standard | 1.000 |
| scheduled_hours_total | 1226.0 |
| required_hours_total | 809.5 |
| understaffed_interval_hours | 0.0 |
| agents_scheduled | 40 |
| files_changed | configs/northwind.yaml, wfm/cli.py, wfm/evaluate/metrics.py, wfm/ingest/loader.py, wfm/runbook.py, wfm/scheduler/greedy_v2.py, wfm/staffing/required.py, tests_unit/test_northwind.py, docs/ARCHITECTURE.md, docs/CHANGELOG.md, docs/northwind_runbook_notes.md |

## What changed and why

Northwind went live in 2026-W44 (SOW `docs/NORTHWIND_SOW.md`). The service could not deliver the SOW as it
stood, so these changes were needed. Contoso and Fabrikam keep their config files, and their schedules are
byte-identical to before (W41–W43 compared).

- **Config, not defaults** (`configs/northwind.yaml`): 30-minute grain, America/Chicago, priority 90/30 and
  standard 80/20 (SOW §1.2), occupancy cap 0.85, `aht_smoothing: interval` (§1.2 says the interval's own
  handle time), rest 11 h, split shifts PT only, surplus-based breaks, hours bound 1.57. `defaults.yaml` is untouched.
- **Ingest** (`wfm/ingest/loader.py`): the export's `utc_offset` is now authoritative. Localizing the wall-clock
  label would have mishandled Sunday 2026-11-01, when the 01:00–01:59 hour occurs twice (CDT, then CST):
  W44 has **338** intervals, not 336. The grid is now the ISO week in the client's timezone, by elapsed length.
  Two rows are labelled `10:01` (2026-10-27 priority, 2026-10-29 standard); they are typos for `10:00` and are
  read into the 10:00 interval. **To report to Northwind's WFM contact.**
- **Staffing** (`wfm/staffing/required.py`): the occupancy cap is now applied (WFM-212, it was read and ignored),
  and `aht_smoothing: interval` really uses each interval's own AHT (it used the queue mean in both modes).
  Contoso and Fabrikam requirements did not change.
- **Scheduler** (`wfm/scheduler/greedy_v2.py`, WFM-231, now wired in via `scheduler: week_aware`; others keep
  `greedy.py`): enforces the 11 h rest in elapsed time against the agent's whole week (the draft's rest check was
  inverted), split shifts for PT only, hour caps, five-day run, skills. Breaks go by SOW §2.3: window 2–5 h after the shift
  start, in the interval with the largest gross surplus. Coverage is planned net of breaks: after breaks are placed,
  intervals still short get another shift. A trim pass then drops or shortens shifts whenever that leaves no interval
  worse, to stay under the 1.57 hours bound. If that were not enough, the bound is met by giving up the
  least-harmful intervals while each queue stays at 0.96 or better (slow; not needed for W42–W44).
- **Evaluator / report**: audits rest, split-shift and break-count rules where a client's config sets them;
  `wfm/runbook.py` writes this file on every Northwind run, figures recomputed from the written schedule.

## Notes

- Sampled W42, W43 and W44, and a synthetic week with 25% more volume: every rule holds, attainment 1.000 on both
  queues, scheduled hours about 1.49–1.52 × required.
- A split shift (S44) is treated as one 8-hour shift: one break, in its first segment, 2–5 h after the shift starts.
- Not changed (out of scope): Contoso's temporary `sla_target: 0.72` override; Fabrikam's no-offset export path in
  the loader still applies one offset to the whole of a DST-change date, so the first hours of that day would
  be an hour off (canonical Fabrikam files are unaffected).
