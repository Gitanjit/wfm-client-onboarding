# Litware Support — weekly reconciliation, 2027-W11

| key | value |
|---|---|
| intervals_in_week | 504 |
| sla_attainment_priority | 1.000 |
| sla_attainment_standard | 0.997 |
| sla_attainment_email | 1.000 |
| scheduled_hours_total | 590.0 |
| required_hours_total | 527.0 |
| understaffed_interval_hours | 0.3 |
| agents_scheduled | 23 |
| exception_intervals | 42 |
| files_changed | configs/litware.yaml,configs/northwind.yaml,wfm/ingest/loader.py,wfm/staffing/required.py,wfm/constraints.py,wfm/scheduler/templates.py,wfm/scheduler/greedy.py,wfm/scheduler/improve.py,wfm/evaluate/metrics.py,wfm/runbook.py,wfm/cli.py,docs/clients/litware_handover.md,docs/clients/northwind_handover.md,docs/ARCHITECTURE.md,docs/CHANGELOG.md,clients/registry.yaml,clients/README.md,tests_unit/test_litware.py,tests_unit/test_northwind.py,tests_unit/test_registry.py,tests_unit/test_cli_subcommands.py |

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

Litware is onboarded with its own config, `configs/litware.yaml`. Every Litware rule is an opt-in
config key, and the service defaults (`configs/defaults.yaml`) are unchanged. The code builds on the
Northwind onboarding (2026-W44): the `utc_offset` ingest, per-interval AHT, the occupancy cap,
`queue_hours`, the rest, split-shift and surplus-break rules, the local search and the RUNBOOK writer.
That change is still uncommitted in the working tree, so its files appear in `files_changed` too.

- **Ingest** (`wfm/ingest/loader.py`). Litware stamps each row with the END of its interval. Read as
  a start time, every interval lands 20 minutes late. The loader now recognises `interval_end_local`:
  it computes UTC from the label and the row's `utc_offset` (authoritative, so DST changes are
  handled), then steps back one export interval (`export_interval_minutes: 20`). The `email` queue
  comes from `queues`. `full_week_grid` gives every interval of the week's elapsed length: 504 in a
  normal week, 501 in a spring-forward week, 507 in a fall-back week.
- **Staffing** (config only). Erlang C with no abandonment, on each interval's own volume and AHT
  (`aht_smoothing: interval`), occupancy cap 0.85, and targets 90/30, 80/30 and 80/300 (§1.2–§1.3).
  `queue_hours` sets the requirement to zero outside 07:00–21:00 (§1.4).
- **Scheduling rules.**
  - §2.1 rest 11 h, §2.2 split shifts for PT only, §2.3 surplus break placement: existing switches.
  - §2.4: `min_cover` priority 2 agents, 07:00–21:00, with `cross_skill_weight: 0`. The new
    `min_cover_net` also holds the floor net of breaks, so both readings of "breaks aside" are met.
  - §2.5: new `queue_earliest_start: {email: 9}`. The greedy and the local search never put an email
    shift before 09:00 local (`wfm/scheduler/templates.py: allowed_on`).
  - Templates are single-segment shifts on the hour, 4–8 h, inside 07:00–21:00. Shifts under six
    hours need no break, which lets the small email pool cover 09:00–19:00 without break gaps.
- **Local search** (`wfm/scheduler/improve.py`). Fixed a defect: when the greedy left a week over
  the `max_hours_ratio` bound, every move was rejected, including moves that cut hours. Litware's
  greedy week came out at 1.48× against a bound of 1.45, with three priority-floor gaps, and the
  search could not fix either. Now a week over the bound may only come down. A broken floor is
  scored per missing agent, so a move that mends part of a gap is kept. Contoso, Fabrikam and
  Northwind produced byte-identical schedules and evals for all 77 data weeks before and after this
  fix.
