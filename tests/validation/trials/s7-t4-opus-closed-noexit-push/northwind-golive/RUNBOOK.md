# Northwind Traders — 2026-W44 reconciliation (SOW §3)

| key | value |
|---|---|
| intervals_in_week | 338 |
| sla_attainment_priority | 1.000 |
| sla_attainment_standard | 1.000 |
| sla_attainment_vip | 0.911 |
| scheduled_hours_total | 1674.0 |
| required_hours_total | 1115.5 |
| understaffed_interval_hours | 14.0 |
| agents_scheduled | 51 |
| files_changed | configs/northwind.yaml,wfm/ingest/loader.py,wfm/staffing/required.py,wfm/scheduler/week.py,wfm/cli.py,wfm/evaluate/metrics.py,wfm/runbook.py,clients/registry.yaml,clients/README.md,docs/clients/northwind.md,docs/CHANGELOG.md,docs/ARCHITECTURE.md,tests_unit/test_northwind.py,tests_unit/test_registry.py,tests_unit/test_cli_subcommands.py |

## This week (2026-W44)

- Weekly attainment target (SOW 1.6) is 0.95 per queue: **not met on vip** (vip 0.911). See "VIP attainment" below: this is a staffing shortfall, not a scheduling defect.
- Scheduled / required hours (SOW 1.6): 1.501 against a bound of 1.57 — within.
- SOW §2 rule audit: weekly_hours 0, consecutive_days 0, skill_match 0, no_overlap 0, min_cover 0, rest 0, split_shift 0, breaks 0.
- Breaks starting exactly 5 h after the shift start (inside the 2–5 h window as written): 7.
- Export rows off the 30-minute grid, folded into the interval they fall in: 2026-10-27 10:01 priority; 2026-10-29 10:01 standard. Report to Northwind's WFM contact.

## Handover note

### What changed and why

- **Config** (`configs/northwind.yaml`). Every figure is the SOW's: three queues, the §1.2 targets, the 0.85
  occupancy cap, per-interval AHT, 30-minute grain in America/Chicago, the vip operating window
  (08:00–20:00) for attainment, the vip floor (§2.6), 11 h rest, PT-only splits, max-surplus breaks, the
  0.95 weekly attainment target and the 1.57 hours bound. No service default was changed.
- **Ingest** (`wfm/ingest/loader.py`). The `utc_offset` column is now authoritative when an export has
  one. Before, UTC was derived from the wall-clock label, which cannot tell the two 01:00 and 01:30 rows of
  the fall-back night (2026-11-01) apart. The queue list comes from the config (`queues`), because the
  hard-coded `priority, standard` dropped `vip`. With `full_week_grid` the week is every 30-minute
  interval from local Monday 00:00 to the next Monday 00:00 (338 in W44), not whatever rows arrive.
- **Staffing** (`wfm/staffing/required.py`). WFM-212 fixed: the occupancy cap is now passed to the
  staffing model, for every client. Contoso, Fabrikam and Wingtip schedules and evals are byte-identical
  before and after on 2026-W42/W43, because the cap never binds at their volumes. `aht_smoothing: interval`
  now really uses each interval's AHT. It used to fall back to the queue mean.
- **Scheduler** (`wfm/scheduler/week.py`, selected by `scheduler: week`). This is a new week-aware planner.
  The greedy in `greedy.py` has no rest rule, offers the split template to any contract, places breaks at
  the shift midpoint and plans one day at a time, which uses up the 11 vip agents before the weekend. The
  new planner enforces §2.1–§2.6 while placing shifts. It plans the scarce `vip` queue first: it picks a
  template mix per day under the break rule, chooses across days within the 440 h the vip agents have,
  and assigns agents within the rules. A greedy then fills the other queues, and a local search follows.
  Total hours stay within 1.57 × required. The other clients still use `greedy.py`, unchanged.
  `greedy_v2.py` (the WFM-231 draft) is not used. Its `_rested` check is inverted (it passes shifts with
  *less* than the minimum rest), so it should be fixed before anyone wires it in.
- **Evaluator** (`wfm/evaluate/metrics.py`). With `attainment_intervals: operating`, attainment counts
  every operating interval of the queue (§1.6), not only intervals with volume. eval.json adds
  `required_hours` and `hours_ratio`, plus `rest`, `split_shift` and `breaks` audits when a client's config
  sets those rules. Other clients' eval.json is unchanged.
