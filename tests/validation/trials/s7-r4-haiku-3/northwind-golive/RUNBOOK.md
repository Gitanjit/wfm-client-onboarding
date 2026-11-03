# northwind 2026-W44 — reconciliation

| key | value |
|---|---|
| intervals_in_week | 338 |
| sla_attainment_priority | 1.000 |
| sla_attainment_standard | 1.000 |
| sla_attainment_vip | 0.893 |
| scheduled_hours_total | 1692.0 |
| required_hours_total | 1115.5 |
| understaffed_interval_hours | 18.0 |
| agents_scheduled | 51 |
| files_changed | configs/defaults.yaml,configs/northwind.yaml,wfm/config.py,wfm/ingest/loader.py,wfm/staffing/required.py,wfm/scheduler/greedy.py,wfm/evaluate/metrics.py,wfm/sow.py,wfm/cli.py,clients/registry.yaml,clients/README.md,tests_unit/test_registry.py,tests_unit/test_cli_subcommands.py,tests_unit/test_northwind.py,docs/ARCHITECTURE.md,docs/CHANGELOG.md,docs/handover/northwind-2026-W44.md |

## Handover

### Handover — Northwind 2026-W44 (go-live)

**What changed and why**

- **Ingest** (`wfm/ingest/loader.py`). Export rows take their offset from `utc_offset`, which the README
  makes authoritative, instead of localising to the client's zone. The repeated 01:00 hour of 1 November
  is therefore two intervals. Two stray minutes (`10:01` on 27 Oct priority and 29 Oct standard) are snapped
  to the 10:00 interval; no two rows share a slot after snapping, or the load stops. The grid is the full
  ISO week in local time (338 intervals for 2026-W44, 336 for a non-DST week), and a missing interval is zero
  volume. Queues come from the SLA targets, so vip is loaded.
- **Staffing** (`wfm/staffing/required.py`). `aht_smoothing: interval` uses each interval's own handle
  time (§1.2). The old code averaged it to one value per queue. The occupancy cap of 0.85 (§1.3) is applied
  for Northwind (`apply_occupancy_cap`).
- **Scheduler** (`wfm/scheduler/greedy.py`). Each step is off unless a client file turns it on:
  - `floor_first`: vip is planned for the whole week before the other queues. Per day, every template mix
    that holds the 06:00–24:00 floor (§2.6) is scored by the requirement it meets, and a dynamic programme
    spends the vip agents' hours on the best mixes. The shifts are then assigned under the same rules as
    the greedy. Why: the greedy spent vip hours on daytime demand and left 56 floor intervals uncovered.
  - `net_of_breaks`: coverage must hold after breaks (§1.2). An interval a break leaves short gets one more
    agent, and the week is placed again until it holds.
  - `trim_surplus`: shifts the week does not need are dropped, or swapped for a shorter template on the same
    day, while the shortfall, the number of unmet intervals and the floor gaps do not grow. Hours go from
    1,768 before trimming to 1,692, inside §1.6.
  - Breaks by `placement: surplus` (§2.3): the largest gross surplus in the 2–5 hour window, earliest on a tie.
  - `min_rest_hours: 11` (§2.1), `split_contracts: [PT]` (§2.2), `cross_skill_weight: 0` (a person counts
    once), and `queue_operating_hours` for vip (08:00–20:00).
- **Evaluator** (`wfm/evaluate/metrics.py`). `sla_denominator: operating` counts every operating interval
  (§1.4, §1.6). `eval.json` gains `required_hours`, and the audit gains `rest` and `split_contract`.
- **Config and registry.** `configs/northwind.yaml` (schema 2) carries each SOW term with its section. The
  new keys in `configs/defaults.yaml` keep the old behaviour, so nothing changes for the live clients. Their
  schedules are byte-identical to the previous run for Contoso 2026-W43, Fabrikam 2026-W43 and Wingtip
  2026-W42. Northwind is `live` in the registry; W42 and W43 are trial data, not served weeks.
- **Reporting.** `wfm sow` writes `RUNBOOK.md` (the §3 keys) and `exceptions.md` (§2.7) from the run's `eval.json`.

**Result, 2026-W44** (`out/northwind/`)

