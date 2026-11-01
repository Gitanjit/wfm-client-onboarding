# Litware — weekly reconciliation, 2027-W11

| key | value |
|---|---|
| intervals_in_week | 504 |
| sla_attainment_email | 1.000 |
| sla_attainment_priority | 1.000 |
| sla_attainment_standard | 0.997 |
| scheduled_hours_total | 718.0 |
| required_hours_total | 527.0 |
| understaffed_interval_hours | 0.3 |
| agents_scheduled | 24 |
| exception_intervals | 42 |
| files_changed | configs/litware.yaml, wfm/ingest/loader.py, wfm/staffing/required.py, wfm/scheduler/greedy_v2.py, wfm/scheduler/templates.py, wfm/evaluate/metrics.py, wfm/runbook.py, tests_unit/test_litware.py, docs/ARCHITECTURE.md, docs/CHANGELOG.md, docs/litware_runbook_notes.md |

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

## What changed and why

Litware goes live in 2027-W11 (SOW `docs/LITWARE_SOW.md`). Their contract differs from the service in ways the
code could not express, so these changes were needed. Contoso, Fabrikam and Northwind keep their configs, and
their schedules are unchanged (every week of their data compared before and after).

- **Config, not defaults** (`configs/litware.yaml`): 20-minute grain, Europe/London, hours 07:00–21:00, three
  queues, priority 90/30, standard 80/30, email 80/300 (§1.2), occupancy cap 0.85, `aht_smoothing: interval`,
  rest 11 h, split shifts PT only and `exclude_templates: [S44]`, surplus-based breaks, `min_staffed: {priority: 2}` (§2.4),
  `earliest_start: {email: 9}` (§2.5), `exceptions: true` (§2.6), hours bound 1.45. `defaults.yaml` is untouched.
- **Ingest** (`wfm/ingest/loader.py`): Litware's export stamps each row with the *end* of its interval. A row
  labelled 09:20 covers 09:00–09:20, so the loader steps back one interval from the (offset-derived) UTC stamp; the
  `00:00` row of the following Monday is the last interval of the week. Reading the label as a start would shift
  the whole demand curve 20 minutes late and put the last interval into the wrong week. The queue list now comes
  from the config (`queues`), so `email` is read; existing clients keep the two default queues.
- **Staffing** (`wfm/staffing/required.py`): a `floor` column (two agents on `priority` in every operating
  interval) is kept apart from `required`, so the SLA, the required hours and the break-surplus rule still use
  the pure Erlang C figure of §1.2–§1.3. `structural_exceptions` finds the intervals §2.5 makes impossible:
  email intervals with demand that start before 09:00 local. They are listed under Exceptions, left in the week's
  totals, and not chased (no rule is broken to cover them) or counted in attainment or understaffed hours.
- **Scheduler** (`wfm/scheduler/greedy_v2.py`): enforces the per-queue earliest start and the priority floor
  (gross, breaks aside) while placing, trimming and shortening shifts. The repair step can now lengthen an
  existing shift as well as add one, and the repair/trim cycle repeats from freshly rebuilt agent state:
  trimming frees agents' hours and days, and the old single pass left the end of the week short.
- **Evaluator / report**: `eval.json` audits break window, break placement, email start and priority floor in
  addition to the earlier rules, and reports attainment over operating intervals without the exceptions;
  `wfm/runbook.py` writes this file with the `exception_intervals` key and the `## Exceptions` section, figures
  recomputed from the written schedule.

## Notes

- Operating intervals for attainment are all 07:00–21:00 local intervals on every queue (email's 19:00–21:00 carry
  no volume and are met trivially). Required hours include the Exceptions intervals.
- Litware's config leaves out the split template (S44): §2.3 does not say whether two 4 h segments are one shift of
  8 h for the break rule, and the plan meets every target without it. §2.2 (split shifts PT only) is still enforced
  by the scheduler and the audit if a split template is ever enabled. Northwind keeps S44.
- Sampled 2027-W10 and W11, a synthetic W12 that contains the 2027-03-28 clock change (501 intervals) and a
  synthetic week with 30% more volume: every §2 rule holds, attainment is 0.99 or better on each queue, hours are about
  1.27–1.36 × required. The only interval left short in W11 is standard on Tuesday 08:40 (needs 3, only the 07:00
  shifts reach it: no template starts at 08:40).
