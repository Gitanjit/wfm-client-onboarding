# Northwind Traders: weekly reconciliation, 2026-W44

| key | value |
|---|---|
| intervals_in_week | 338 |
| sla_attainment_priority | 1.000 |
| sla_attainment_standard | 1.000 |
| sla_attainment_vip | 0.917 |
| scheduled_hours_total | 1688.0 |
| required_hours_total | 1115.5 |
| understaffed_interval_hours | 15.5 |
| agents_scheduled | 51 |
| files_changed | configs/northwind.yaml, wfm/ingest/loader.py, wfm/staffing/required.py, wfm/scheduler/search.py, wfm/scheduler/templates.py, wfm/evaluate/metrics.py, wfm/reconcile.py, wfm/cli.py, clients/registry.yaml, clients/README.md, docs/clients/northwind.md, docs/ARCHITECTURE.md, docs/CHANGELOG.md, tests_unit/test_northwind.py, tests_unit/test_cli_subcommands.py, tests_unit/test_registry.py |

## Handover note

**What changed and why.** Northwind is the first client whose contract the service could not plan
for as it stood. Every change is opt-in from `configs/northwind.yaml`. `configs/defaults.yaml` is
untouched, and Contoso, Fabrikam and Wingtip produce byte-identical `schedule.csv` and `eval.json`
(checked on 2026-W41 to W43).

- *Ingest* (`wfm/ingest/loader.py`): the queue list comes from config (`queues`). Before this change
  `vip` was silently dropped. When an export has a `utc_offset` column, UTC is taken from it. The old
  path localised the wall-clock label, which gets the repeated 01:00/01:30 on the fall-back night
  (Sun 2026-11-01) wrong. With `full_week_grid` the week is always the calendar week in local time
  (338 intervals in W44). Missing intervals come back with zero volume and a warning, rows outside
  the week are dropped, and duplicate queue/interval rows are dropped with a warning.
- *Staffing* (`wfm/staffing/required.py`): SOW 1.2 says Erlang C with each interval's own volume
  and AHT. SOW 1.3 sets the 0.85 occupancy cap. `aht_smoothing: interval` now really uses each
  interval's AHT; before, it was ignored and the queue mean was always used. `apply_occupancy_cap: true`
  applies the cap (WFM-212). `queue_hours` zeroes the requirement outside a queue's hours (vip 08–20).
- *Scheduler* (`wfm/scheduler/search.py`, `scheduler: search`): a week-level, seeded, deterministic
  local search. It replaces the per-day greedy, which cannot enforce SOW 2. It enforces 11 h rest
  (2.1), split shifts for PT only (2.2), one 20-min break per shift of 6 h or more in the
  max-gross-surplus interval of the 2–5 h window (2.3), the standard rules (2.4), local templates
  (2.5), and at least one agent on vip 06:00–24:00 net of breaks (2.6). It plans to 98 % of the
  1.57 × required-hours bound (1.6).
- *Evaluator* (`wfm/evaluate/metrics.py`): for Northwind, attainment is over each queue's operating
  intervals (SOW 1.6, `attainment_scope: operating_hours`), not over intervals with volume.
  eval.json adds required hours, the efficiency ratio and audits of every SOW 2 rule (rest,
  split_shift, breaks, templates, one_shift_per_day, min_cover_net). `wfm/reconcile.py` writes this
  file and `exceptions.md` on every run.

**Exception raised (SOW 2.7): `vip` attainment.** The 0.95 weekly target for vip cannot be met with
the roster provided, when attainment is measured as SOW §1 defines it. Only 11 agents hold the vip skill, all
full-time, so vip has at most 440 agent-hours a week. vip needs 3–7 agents in every interval
08:00–20:00 (about 306 h in W44) plus SOW 2.6's one agent from 06:00–08:00 and 20:00–24:00
(42 h). The only shapes are the 8 h/6 h/4 h templates, and only E8/P6a cover 08:00–09:00. Even
ignoring breaks, rest and per-agent limits, at most 8 failing intervals (0.95 of 168) needs about
486 vip hours in W44. The best a relaxed bound allows with 440 h is about 13 failing intervals
(0.923). The schedule reaches 0.917 (14 intervals, mostly 08:00/08:30). Priority and standard meet
their targets with hours to spare, so the fix is roster, not hours. Two or more vip-skilled agents
(or vip skill for existing priority agents) would close the gap. The WFM lead's "sufficient" check
was most likely made with the service's old method (queue-mean AHT, no occupancy cap, cross-skilled
agents counting toward floors), which understates vip need. To raise with the account team.

**Pre-existing deviations from the SOW §1 method (SOW 2.8).** These are in the service as it stood
before onboarding and would affect Northwind's queues. Each is neutralised for Northwind by its config.
The service-wide ones are still open for other clients:
1. WFM-212: the occupancy cap (`occupancy_cap: 0.85`) is read but not applied in required staffing.
   SOW 1.3 is broken without the opt-in. Still open for every other client.
2. WFM-198: required staffing uses the queue's mean AHT (`aht_smoothing: queue_mean`, the default),
   not the interval's own AHT as SOW 1.2 requires. The `interval` setting was also ignored by the
   code. Fixed in code; the default is unchanged.
3. The evaluator counts attainment over intervals with volume, not over operating intervals
   (SOW 1.6). For vip the operating intervals are 08:00–20:00.
4. PR #31: an agent on another queue holding the floor queue's skill counts 0.5 toward a floor
   (`cross_skill_weight`). SOW 1.2 says a person counts once, on the queue they are scheduled on.
   Northwind sets 0.
5. The loader derived UTC from the local label and the zone rules, ignoring `utc_offset`. The fall-back
   night's repeated hour would be misread. It also kept only `priority` and `standard`, so vip would be lost.
6. `sla_target` defaults to 0.90 (and Contoso runs a temporary 0.72); SOW 1.6 sets 0.95.
7. Not used for Northwind but in the service: `queueing: qlib` (abandonment model, Fabrikam) and
   `attainment_basis: coverage` (partial credit, Fabrikam PR #47) both depart from SOW 1.2.
8. Scheduling rules the old planner broke for this contract: no rest rule, `S44` open to full-time
   agents (template eligibility `all`), breaks at the shift midpoint, per-day planning. The WFM-231
   draft (`greedy_v2.py`) has its rest test inverted (`<` instead of `>=`) and is still not wired in.

**Interpretations to confirm with Northwind.**
- A break may start exactly 5 h after the shift starts: the 2–5 h window includes its end. On some days
  no shape lets the vip E8 shift's maximum surplus fall inside, because gross vip cover is the same at
  10:00, 10:30 and 11:00. The search prefers inside slots whenever one ties.
- SOW 2.6 is met net of breaks as well as gross.
- `S44` (split, 4+4 h) is not used. Whether a 4+4 split is a "shift of six hours or more" for SOW 2.3
  is not stated, and part-time agents are covered by P4/P6a/P6b.
- "Scheduled on queue" in `understaffed_interval_hours` is net of breaks, as in SOW 1.2.

**Data to report to Northwind's WFM contact.** `export_2026-W44.csv` has two off-grid labels,
`2026-10-27 10:01` (priority) and `2026-10-29 10:01` (standard). Each is the only row for its
10:00 interval. Ingest floors them to 10:00 and counts them once.