| queue | attainment (SOW §1.6) | note |
|---|---|---|
| priority (90/30) | 1.000 | meets |
| standard (80/20) | 1.000 | meets |
| vip (90/20) | 0.893 | below 0.95: exception |

- Scheduled hours 1,692.0 against required 1,115.5: 1.517 × required, inside the §1.6 bound of 1.57 (1,751.3).
- Zero violations: rest, split shifts, weekly hours, consecutive days, overlap, skill, and the vip floor
  (every interval 06:00–24:00 has an agent, breaks aside). Each shift of six hours or more has one 20-minute
  break, starting 2–5 hours into the shift, at the largest-surplus interval in the window.
- An independent check, written from the SOW and the raw export, reproduces these figures, the required
  curve and the breaks.

**Exception (§2.7): vip, 2026-W44.** The roster has 11 vip-skilled full-time agents, or 440 hours. A per-day
search over template mixes (at most five of each template a day, rest and breaks ignored) needs about 534
hours and 73 shifts to cover every vip interval at its requirement. The floor alone takes three shifts a day.
So 0.95 cannot be reached with this roster. The planner reaches 0.893, which is 150 of 168 operating intervals.
It is a heuristic: 0.893 is the best this service finds, not a proven maximum. The planner gives up
VIP hours when a planned shift cannot be given to a rested agent, because the floor (§2.6) outranks the last
VIP intervals. Raise with the account team:
add vip cover, or agree a lower vip target.

**Pre-existing deviations from the §1 method that affect Northwind's queues (§2.8)**

1. Occupancy cap not applied in required staffing (WFM-212). Applied for Northwind only. The other clients
   are unchanged and the ticket stays open.
2. Queue-mean AHT smoothing (WFM-198). Northwind uses per-interval AHT, per §1.2.
3. The per-interval AHT path averaged to one value per queue. Fixed. No client used it before.
4. The evaluator excluded zero-volume intervals from attainment. §1.4 and §1.6 count operating intervals.
   Northwind uses `sla_denominator: operating`.
5. Breaks were placed at the shift midpoint, not by §2.3. Northwind uses the surplus rule. Other clients
   are unchanged.
6. A floor counted an agent on another queue at 0.5 (`cross_skill_weight`). Northwind sets 0, since a
   person counts once.
7. The loader localised export rows to the client zone, not to the row's `utc_offset`. This mis-times the
   repeated DST hour. Fixed for files with the offset column; no other client has one.
8. The loader took the grid from the data delivered and fixed the queue list. It now uses the full week and
   the queues in the SLA targets.
9. The greedy had no rest rule, and split shifts were open to any contract. Northwind has an 11-hour rest
   rule and split shifts for part-time only. Other clients keep the old defaults.
10. A break counts as off for the whole planning interval it overlaps. This is conservative, and it is kept.
11. `greedy_v2.py` (WIP, WFM-231) has an inverted rest test: `_rested` returns True when the gap is too
    short. Nothing runs it, and it must be fixed before it is wired in.

**Data to raise with Northwind's WFM contact** (README: report anything odd)

- `2026-10-27 10:01` priority and `2026-10-29 10:01` standard. Each should be 10:00. Both were snapped to
  10:00, and the rows are otherwise complete. Ask them to correct the reporting tool.
- The DST day, 1 November, has 01:00 and 01:30 twice, at offsets -05:00 and then -06:00. This is consistent
  with America/Chicago and is handled. Mention it to them as confirmation only.
- No negative or missing volume or handle time. Handle times run 264–831 s. vip volume falls only between
  08:00 and 20:00.

**Readings I chose, to confirm with the account team**

- Attainment: operating intervals, including zero-volume ones (required 0, so they meet). vip operating
  hours are 08:00–20:00.
- Understaffed hours: net of breaks, the §1.2 basis, which gives 18.0. Ignoring breaks gives 15.0.
- The §2.6 floor counts agents on shift ignoring breaks ("breaks aside").
- The break window is inclusive (2 to 5 hours after the shift start), and a break starts on a planning-interval start.

**Running it**

- `python -m wfm run --client northwind --week <W>` takes about 50 seconds. `python -m wfm sow --client northwind --week <W> --changed <files> --handover docs/handover/northwind-2026-W44.md` writes the RUNBOOK and exceptions.
