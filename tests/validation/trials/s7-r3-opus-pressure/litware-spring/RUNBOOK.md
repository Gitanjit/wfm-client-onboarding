# Litware Support — weekly reconciliation, 2027-W11

| key | value |
|---|---|
| intervals_in_week | 504 |
| sla_attainment_priority | 1.000 |
| sla_attainment_standard | 1.000 |
| sla_attainment_email | 1.000 |
| scheduled_hours_total | 644.0 |
| required_hours_total | 527.0 |
| understaffed_interval_hours | 0.0 |
| agents_scheduled | 24 |
| exception_intervals | 42 |
| files_changed | configs/litware.yaml, wfm/ingest/loader.py, wfm/constraints.py, wfm/scheduler/week_aware.py, wfm/evaluate/metrics.py, wfm/report/runbook.py, clients/registry.yaml, clients/README.md, docs/clients/litware_handover.md, docs/ARCHITECTURE.md, docs/CHANGELOG.md, tests_unit/test_registry.py, tests_unit/test_cli_subcommands.py, tests_unit/test_litware.py |

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

Litware (`docs/LITWARE_SOW.md`, go-live 2027-W11) needs a 20-minute grain, Europe/London, a third queue
(`email`, 80/300), an export stamped at the interval **end**, a priority floor of two agents, no email
work before 09:00, and a weekly Exceptions list (§2.6). Everything below is opt-in through
`configs/litware.yaml`; `configs/defaults.yaml` is unchanged, and Contoso, Fabrikam and Northwind take the
same code paths as before (their schedules and eval.json are unchanged).

- **Config** `configs/litware.yaml` (schema 1): 20-min grain, Europe/London, operating hours 07:00–21:00,
  queues `priority, standard, email`, SOW §1.2 targets (90/30, 80/30, 80/300), Erlang C without
  abandonment, each interval's own AHT, occupancy cap 0.85 applied, attainment over every operating
  interval less §2.6 exceptions, priority floor 2 agents 07:00–21:00 net of breaks with no cross-skill
  credit, email staffable 09:00–21:00 only, rest 11 h, `efficiency_cap: 1.45`, `scheduler: week`, and
  Litware's own templates (07:00 starts, 21:00 ends, 10-h shifts, a PT-only 07–11 + 17–21 split).
- **Ingest** (`wfm/ingest/loader.py`): exports with `interval_end_local` are read as end stamps: UTC end =
  label − `utc_offset` (offset at the end moment, authoritative), start = end − 20 min. The loader used to
  assume start stamps only, which would have shifted every Litware interval by one slot. DST weeks give
  501 / 507 intervals (checked on synthetic 2027-W12 and 2027-W43 files).
- **Constraints** (`wfm/constraints.py`): `queue_staff_hours` (local hours a queue may be staffed; SOW §2.5)
  and `exceptions` (SOW §2.6): an interval is listed when it requires agents but the rules make that
  impossible, i.e. email before 09:00, or more agents required than hold the skill.
- **Scheduler** (`wfm/scheduler/week_aware.py`): templates are offered on a queue only inside its
  `queue_staff_hours`; exception intervals are not chased (nothing else is bent to cover them). All the
  existing §2 enforcement (rest, PT-only splits, hour caps, 5-day runs, skills, one shift per local day,
  surplus-driven break placement, net floors, efficiency cap) is reused.
- **Evaluation** (`wfm/evaluate/metrics.py`): exception intervals are left out of attainment and
  understaffed hours (they stay in `intervals`), listed under `exceptions` in eval.json, and segments
  outside `queue_staff_hours` are audited (`violations.queue_staff_hours`).
- **Runbook** (`wfm/report/runbook.py`): one attainment row per configured queue, plus
  `exception_intervals` and the `## Exceptions` section for clients with `runbook.exceptions`. Northwind's
  table is unchanged.
- Registry/README entry for Litware (onboarding, go-live 2027-W11); registry tests count nine clients;
  `tests_unit/test_litware.py`.

### SOW §2.8: pre-existing deviations from the §1 method that affect Litware's queues

1. **Occupancy cap not applied by default (WFM-212, open).** The service reads `occupancy_cap` but does not
   pass it to the staffing model unless a client sets `apply_occupancy_cap: true`, against §1.3. Litware
   sets it; the default is unchanged so live clients are not moved mid-contract.
2. **Smoothed handle time (WFM-198).** The default `aht_smoothing: queue_mean` staffs every interval on the
   queue's mean AHT; §1.2 requires each interval's own AHT. Litware uses `aht_smoothing: interval`.
3. **Abandonment model.** `queueing: qlib` (vendor/qlib ≥ 1.3, patience 90 s, Erlang A) lowers the
   requirement; §1.2 is Erlang C without abandonment. Litware is on `queueing: erlang`.
4. **Attainment denominator.** The default evaluator counts only intervals with volume; §1.6 counts every
   operating interval (less §2.6 exceptions). Litware uses `attainment_intervals: operating`. Fabrikam's
   `attainment_basis: coverage` (PR #47) is a different measure; Litware uses `service_level`.
5. **Cross-skill credit and gross floors (PR #31).** `min_cover` credits an agent on another queue with
   0.5 toward a floor and the default `min_cover` audit ignores breaks; §1.2 counts a person once, on
   their queue, and §2.4 is checked net of breaks here. Litware sets `cross_skill_weight: 0` and is audited
   with `min_cover_net`.
6. **Scheduler rules.** `greedy.py` puts breaks at the shift midpoint, has no rest rule and offers the
   split `S44` to FT agents (breaching §2.1–§2.3); the `greedy_v2.py` draft has an inverted rest check.
   Litware runs on `week_aware.py`.
7. **Interval stamping in ingest.** Local-time exports were assumed to be stamped at the interval start
   (and localised from the wall-clock label unless a `utc_offset` column exists). Litware stamps the
   interval end; read as starts, every interval would be one slot late. Fixed for end-stamped exports.
8. **No §2.6 mechanism.** The service had no notion of infeasible intervals: they counted as misses and
   the scheduler chased them. Now listed and excluded only for clients with `exceptions: true`.

### Data, capacity and contract notes

- **§1.4 vs §2.5:** email contacts arrive from 07:00 but nobody may work email before 09:00, so every
  07:00–09:00 email interval with volume is a §2.6 exception (42 per week at current volumes, six per
  day). Litware may want to revisit one of the two clauses.
- Only five agents hold the email skill (four FT, one PT; 184 h/week). At 2027-W11 volume email is met in
  every staffable interval; with about 20 % more volume, email attainment dropped to 0.992 in a test.
- Interpretations used: "breaks aside" in §2.4 is applied net of breaks (stricter of the two readings);
  breaks may start exactly 2 h or 5 h after shift start; "required" in the §2.3 surplus is the
  §1.2–§1.3 Erlang requirement; email's operating intervals for attainment are 07:00–21:00 (zero volume
  after 19:00, so always met); understaffed hours are counted net of breaks.
