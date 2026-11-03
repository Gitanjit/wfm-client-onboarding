# Northwind Traders — 2026-W44 reconciliation

| key | value |
|---|---|
| intervals_in_week | 338 |
| sla_attainment_priority | 0.960 |
| sla_attainment_standard | 0.960 |
| sla_attainment_vip | 0.905 |
| scheduled_hours_total | 1534.0 |
| required_hours_total | 1115.5 |
| understaffed_interval_hours | 30.0 |
| agents_scheduled | 51 |
| files_changed | configs/northwind.yaml, wfm/ingest/loader.py, wfm/staffing/required.py, wfm/scheduler/week.py, wfm/evaluate/metrics.py, wfm/report/runbook.py, wfm/cli.py, clients/registry.yaml, clients/README.md, docs/clients/northwind.md, docs/ARCHITECTURE.md, docs/CHANGELOG.md, tests_unit/test_northwind.py, tests_unit/test_registry.py, tests_unit/test_cli_subcommands.py |

## Handover note

**What changed and why (go-live, 2026-W44).**

- *Ingest* (`wfm/ingest/loader.py`). An export with a `utc_offset` column now takes UTC from that offset
  (README: it is authoritative). Before, the wall-clock label was localised. At the 2026-11-01 fall-back
  that is ambiguous, because 01:00–02:00 happens twice. A client's queues now come from its `sla` keys:
  `vip` was dropped by the hard-coded `priority, standard`. The interval grid is the whole ISO week in
  the client's timezone (338 intervals in W44, 336 otherwise), not just the intervals that happen to be
  in the file. Live clients' outputs are byte-identical on every data week on file.
- *Staffing* (`wfm/staffing/required.py`). `aht_smoothing: interval` was ignored: the queue mean was always
  used. It now uses each interval's own AHT, as §1.2 requires. The occupancy cap (§1.3, 0.85) is now
  applied (WFM-212, service-wide). It does not bind for any live client on current data, so their
  required curves are unchanged.
- *Scheduler* (`wfm/scheduler/week.py`, `scheduler: week`). The default greedy scheduler is left as it is
  for the live clients. Northwind gets a week-aware scheduler that enforces §2 while placing shifts:
  - 11 h elapsed rest between shifts, both ways (§2.1);
  - S44 split shifts for PT only (§2.2);
  - one 20-minute break on every shift of 6 h or more, starting 2–5 h in, in the interval with the
    largest gross surplus (§2.3). If the 5 h edge interval is not strictly the largest, the break starts
    in [2 h, 5 h), so it is valid whether the window is read as closed or half-open. A few breaks can
    only go at exactly 5 h; these are valid under the closed reading;
  - 40/24 h elapsed caps, at most five consecutive days, skills, no overlap (§2.4);
  - only the ARCHITECTURE templates (§2.5);
  - at least one agent on `vip` net of breaks, 06:00–24:00 local (§2.6). Cross-skilled agents count
    0 (§1.2: a person counts once).

  The scheduler then runs a seeded local search, so it is deterministic. The search keeps scheduled
  hours under the §1.6 cap of 1.57 × required hours (W44: about 1.38), aims for at least 0.96
  attainment per queue, and otherwise maximises `vip` attainment.
- *Evaluation* (`wfm/evaluate/metrics.py`, `wfm/report/runbook.py`). Attainment is counted over
  operating intervals: 06:00–24:00, and 08:00–20:00 for `vip` (§1.4, §1.6). Before, only intervals
  with volume counted. Cover is net of breaks. `eval.json` adds `required_hours`, `efficiency` and audits
  for rest, split shifts, templates and breaks. `RUNBOOK.md` is written on every run.

**Not met: §1.6 `vip` attainment ≥ 0.95. The roster cannot deliver it.** Only 11 agents hold `vip`.
All are FT, so `vip` gets at most 11 × 40 = 440 agent-hours a week. In W44, covering every `vip`
interval at §1.2, plus the §2.6 floor, needs 534 agent-hours with the SOW templates. That figure comes
from an exhaustive per-day search and ignores breaks and rest, so the real need is higher. Even at
0.95 (about 8 failing intervals) the need is about 486 h. With 440 h, the best possible is about 14
failing intervals, or about 0.92. The scheduler reaches 0.887–0.905 on the weeks on file (W42–W44; this week's figure is in the table above).
Every §2 rule holds, priority and standard are at or above 0.96, and hours are inside the §1.6 cap.
With two more FT agents holding `vip` (new hires, or `vip` added to two FT priority agents), the same
scheduler reaches 0.964 on W44 at about 1.44 × required hours. **Action: the account team and Northwind
need to agree on the extra `vip`-skilled staffing (or a temporary `vip` target) before this is
signed off as compliant.**

**Data to raise with Northwind's WFM contact.** `export_2026-W44.csv` has two rows stamped off the
30-minute grid: `2026-10-27 10:01` (priority) and `2026-10-29 10:01` (standard). Each is the only row
for its interval, so ingest floors it to 10:00 and the demand is kept. Otherwise W42–W44 are clean: no
duplicates, no gaps, every offset matches Central time, and the 01:00 hour on 2026-11-01 appears twice
(−05:00 then −06:00), as expected.

**§2.8: deviations from the §1 method that existed before go-live and affect Northwind's queues.**

1. WFM-212. The occupancy cap was read from config but not applied (§1.3). Fixed in this change.
2. WFM-198. Staffing uses the smoothed queue-mean AHT by default, not the interval's own AHT (§1.2).
   Selecting `aht_smoothing: interval` had no effect. Fixed; Northwind runs on interval AHT.
3. The evaluator counted attainment only over intervals with volume, not over operating intervals
   (§1.6), and had no per-queue operating hours for `vip` (§1.4). Northwind now uses
   `attainment_intervals: operating` and `queue_hours`.
4. Minimum cover counts a cross-skilled agent on another queue as 0.5 toward a floor (PR #31,
   `cross_skill_weight`), and counted floors gross of breaks. §1.2 and §2.6 require one person to count
   once, on their own queue, net of breaks. Northwind sets `cross_skill_weight: 0` and
   `floor_net_of_breaks: true`.
5. The greedy scheduler places breaks at the shift midpoint (not §2.3), has no rest rule (§2.1), and
   lets FT agents take the S44 split (§2.2). Northwind uses `scheduler: week`. The WFM-231 draft
   (`greedy_v2.py`) is not used: its `_rested` check is inverted and lets through exactly the shifts
   that are too close.
6. The loader dropped any queue other than `priority`/`standard`, and ignored export UTC offsets.
   Both are fixed (see above).

These affect other clients only, and are listed for completeness: Fabrikam's staffing runs on the
vendored abandonment model (`queueing: qlib`) and its attainment on `coverage` (PR #47). Contoso's
`sla_target: 0.72` is a temporary override made while WFM-212 was open; it is an evaluator verdict
only, and it is out of scope here. Fabrikam's offset-less export fallback (WFM-204) assigns one offset
per local date, so the early hours of a DST change day would be off by an hour. Fabrikam delivers
canonical files today.

**Figures in the table** are recomputed from `schedule.csv`. Attainment and understaffing count an agent
on break as absent for the 30-minute interval the break falls in. Scheduled hours are elapsed and
include paid breaks. Required hours are Erlang C under §1.2–§1.3 only; the §2.6 floor is not counted
as required. `files_changed` lists the go-live change.