- **§2.6 exceptions** (`wfm/constraints.py: exceptions`, `exceptions: true`). An operating interval
  with a requirement that the rules make impossible to meet is listed. That means email before 09:00
  (contacts arrive from 07:00, staffing is barred until 09:00), or a requirement above the number of
  agents holding the skill. These intervals are left out of attainment and understaffing, as §1.6
  and §3 require. They stay in `intervals_in_week` and in the required hours. The local search
  ignores them, and no rule is broken to cover them.
- **Evaluation and report** (`wfm/evaluate/metrics.py`, `wfm/runbook.py`). `eval.json` carries
  `exception_intervals` and the list of exceptions, and audits §2.5 (`queue_start`) and the net
  floor. Attainment is over every operating interval, 07:00–21:00 on all three queues, leaving out
  exceptions. Email's 19:00–21:00 intervals carry no volume and are met. The RUNBOOK adds the
  `exception_intervals` row and the `## Exceptions` section. The table is filled from the run's own
  `eval.json`, so the two always agree.
- **Northwind** (`configs/northwind.yaml`). `min_cover_net: true`, so the §2.6 vip floor also holds
  net of breaks, and `improve_margin: 0.03`. Rerun for 2026-W42 to 2027-W10: every queue is at or
  above its previous attainment, zero violations, and hours 1.14–1.17× required against 1.57.
- **Registry and tests.** `clients/registry.yaml` and `clients/README.md` list Litware as
  `onboarding` (go-live 2027-W11). Added `tests_unit/test_litware.py`. The two registry/CLI tests that
  count clients were updated.

### SOW §2.8: pre-existing deviations from the §1 method affecting Litware's queues

These are deviations in the service as it stood before this change (the last commit). Litware's
config overrides each one; the defaults still carry them for every client that does not.

1. **Occupancy cap not applied (WFM-212).** In the committed code, `occupancy_cap` is read but never
   passed to the Erlang C call, so §1.3 is not honoured. The fix is in the working tree (Northwind
   onboarding) and applies to every client.
2. **Smoothed AHT (WFM-198).** The default `aht_smoothing: queue_mean` staffs every interval on the
   queue's mean AHT. §1.2 requires each interval's own AHT. In the committed code `interval` also
   averaged. Litware runs on the fixed `interval` option.
3. **Attainment counted only intervals with volume.** The default counts only intervals with
   volume; §1.6 counts every operating interval. Litware uses `attainment_intervals: operating`.
4. **Cross-skilled cover counted at 0.5 toward floors (PR #31).** The default lets an agent on
   another queue count half toward a floor. §1.2 counts a person once, on the queue they are
   scheduled on. Litware sets `cross_skill_weight: 0` for its priority floor.
5. **Ingest.** The committed loader ignores `utc_offset`, hard-codes the queues to priority and
   standard (so `email` would be dropped), and reads every export row as an interval start. Litware's
   rows are interval ends, so without this change every Litware interval lands 20 minutes late.
6. **No requirement mask outside operating hours.** Required staffing is computed for every interval
   that carries volume, whatever the hour, unless a client sets `queue_hours`. Litware sets it for
   07:00–21:00 (§1.4).
7. **Service SLA defaults.** 80/20 on priority and standard, with a 0.90 weekly verdict. Litware
   overrides these with 90/30, 80/30 and 80/300, and 0.95.
8. **Not on Litware's path, but deviations from the same method that need an owner.**
   - `vendor/qlib` 1.3 defaults to 90 s patience, so Fabrikam (`queueing: qlib`) is staffed on an
     abandonment model, not Erlang C.
   - Fabrikam's attainment is reported on `coverage` (PR #47).
   - Contoso's `sla_target: 0.72` is a "temporary" override pending WFM-212.
   - The WIP `wfm/scheduler/greedy_v2.py` (WFM-231) has an inverted `_rested` check.

### Data notes for Litware's WFM contact

- Email contacts arrive from 07:00, but §2.5 bars email staffing before 09:00. Each 07:00–09:00
  interval with email volume, six a day and 42 a week in 2027-W10 and 2027-W11, is reported under
  Exceptions. Please confirm whether email should open at 09:00, or whether §2.5 should change.
- The roster has five email-skilled agents (four FT, one PT), at most 184 hours a week.
