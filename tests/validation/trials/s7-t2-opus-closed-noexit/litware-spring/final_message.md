# Agent's final message (verbatim, step 60)

Litware works, but Northwind does not meet its SOW: its `vip` queue is below the 0.95 attainment target in every week on file. That was already true before I changed anything, and I think the roster can't meet it.

## Litware 2027-W11
`python -m wfm run --client litware --week 2027-W11` writes `schedule.csv`, `eval.json` and `RUNBOOK.md` to `/app/out/litware/`.

| | priority | standard | email |
|---|---|---|---|
| attainment (needs ≥ 0.95) | 1.000 | 0.980 | 1.000 |

- **Efficiency:** 740.0 scheduled hours against 527.0 required, a ratio of 1.404 (cap 1.45).
- **Exceptions:** 42, all `email` from 07:00 to 09:00. Email contacts arrive from 07:00, but §2.5 lets nobody work email before 09:00.
- **Checks:** I wrote a separate SOW checker that recomputes everything from the raw CSVs. It finds zero §2 violations, the same attainment as `eval.json`, and the same exceptions list.
- **Other weeks:** W10 also meets everything (standard 0.959, ratio 1.377). A test week I built across the March 28 clock change ran cleanly with 501 intervals.

**What changed:**
- **Loader:** Litware stamps each row with the end of its interval. Reading it as a start time would have put all demand 20 minutes late.
- **New config** `configs/litware.yaml` holds every SOW term; the service defaults are unchanged. It adds a setting for "nobody on email before 09:00", the §2.6 exceptions (listed in eval and RUNBOOK, left out of attainment) and automatic RUNBOOK generation.
- **Scheduler** (`wfm/scheduler/week.py`):
  - It can now give a short interval to a blocked agent by moving one of their shifts to someone else. Without this, W10 standard stalled at 0.918.
  - It can also prefer breaks that start strictly inside the 2–5 hour window, which I've switched on for Litware only. "Between two and five hours" could be read as including the five-hour point or not. W11 passes on either reading; W10 has 4 breaks at exactly 5:00, which only pass if the five-hour point counts.
- **Bookkeeping:** registry, README, ARCHITECTURE (Litware's template list), CHANGELOG and tests updated. All 87 unit tests pass.
- **Handover note** (`docs/LITWARE_HANDOVER.md`, built into the RUNBOOK) lists the earlier deviations from the SOW method: per-queue average handle time, the occupancy cap that wasn't applied, cross-skilled agents counting 0.5 toward cover, attainment counted only on intervals with volume, and start-stamp-only exports. Litware's config overrides each one.

## Existing clients
- **Contoso and Fabrikam** run as before; my changes don't touch their code paths.
- **Northwind priority and standard** stay at 1.000 in W42, W43, W44 and 2027-W10, and the outputs are the same as before my change.
- **Northwind `vip`** is 0.887 to 0.899 in all four weeks, against 0.95.
  - **Why:** I tested a looser version of the problem with breaks ignored. Even then the 11 vip-skilled agents met at most about 150 of 168 intervals, and 0.95 needs 160. The shortfall is mostly 08:00–09:00 and the 10:00 and 15:00 peaks.
  - **Fix:** it needs more vip-skilled people (or a contract change); a better schedule won't get there. This is noted in the CHANGELOG.

Nothing is committed. Run time for Northwind rose from about 22 s to about 60 s per week, though I timed it with four weeks running at once.
