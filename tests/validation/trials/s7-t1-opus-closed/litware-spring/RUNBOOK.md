# Litware — weekly reconciliation, 2027-W11

| key | value |
|---|---|
| intervals_in_week | 504 |
| sla_attainment_priority | 1.000 |
| sla_attainment_standard | 1.000 |
| sla_attainment_email | 1.000 |
| scheduled_hours_total | 742.0 |
| required_hours_total | 527.0 |
| understaffed_interval_hours | 0.0 |
| agents_scheduled | 24 |
| exception_intervals | 42 |
| files_changed | configs/litware.yaml, clients/README.md, clients/registry.yaml, docs/ARCHITECTURE.md, docs/CHANGELOG.md, docs/clients/litware.md, docs/clients/litware_handover.md, tests_unit/test_cli_subcommands.py, tests_unit/test_litware.py, tests_unit/test_registry.py, wfm/cli.py, wfm/evaluate/metrics.py, wfm/infeasible.py, wfm/ingest/loader.py, wfm/report/reconciliation.py, wfm/scheduler/week.py |

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

Litware (`docs/LITWARE_SOW.md`) is onboarded with its own config, `configs/litware.yaml`. Every key in it
is the SOW's figure or rule. `configs/defaults.yaml` is untouched, and Contoso, Fabrikam, Wingtip and
Northwind produce byte-identical `schedule.csv`, `eval.json` and (Northwind) `RUNBOOK.md`/`exceptions.md`
before and after. Litware reuses what Northwind brought in (week scheduler, per-interval AHT, occupancy cap,
strict operating hours, net floors, reconciliation report) and adds:

- **Ingest** (`wfm/ingest/loader.py`). Litware stamps each row with the local wall-clock END of its
  20-minute interval (`interval_end_local`, SOW §1.5, `data/litware/README.txt`). UTC end comes from the
  row's own `utc_offset`, then the interval start is one interval earlier. Before this, the export reader
  took every label as an interval start, which would have shifted all Litware demand 20 minutes late.
  The grid is the full ISO week in Europe/London, elapsed (501 intervals in a spring-forward week, 507 in a
  fall-back week). Off-grid ends snap to the nearest interval end and exact duplicates are dropped, both with a warning.
- **Email start** (§2.5): `queue_start_hours: {email: 9}`. The scheduler never puts anyone on email before
  09:00 local (email shifts are D8, L8, P6b or P4), and the evaluator audits it (`queue_start`).
- **Infeasible intervals** (§2.6, new `wfm/infeasible.py`). An operating interval that needs agents and that
  no allowed shift can staff on its queue (or that needs more agents than hold the skill) is listed under
  Exceptions. Every week that means the email intervals 07:00–09:00 local that have contacts (§1.4 says email
  arrives from 07:00, §2.5 says nobody may be on email before 09:00). They stay in the week and in required
  hours (§1.6), and they are left out of attainment and `understaffed_interval_hours`, as §1.6 and §3 define
  them. No rule is broken to cover them.
- **Priority cover** (§2.4): `min_cover: {priority: {agents: 2, hours: [7, 21]}}`, counted on the queue
  and net of breaks, so it holds whichever way "breaks aside" is read.
- **Templates** (§2.10): D8, L8, P6a, P6b, P4 (ARCHITECTURE, "Templates per client"). E8 and N8 fall
  outside 07:00–21:00. S44 is not used, which avoids any doubt about breaks on a 4 h + 4 h split. The
  PT-only split rule (§2.2) is enforced anyway (`split_shift_contracts: [PT]`).
- **Scheduler search** (`wfm/scheduler/week.py`). The anneal can also move shifts between queues
  (`anneal_cross_queue`). Without it, a shared priority/standard agent's late shift could block an
  early standard start under the 11 h rest rule. `edge_break_weight` makes the search prefer breaks
  strictly inside the 2–5 h window wherever that costs no attainment. Every break still starts within the
  window, in a 20-minute interval of largest gross surplus (§2.3). The efficiency bound (§1.6, 1.45 ×
  required hours) is a hard limit.
- **Report** (`wfm/report/reconciliation.py`, `reconciliation_exceptions_section`). This RUNBOOK, with the
  `exception_intervals` key and the `## Exceptions` list, recomputed from the run's own required curve and
  schedule; `eval.json` reports attainment on the same definition. `exceptions.md` (§2.7) is written next
  to it. This week no target is missed with the roster provided.
- Registry (`onboarding`, go-live 2027-W11), client note `docs/clients/litware.md`, ARCHITECTURE,
  CHANGELOG, unit tests (`tests_unit/test_litware.py`).

### SOW §2.8: pre-existing deviations from the §1 method that affect Litware's queues

These were in the service before Litware. Each is corrected for Litware in `configs/litware.yaml` or in
code as noted. The service defaults and the clients that do not opt in still behave this way:

1. **Occupancy cap not applied (WFM-212, open).** The default reads `occupancy_cap` but does not pass it to
   Erlang C, against §1.3. Litware sets `enforce_occupancy_cap: true`.
2. **Smoothed handle time (WFM-198).** By default, required staffing uses the queue's mean AHT, not each
   interval's own AHT as §1.2 requires. Litware uses `aht_smoothing: interval`.
3. **Service-level targets.** The defaults are 80/20 on priority and standard and nothing for email.
   Litware's 90/30, 80/30 and 80/300 come from §1.2 in its config.
4. **Attainment denominator.** By default the evaluator counts only intervals with volume. §1.6 counts
   every operating interval (07:00–21:00) apart from those reported under §2.6. Litware uses
   `attainment_intervals: operating` with `attainment_exclude_exceptions: true`.
5. **Cross-skilled cover (PR #31).** By default an agent on another queue who holds the skill counts 0.5
   toward a floor, and floors are checked gross of breaks. §1.2 counts a person once, on the queue they are
   scheduled on. Litware sets `cross_skill_weight: 0` and `min_cover_net: true`.
6. **Ingest of interval-end exports.** The export reader assumed interval-start labels (Fabrikam's
   layout), and without `utc_offset` it localised wall-clock labels. Litware's end-stamped rows would have
   landed one interval late. Fixed in code for exports with `interval_end_local`.
7. **Operating hours.** By default staff are required for any interval with volume, inside operating
   hours or not (§1.4). Litware sets `operating_hours_strict: true`.
8. **Breaks at the shift midpoint and no rest rule** (`greedy.py`, the default scheduler). These are §2
   rules, but they change net cover and so the measured service level. Litware uses `scheduler: week`.

Not affecting Litware: the vendored abandonment model (`queueing: qlib`) and `attainment_basis: coverage`
are Fabrikam's only, and §1.2 has no abandonment. Contoso's `sla_target: 0.72` is a temporary evaluator
threshold tied to WFM-212. None of them is set for Litware.
