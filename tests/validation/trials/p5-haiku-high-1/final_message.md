# Agent's final message (verbatim, step 31)

Northwind 2026-W44 now runs with `python -m wfm run --client northwind --week 2026-W44`. It writes `schedule.csv` and `eval.json`, and I wrote `RUNBOOK.md` alongside them. An independent SOW checker finds no §2 violations and recomputes §3 at 1.000 attainment on both queues. The changes are in the working tree and not committed, since you didn't ask for a commit.

**Results (W44)**

| key | value |
|---|---|
| intervals_in_week | 338 |
| sla_attainment_priority | 1.000 |
| sla_attainment_standard | 1.000 |
| scheduled_hours_total | 1328.0 |
| understaffed_interval_hours | 0.0 |
| agents_scheduled | 40 |

**What was wrong and what I changed**
- **DST (2026-11-01):** the old loader crashes on the repeated 01:00 hour (`AmbiguousTimeError`, which I confirmed). It now uses the export's `utc_offset` column, and the grid is the full local week (338 intervals).
- **Occupancy cap (WFM-212):** it was never applied. It now is. It doesn't bind on any existing week's volumes, so nothing changes for Contoso or Fabrikam.
- **AHT:** `aht_smoothing: interval` was computed as a queue mean. It is now per interval.
- **Scheduler:** it had no rest rule, allowed split shifts for everyone, and placed breaks at the midpoint. These are now config-driven. Defaults keep the old behaviour.
- **Breaks and SLA:** breaks are placed at the largest gross surplus, and the target is raised wherever a break leaves an interval short (net of breaks).
- **Config:** `configs/northwind.yaml` holds only the SOW overrides. Service defaults are unchanged.

**Regression check:** Contoso and Fabrikam W41–W43 schedules are byte-identical to baseline. Their configs are untouched, including the Contoso `sla_target` override.

**Interpretations I chose**
- SLA denominator is the 252 operating intervals (06:00–24:00 local). Zero-volume intervals count as met, since the requirement is 0.
- A break removes its agent from the whole planning interval. This is the conservative reading of "net of breaks".
- Breaks start on the planning-interval boundary inside the 2–5 h window.
- A split shift is two segments on one local day.

**Not verified or open**
- **Hours vs reference:** 1328 scheduled hours against about 809 h of raw requirement. Pruning removed nothing, and per-hour template scoring made coverage worse, so I reverted it. I haven't tried a stronger optimiser, so this may be well above a reference solution.
- **Other weeks:** I tested W42 and W43 on real data, and a synthetic spring-forward week (2027-W10) built from the real volume profile. I didn't test real later weeks, and I couldn't run Contoso or Fabrikam's next week because that data isn't here.
- **Known bug left alone:** `greedy_v2.py` has an inverted rest comparison (WFM-231). It's a WIP draft that isn't wired in, so I didn't touch it.

**Files:** `wfm/ingest/loader.py`, `wfm/staffing/required.py`, `wfm/scheduler/greedy.py`, `configs/northwind.yaml`, `wfm/evaluate/sow_northwind.py` (new), `tests_unit/test_northwind.py` (new), `docs/CHANGELOG.md`, `docs/ARCHITECTURE.md`. The existing 9 tests and 3 new ones pass. Outputs are in `out/northwind/`.
