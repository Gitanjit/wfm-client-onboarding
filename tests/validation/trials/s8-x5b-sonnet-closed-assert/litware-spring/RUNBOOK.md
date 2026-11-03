# Litware weekly reconciliation, 2027-W11

| key | value |
|---|---|
| intervals_in_week | 504 |
| sla_attainment_priority | 1.000 |
| sla_attainment_standard | 1.000 |
| sla_attainment_email | 1.000 |
| scheduled_hours_total | 722.0 |
| required_hours_total | 527.0 |
| understaffed_interval_hours | 0.0 |
| agents_scheduled | 24 |
| exception_intervals | 42 |
| files_changed | clients/README.md, clients/registry.yaml, configs/defaults.yaml, configs/litware.yaml, docs/ARCHITECTURE.md, docs/CHANGELOG.md, docs/clients/litware.md, tests_unit/test_litware.py, wfm/config.py, wfm/constraints.py, wfm/evaluate/metrics.py, wfm/ingest/loader.py, wfm/report/sow.py, wfm/scheduler/weekly.py |

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

Week 2027-W11. Scheduled 722.0 h against 527.0 required h (ratio 1.370;
SOW 1.6 allows 1.45). Rule violations audited in `eval.json`: 0. 42 intervals are listed
under Exceptions (SOW 2.6): `email` contacts arrive from 07:00 but nobody may be scheduled on `email` before 09:00
(SOW 2.5), so those intervals cannot meet their target; they are neither covered by breaking another rule nor dropped
from the week (they count in `intervals_in_week` and `required_hours_total`, and stay out of the attainment
fractions and `understaffed_interval_hours`).

### What changed, and why

Litware could not be run on the service as it stood. Everything is opt-in per client through
`configs/litware.yaml`; `configs/defaults.yaml` only gained the new key `queue_start` at its old behaviour (none),
so Contoso, Fabrikam and Northwind keep their outputs.

- **Ingest** (`wfm/ingest/loader.py`): Litware's export stamps each row with the END of its interval
  (`interval_end_local`) and a `utc_offset` for that moment. The loader only knew start-stamped exports, so the
  stamp is converted to UTC with the offset and one grain (20 min) is subtracted: a row stamped 09:20 covers
  09:00-09:20. Reading the stamps as starts would shift all demand 20 minutes late. The week's grid comes from the
  calendar (`calendar_grid`; a spring-forward week has 167 h) and `email` is read (`queues`).
- **Staffing** (`configs/litware.yaml`): Erlang C without abandonment, the 0.85 occupancy cap applied
  (`apply_occupancy_cap`, WFM-212), each interval on its own handle time (`aht_smoothing: interval`), targets
  priority 90/30, standard 80/30, email 80/300 (SOW 1.2), set in the client file; defaults untouched.
- **Scheduler** (`wfm/scheduler/weekly.py`, `scheduler: weekly`): rest 11 h, split shifts PT only, breaks by the
  largest gross surplus inside the 2-5 h window, plans on coverage net of breaks, hours bound 1.45 (SOW 1.6),
  two agents on `priority` in every operating interval (`min_cover`, SOW 2.4, no cross-skill credit) and a new
  per-queue earliest start (`queue_start: {email: 9}`, `wfm/constraints.py`, SOW 2.5) that keeps `email` shifts
  from starting before 09:00 (D8, L8, P4 and P6b only) and marks the earlier email intervals as SOW 2.6 exceptions.
- **Evaluator** (`wfm/evaluate/metrics.py`): attainment over every operating interval (email 07:00-19:00, the
  others 07:00-21:00) without the SOW 2.6 exceptions, `sla_target` 0.95, audits for rest, split shifts, breaks and
  the email start.
- **Reports** (`wfm/report/sow.py`): this file and `exceptions.md`, recomputed from `schedule.csv` on each run.

### SOW 2.8: pre-existing deviations from the section 1 method that touch Litware's queues

1. WFM-212: the occupancy cap was read but not applied in required staffing (SOW 1.3). Fixed for Litware; still
   open for the other clients.
2. WFM-198: required staffing used the queue's mean handle time, not the interval's own (SOW 1.2). Off for
   Litware (`aht_smoothing: interval`); the old `interval` mode also collapsed to the queue mean, which is
   fixed (Litware and Northwind use it; Contoso, Fabrikam and the rest still smooth).
3. The service defaults are 80/20 on `priority` and `standard` with `sla_target` 0.90 and no `email`; Litware's
   targets differ (SOW 1.2) and `email` was silently dropped by the loader. Set in `configs/litware.yaml`.
4. The evaluator took only intervals with volume as the attainment denominator and one `sla_target` for all
   queues; SOW 1.6 counts every operating interval. Changed for Litware only.
5. The loader localised wall-clock labels (ambiguous at a DST change), used the delivered grid instead of the
   calendar, and knew only start-stamped rows (see Ingest above).
6. Minimum-cover credit: an agent on another queue counted 0.5 toward a floor (PR #31); SOW 1.2 counts a person once,
   on the queue they are scheduled on. `cross_skill_weight: 0` for Litware.
7. The greedy scheduler places day by day with no rest rule, split shifts for any contract, breaks at the shift
   midpoint and coverage counted gross of breaks. Replaced for Litware by `weekly`.
8. The service had no earliest-start rule per queue (SOW 2.5) and no notion of an infeasible interval (SOW 2.6).
   Added as opt-in (`queue_start`).
9. Not applicable to Litware: Fabrikam's `qlib` abandonment model and `attainment_basis: coverage` (PR #47).

### Data and roster findings

- Export 2027-W11: nothing unusual found (1512 rows, one per queue per 20-minute interval, stamped with the interval end; utc_offset used as given).
- Roster: 24 agents; 5 hold `email`. Checked against this schedule:

- None: every queue meets the 0.95 weekly attainment with the roster provided.
