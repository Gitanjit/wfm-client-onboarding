# Litware — 2027-W11 reconciliation (SOW §3)

| key | value |
|---|---|
| intervals_in_week | 504 |
| sla_attainment_priority | 1.000 |
| sla_attainment_standard | 0.986 |
| sla_attainment_email | 1.000 |
| scheduled_hours_total | 758.0 |
| required_hours_total | 527.0 |
| understaffed_interval_hours | 1.3 |
| agents_scheduled | 24 |
| exception_intervals | 42 |
| files_changed | configs/litware.yaml,wfm/ingest/loader.py,wfm/exceptions.py,wfm/scheduler/week.py,wfm/evaluate/metrics.py,wfm/runbook.py,clients/registry.yaml,clients/README.md,docs/clients/litware.md,docs/CHANGELOG.md,docs/ARCHITECTURE.md,tests_unit/test_litware.py,tests_unit/test_registry.py,tests_unit/test_cli_subcommands.py |

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

## This week (2027-W11)

* Weekly attainment target (SOW 1.6) is 0.95 per queue: met on every queue.
* Scheduled / required hours (SOW 1.6): 1.438 against a bound of 1.45 — within.
* Intervals listed under Exceptions (SOW §2.6), left out of attainment and of understaffed_interval_hours: 42.
* SOW §2 rule audit: weekly_hours 0, consecutive_days 0, skill_match 0, no_overlap 0, min_cover 0, rest 0, split_shift 0, breaks 0.
* Breaks starting exactly 5 h after the shift start (inside the 2–5 h window as written): 4.

## Handover note

### What changed and why

1. **Config** (`configs/litware.yaml`). Every figure is the SOW's: three queues (§1.1), the §1.2 targets
   (priority 90/30, standard 80/30, email 80/300), Erlang C without abandonment on each interval's own
   AHT, the 0.85 occupancy cap (§1.3), 07:00–21:00 Europe/London (§1.4), the 20-minute grain (§1.5),
   the 0.95 weekly attainment and the 1.45 hours bound (§1.6), 11 h rest (§2.1), PT-only splits (§2.2),
   max-surplus breaks (§2.3), the priority floor of two (§2.4), no email before 09:00 (§2.5), and the
   standard hour and day caps (§2.9). No service default was changed. Every new behaviour is behind a
   key that only `configs/litware.yaml` sets.
2. **Ingest** (`wfm/ingest/loader.py`). Litware stamps each row with the interval's END. The loader only
   knew `interval_start_local`. Reading the end stamp as a start would have put every interval 20
   minutes late. Rows with `interval_end_local` are converted to UTC with the row's own `utc_offset`
   (the offset in effect at the end, as the README says), then moved back one interval. This also holds
   on the BST change nights.
3. **Infeasible intervals** (`wfm/exceptions.py`, new; §2.6). An interval is listed under Exceptions when
   its required agents exceed the most agents the rules allow on that queue at that time. In practice
   these are the `email` intervals from 07:00 to 09:00 that carry volume: §2.5 allows nobody on email
   then. There are 42 in W11. No other rule is broken to cover them. They stay in the week (in
   `intervals_in_week` and in `required_hours_total`), but they are left out of attainment and out of
   `understaffed_interval_hours`.
4. **Scheduler** (`wfm/scheduler/week.py`, the week planner written for Northwind). New config keys:
   `queue_start` (§2.5: a template may go on email only if it starts at 09:00 or later, so D8, L8, P6b
   and P4); `min_cover_net` (the priority floor of two is held net of breaks as well as gross); and
   `hours_margin` (how close the plan may come to the hours bound; the Northwind default 0.985 is kept).
   For clients with a net floor, the greedy fills floors first, and a repair pass fixes any remaining
   floor gap: it moves one agent onto the gap and rearranges that agent's neighbouring days so that 11 h
   rest still holds. The planner does not plan for §2.6 intervals. Northwind's output is unchanged.
5. **Evaluator and runbook** (`wfm/evaluate/metrics.py`, `wfm/runbook.py`). With `exclude_exceptions`,
   eval.json lists `exceptions` and scores attainment without them. `min_cover` is also audited net of
   breaks. The runbook table takes its queue rows from the config and adds `exception_intervals` and the
   `## Exceptions` section. Every figure in it is the run's own, the same as in eval.json.
6. **Registry and tests.** Litware is added to `clients/registry.yaml` and `clients/README.md` as onboarding
   for 2027-W11. `tests_unit/test_litware.py` pins the ingest, the staffing, the exceptions and the §2 rules.

### Pre-existing deviations from the §1 method affecting Litware's queues (SOW §2.8)

1. **Interval stamping.** The service's export reader assumed rows stamped with the interval start. On
   Litware's end-stamped export every interval's volume would have landed 20 minutes late, with
   requirement and coverage out of step all day. *Fixed* (item 2 above).
2. **Handle time (WFM-198).** The service default `aht_smoothing: queue_mean` staffs every interval on the
   queue's mean AHT. §1.2 requires each interval's own AHT. *Litware uses `interval`.*
3. **Occupancy cap (WFM-212).** The §1.3 cap of 0.85 used to be read but not applied. *It is fixed
   service-wide in the current tree. Litware's requirements include it.*
4. **Attainment denominator.** The default evaluator scores only intervals with volume. §1.6 scores
   operating intervals, minus the §2.6 Exceptions. *Litware uses operating intervals, 07:00–21:00, with
   exceptions excluded.* Email has no volume after 19:00, so those intervals need no staff and are met
   either way. Litware's reported email figure is the same whether email's operating window is read as
   07:00–21:00 or 07:00–19:00.
5. **Cross-skilled cover (PR #31).** The service default credits an agent on another queue with 0.5
   toward a floor. Under §1.2/§2.4 only agents scheduled on the queue count. *Set to 0 for Litware.*
6. **Floors gross of breaks.** The service's `min_cover` (and Northwind's reading of "breaks aside")
   counts agents on shift whether or not they are on break. *For Litware the priority floor of two holds
   both gross and net of breaks.*
7. **Greedy scheduler.** It places breaks at the shift midpoint (not the §2.3 max-surplus rule), has no
   rest rule, and offers the split template to any contract. *Litware uses the week planner.*
8. **Methods kept for other clients and not applied to Litware.** These are the `vendor/qlib` abandonment
   model (Fabrikam), Fabrikam's `attainment_basis: coverage`, Contoso's `sla_target: 0.72` reporting
   threshold, and the service defaults (80/20 targets, a 15-minute grain, UTC). None is used for Litware
   or may be used to report Litware's §1 figures.

### Interpretations to confirm with Litware

1. **§2.6 Exceptions.** These are the email intervals 07:00–09:00 with volume, which §2.5 makes impossible.
   Nothing else in W11 is infeasible.
2. **§2.4 "breaks aside".** The plan meets the floor under either reading: two agents on priority in every
   operating interval, counted with or without those on break.
3. **§2.3 window.** A break may start from 2 h up to and including 5 h after the shift start.
4. **§1.2 "net of breaks".** An agent whose 20-minute break covers an interval is not counted in it.
5. **Standard mornings.** Standard's four misses in W11 (0.986) are all at 08:40 (Mon, Tue, Thu, Fri). Before 09:00 only the 07:00 shift
   (and the PT split from 08:00) can cover, and 11 h rest stops agents who worked until 21:00 the day
   before from starting at 07:00.
