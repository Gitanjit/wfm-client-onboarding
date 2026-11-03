# Litware Support — weekly reconciliation report, 2027-W11

| key | value |
|---|---|
| intervals_in_week | 504 |
| sla_attainment_priority | 1.000 |
| sla_attainment_standard | 0.980 |
| sla_attainment_email | 1.000 |
| scheduled_hours_total | 740.0 |
| required_hours_total | 527.0 |
| understaffed_interval_hours | 4.3 |
| agents_scheduled | 24 |
| exception_intervals | 42 |
| files_changed | configs/litware.yaml,wfm/ingest/loader.py,wfm/constraints.py,wfm/scheduler/week.py,wfm/evaluate/metrics.py,wfm/report/runbook.py,wfm/cli.py,clients/registry.yaml,clients/README.md,docs/LITWARE_HANDOVER.md,docs/ARCHITECTURE.md,docs/CHANGELOG.md,tests_unit/test_litware.py,tests_unit/test_registry.py,tests_unit/test_cli_subcommands.py |

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

**What changed and why (Litware onboarding, go-live 2027-W11).**

- `configs/litware.yaml` (new): every Litware SOW term written as client config. The service
  defaults (`configs/defaults.yaml`) are unchanged. 20-minute grain, Europe/London, operating hours
  07:00–21:00 with no staff required outside them, queues priority/standard/email, the §1.2 targets
  (90/30, 80/30, 80/300), occupancy cap 0.85, each interval's own AHT, Erlang C with no abandonment,
  attainment over every operating interval minus the §2.6 exceptions, efficiency cap 1.45, and
  priority cover of two agents net of breaks (§2.4), with a cross-skilled agent counting only on the
  queue they are scheduled on. Planning uses the week scheduler: 11 h rest, split shifts for PT only,
  surplus breaks, nobody on `email` before 09:00 (§2.5, new key `queue_earliest_start`). Templates:
  D8, L8, P6a, P6b and P4, the templates in ARCHITECTURE that fit 07:00–21:00. S44 is not planned.
- `wfm/ingest/loader.py`: Litware's export stamps each row with the **end** of its interval. A
  start-stamped reader would put all demand 20 minutes late, so `interval_end_local` exports are
  read as end-stamped. UTC is taken from the end stamp and its own `utc_offset`, minus one interval,
  which stays right across a DST change.
- `wfm/constraints.py`, `wfm/evaluate/metrics.py`: §2.6 exceptions are intervals that have a
  requirement which no allowed shift can cover. For Litware that means `email` 07:00–09:00, which
  §2.5 leaves unstaffable while §1.4 has email arriving from 07:00. They are listed below and left
  out of attainment and understaffed hours. They stay in the week and in required hours. eval.json
  now carries `exceptions`, `exception_intervals` and a `queue_start` audit.
- `wfm/scheduler/week.py`: the email start rule; a targeted two-agent move, which hands a short
  interval to an agent whose rest, hours or consecutive-day limit blocked them by moving one of
  their shifts to someone else; and a preference for break intervals strictly inside the 2–5 h
  window, which the search ranks after the weekly attainment target.
- `wfm/report/runbook.py`, `wfm/cli.py`: this report is written on every Litware run, straight from
  the same evaluation that writes eval.json, so the two always agree.
- Registry, README, ARCHITECTURE, CHANGELOG and unit tests updated for the new client.

**Pre-existing deviations from the SOW §1 method (§2.8).** These were in the service before this
change. Litware's config overrides each one, so none affects the figures above:

1. Handle time: the service default `aht_smoothing: queue_mean` (WFM-198) staffs every interval on
   the queue's mean AHT, not on the interval's own AHT (§1.2). Litware uses `interval`.
2. Occupancy cap: in release 0.4.1 the 0.85 cap was read from config and never applied (WFM-212).
   It is applied now. At Litware's volumes in W10–W11 it never binds, so the §1.2 test (agents ≥
   the required number) gives the same result as the test "Erlang C service level ≥ target".
3. Person counts once: the service default `cross_skill_weight: 0.5` (PR #31) counts an agent on
   another queue as half an agent toward a floor. Litware sets 0, so priority cover counts only
   people scheduled on `priority`.
4. Attainment base: by default the evaluator counts only intervals with volume, not every operating
   interval (§1.6). It also keeps only the intervals present in the file, not the full ISO week.
   Litware uses `attainment_intervals: operating` and `week_grid: full`.
5. Export time stamps: the export reader assumed start-stamped rows (see above). Fixed for
   end-stamped exports.
6. Not applied to Litware: Fabrikam's staffing goes through the vendored `qlib` abandonment model
   and its attainment is reported on coverage (PR #47), and Contoso's `sla_target` is lowered to
   0.72. All three are other clients' config only. They do not touch Litware's queues and are listed
   so they are not copied.
