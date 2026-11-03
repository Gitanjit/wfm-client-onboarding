# Northwind Traders — 2026-W44 reconciliation

Produced by `cd /app && python -m wfm run --client northwind --week 2026-W44` (`schedule.csv` and
`eval.json` in this directory). Definitions are the SOW §3 definitions (`docs/NORTHWIND_SOW.md`).

| key | value |
|---|---|
| intervals_in_week | 338 |
| sla_attainment_priority | 1.000 |
| sla_attainment_standard | 1.000 |
| sla_attainment_vip | 0.899 |
| scheduled_hours_total | 1654.0 |
| required_hours_total | 1115.5 |
| understaffed_interval_hours | 15.5 |
| agents_scheduled | 51 |
| files_changed | configs/northwind.yaml, wfm/ingest/loader.py, wfm/staffing/required.py, wfm/constraints.py, wfm/scheduler/week.py, wfm/evaluate/metrics.py, wfm/cli.py, tests_unit/test_northwind.py, tests_unit/test_registry.py, tests_unit/test_cli_subcommands.py, docs/ARCHITECTURE.md, docs/CHANGELOG.md |

Efficiency (SOW §1.6): 1654.0 / 1115.5 = 1.483, inside the 1.57 bound. SOW §2: no violations (rest,
split shifts, breaks and break placement, weekly hours, consecutive days, skills, overlap, VIP cover).
I checked this with the service evaluator and with a separate checker written straight from the SOW.

## Handover note

### Action needed: VIP cannot reach 0.95 with the current roster

VIP attainment is **0.899** (151 of 168 operating intervals). SOW §1.6 asks for 0.95. **The SOW is
not met on `vip` this week**, and `eval.json` reports `meets_target: false`. This comes from the
roster, not from the scheduler:

- Only 11 agents hold the `vip` skill (7 vip-only, 4 priority+vip, all full-time). At 40 h each,
  that is at most **440 VIP agent-hours** a week.
- Covering VIP's §1.2 requirement plus the §2.6 floor (one agent 06:00–24:00) in every interval of
  W44 needs at least **534 agent-hours** with the allowed templates. I found that minimum by exhaustive
  search per day, with breaks ignored, so the real need is higher. W42 and W43 look the same (0.887 and
  0.899).
- All 11 VIP agents work only on `vip` (430 h). Priority and standard are at 1.000 and do not borrow
  any VIP-skilled time.
- To close the gap, Northwind needs about 3–4 more full-time agents with the `vip` skill, or a change
  to the VIP target or floor. This needs to go to the account team and Northwind. The config keeps the
  SOW figures (`sla_target: 0.95`, vip 90/20). Lowering them would only hide the shortfall.

### What changed and why

All new behaviour is opt-in through `configs/northwind.yaml`. `configs/defaults.yaml` is unchanged.
Contoso (2026-W43), Fabrikam (2026-W43) and Wingtip (2026-W42) produce byte-identical `schedule.csv`
and `eval.json` before and after the change.

- **Ingest** (`wfm/ingest/loader.py`):
  - UTC now comes from each row's `utc_offset`, as Northwind's README requires. Before, the wall-clock
    label was localised to the timezone. That cannot tell apart the two 01:00/01:30 rows on 2026-11-01
    (fall-back), and the week has 338 intervals, not 336.
  - Queues now come from config, so `vip` is ingested. They were hard-coded to priority and standard.
  - `week_grid: full` gives the whole ISO week even if rows are missing. Missing rows count as zero
    volume.
  - Off-grid timestamps are snapped to their interval and duplicate rows are dropped, both with a
    warning.
- **Staffing** (`wfm/staffing/required.py`):
  - The occupancy cap is now applied (**WFM-212 fixed**). SOW §1.3 requires it. It never binds for the
    live clients, so their outputs do not change.
  - `aht_smoothing: interval` now uses each interval's own AHT, as SOW §1.2 requires. Before, it still
    averaged AHT across the queue.
  - Nothing is required outside a queue's operating hours: `vip` 08:00–20:00, other queues
    06:00–24:00 (§1.4).