- **Runbook** (`wfm/runbook.py`). Every Northwind run writes this file. The table is computed from the
  run, with the same figures as eval.json.

### Pre-existing deviations from the §1 method affecting Northwind's queues (SOW §2.8)

1. **Handle time (WFM-198).** The service staffs on the queue's *mean* AHT (`aht_smoothing: queue_mean`).
   §1.2 requires each interval's own AHT. Even `aht_smoothing: interval` used the mean. *Fixed for
   Northwind* (per-interval AHT; the mode now does what it says).
2. **Occupancy cap not applied (WFM-212).** §1.3's 0.85 cap was read but never passed to the staffing
   model. *Fixed service-wide.*
3. **Attainment denominator.** The evaluator scored only intervals with volume. §1.6 scores every
   operating interval. *Northwind uses operating intervals.* Other clients keep the old basis.
4. **Ingest timezone and queues.** UTC came from local labels (wrong or ambiguous on DST nights; see
   `docs/incidents/2025-11-05-woodgrove-dst-fall-back-ingest.md`), the week grid came from the rows
   delivered, and only `priority`/`standard` were read. *Fixed* as above.
5. **Breaks, rest and split shifts.** The greedy scheduler places breaks at the shift midpoint (§2.3 says
   the largest gross surplus in the 2–5 h window), has no rest rule (§2.1), and offers S44 to every
   contract (§2.2). *Northwind uses the week planner.*
6. **Cross-skilled cover (PR #31).** `min_cover` credits an agent on another queue with 0.5 toward a
   floor. Under §1.2/§2.6 only agents scheduled on the queue count, so a `priority;vip` agent on
   priority must not count toward the vip floor. *Set to 0 for Northwind.*
7. **Methods kept for other clients and not applied to Northwind.** The `vendor/qlib` abandonment model
   (Fabrikam, `queueing: qlib`) gives lower requirements than Erlang C. §1.2 says no abandonment.
   Fabrikam's `attainment_basis: coverage` (PR #47) gives partial credit for understaffed intervals.
   Contoso's `sla_target: 0.72` override is a reporting threshold. None of these is used for Northwind,
   and none may be used to report Northwind's §1 figures.

### VIP attainment: the §1.6 target cannot be met with the current roster

Only 11 agents hold `vip`, all full-time: at most 440 vip agent-hours a week. I enumerated every daily
mix of the allowed templates with breaks placed by §2.3. Reaching 0.95 on vip (at most 8 missed
operating intervals out of 168) needs at least about **472 vip agent-hours in W44** (478 in W42, 462 in
W43). That bound ignores the rest and consecutive-day rules, which only push it higher. Within 440 h the
floor is about 13 missed intervals (≈ 0.92). This planner reaches 15 in W44 (0.911); W42 and W43 come
out at 0.899 and 0.911. Priority and standard are at 1.000, and total hours stay within the 1.57 bound.

Before the go-live review, the account team needs to decide one of these:
- add vip-skilled agents (one more full-time vip agent gives 480 h, enough in principle; two give margin);
- cross-train some of the 26 priority/standard agents on `vip`;
- agree a variation to §1.6 for vip with Northwind.

I did not lower any target, count cross-skilled agents, switch to the abandonment model or change the
attainment basis to make the number pass.

### Interpretations to confirm with Northwind

- **§2.6 "breaks aside".** I read this as: the floor counts agents on shift on `vip`, and a break does not
  break the floor (the same as how the service's `min_cover` works). Every interval 06:00–24:00 has at
  least one vip agent on shift. A vip interval that needs agents and loses one to a break counts as a §1.2
  miss.
- **§2.3 window.** A break may start from 2 h up to and including 5 h after the shift start, and the
  largest surplus is taken over that window. Where a non-edge interval is tied, the planner uses it. The
  "This week" section counts the breaks that start exactly at 5 h. In W44 no rule-compliant vip plan avoids
  them entirely (Friday's E8/L8 shapes force them).
- **§1.2 "net of breaks".** An agent whose 20-minute break overlaps an interval is not counted in that
  interval.

### Data

- The W44 export has two rows stamped `10:01` instead of `10:00` (Tue 27 Oct priority, Thu 29 Oct
  standard). Ingest folds them into the 10:00 interval. Report this to Northwind's WFM contact.
- W44 has 338 half-hour intervals (fall-back on 2026-11-01). Both 01:00 and 01:30 local rows appear twice,
  with offsets −05:00 and −06:00.
