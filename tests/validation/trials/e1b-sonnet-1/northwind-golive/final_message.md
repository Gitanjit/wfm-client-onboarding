# Agent's final message (verbatim, step 55)

Northwind W44 now runs end to end, but the `vip` queue misses the SOW's 0.95 target at 0.917, and the roster can't reach it. I did not commit anything.

`python -m wfm run --client northwind --week 2026-W44` writes `schedule.csv`, `eval.json`, `RUNBOOK.md` and `exceptions.md` to `/app/out/northwind/`. It takes about 25 s and gives byte-identical output on repeat runs. W42 and W43 also run.

An independent checker I wrote from the SOW definitions matches `eval.json` and the RUNBOOK figures, and finds no SOW §2 violations. The unit tests pass (87), and Contoso, Fabrikam and Wingtip produce byte-identical `schedule.csv` and `eval.json` to before my changes.

| | W44 |
|---|---|
| priority / standard attainment | 1.000 / 1.000 |
| vip attainment | 0.917 (target 0.95) |
| scheduled hours | 1660.0 (1.488× the 1115.5 required; limit 1.57×) |
| intervals | 338 |
| agents scheduled | 51 |
| understaffed interval hours | 15.0 |

**Vip:** only 11 agents hold the vip skill, which is 440 h at their caps. Covering every vip interval needs about 534 h even before breaks and rest rules. A relaxed hours-only bound allows at best about 0.923. `exceptions.md` records vip at 0.917 with a shortfall of 0.033, and says roughly one to three more full-time vip agents would close it.

Things I found in the repo and the data:
- **DST:** W44 contains the Chicago fall-back on 1 Nov. The 01:00 and 01:30 labels appear twice, so the week has 338 intervals. Ingest now takes UTC from each row's `utc_offset`.
- **Odd rows:** two W44 rows are stamped `10:01` (27 Oct priority, 29 Oct standard) with no `10:00` row beside them. I treated them as the 10:00 intervals; the handover note flags them for Northwind's WFM contact.
- **Staffing bugs:** the occupancy cap (WFM-212) was never applied, `aht_smoothing: interval` silently collapsed to the queue mean, and `vip` was dropped by the loader.
- **Draft scheduler:** I did not use `greedy_v2.py`. Its rest check is inverted.
- **Break stacking:** the SOW's break rule piles breaks into the same peak-surplus interval, so the scheduler checks attainment net of those breaks.

Every change is opt-in per client through `configs/northwind.yaml`. `configs/defaults.yaml` and the other clients' configs are untouched, so WFM-212 is still open for Contoso, Fabrikam and Wingtip. The handover note lists this and the other pre-existing deviations under §2.8.

I added a week-aware scheduler in `wfm/scheduler/weekly.py` and a reconciliation writer in `wfm/report/reconcile.py`. The evaluator, loader, `required.py` and CLI got opt-in changes. I also added Northwind tests, docs and a registry update.

**For you to decide:**
- I left Northwind as `onboarding` in `clients/registry.yaml`, since the earlier data weeks (W42, W43) would fail the registry check if the status flipped to `live`. Flipping it is an ops call once the first cycle is archived.
- I treated a split shift (S44) as one shift for the break rule, with the break in its first segment. The SOW doesn't say; if the account team reads it per segment, S44 breaks would need to change.