- **Scheduler** (`wfm/scheduler/week.py`, selected by `scheduler: week`):
  - Places shifts across the whole week with the §2 rules enforced: 11 h rest, split shifts for PT
    only, 40/24 h caps, at most 5 consecutive days, skills, one template per day.
  - The VIP floor counts net of breaks and only agents on the `vip` queue.
  - Breaks follow §2.3: one 20-minute break, starting at the window interval with the largest gross
    surplus.
  - A deterministic local search then improves floor cover, attainment and hours. Scheduled hours are
    held under 1.57 × required hours.
  - S44 is not used. Its 2–5 h break window falls partly in the gap between its two segments, so the
    rule is ambiguous there. §2.5 allows using a subset of the templates.
  - The WFM-231 draft (`greedy_v2.py`) is not used. Its rest check is inverted: it accepts shifts with
    *less* than 11 h rest.
- **Evaluator** (`wfm/evaluate/metrics.py`):
  - Attainment is counted over operating intervals (§1.6), not over intervals with volume.
  - The VIP floor is counted net of breaks.
  - New audits for rest, split shifts, break count and break placement.
  - `eval.json` now includes `required_hours` and the efficiency ratio.
- **Tests**: new `tests_unit/test_northwind.py`. The two registry tests that pinned "northwind
  pending, no config yet" now expect no pending items. The registry still lists Northwind as
  `onboarding`. Switching it to `live` is a separate lifecycle step: with `onboarded: 2026-10-26`,
  `clients --check` flags the W42/W43 history files as outside the weeks served.

### Pre-existing deviations from the SOW §1 method that affect Northwind's queues (SOW §2.8)

1. **Occupancy cap not applied (WFM-212).** The cap was read from config but never passed to the
   Erlang C call (§1.3). Now fixed for all clients; no change for the live ones.
2. **Smoothed handle time (WFM-198).** The service default `aht_smoothing: queue_mean` uses the
   queue's mean AHT, not each interval's own AHT (§1.2). The `interval` option also still averaged.
   Northwind now uses true per-interval AHT. The default is unchanged for other clients.
3. **Export timestamps.** The export reader ignored `utc_offset` and localised wall-clock labels
   (§1.5). Fall-back rows were ambiguous and DST weeks would have been mis-gridded. Fixed.
4. **Queues hard-coded to priority/standard.** `vip` (§1.1) would have been dropped at ingest. Fixed
   through the `queues` config key.
5. **Grid "as the data delivers it".** Missing intervals disappeared from the week instead of counting
   as zero-volume intervals. Northwind now uses the full ISO-week grid.
6. **No operating-hours rule in staffing.** Any volume outside 06:00–24:00, or outside 08:00–20:00 for
   `vip`, would have been staffed (§1.4). Now enforced for Northwind.
7. **Attainment basis.** The evaluator counted only intervals with volume > 0, not all operating
   intervals (§1.6). The `coverage` basis (Fabrikam, PR #47) gives partial credit and is not the SOW
   method. Northwind uses `service_level` over operating intervals.
8. **Cross-skilled floor credit (PR #31).** `cross_skill_weight: 0.5` counts an agent on another queue
   as half an agent toward a floor. This conflicts with §1.2 ("a person counts once, on the queue they
   are scheduled on"). Floors were also counted gross of breaks. Northwind sets the weight to 0 and
   counts the floor net of breaks.
9. **Abandonment model.** `queueing: qlib` (vendored qlib 1.3, Erlang A, 90 s default patience since
   1.3) is not the §1.2 model, which is Erlang C with no abandonment. Northwind uses `queueing: erlang`.
   Any client routed through qlib gets a lower requirement than the SOW method gives.
10. **`sla_target` is an evaluator verdict, not a contract.** Contoso's temporary 0.72 override shows
    how this has been used to make `eval.json` pass. Northwind's `sla_target: 0.95` is the SOW §1.6
    figure, and the 0.899 VIP result is reported as a failure.

### Data notes for Northwind's WFM contact

- `export_2026-W44.csv` has two off-grid rows: `2026-10-27 10:01` (priority) and `2026-10-29 10:01`
  (standard). Both sit where the 10:00 row is missing for that queue, so I treated them as the 10:00
  interval. Please confirm.
- The fall-back night (2026-11-01, two 01:00 and two 01:30 hours) is handled through `utc_offset`.

### Interpretation choices

- The break window is read as inclusive: the break starts 2 h to 5 h after shift start, both ends
  allowed. Among tied intervals, ones strictly inside the window are preferred. 17 breaks in W44 start
  at exactly +5 h, because that interval alone has the largest surplus.
- "Breaks aside" in §2.6 is applied strictly: at least one VIP agent who is not on break in every
  interval from 06:00 to 24:00. This also satisfies the looser, gross reading.
