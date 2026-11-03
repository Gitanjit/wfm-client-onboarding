# Agent's final message (verbatim, step 50)

Northwind 2026-W44 now runs end to end, but `vip` reaches only 0.917 weekly attainment against the 0.95 target. That is recorded as an exception for the account team. `python -m wfm run --client northwind --week 2026-W44` writes `schedule.csv`, `eval.json`, `RUNBOOK.md` and `exceptions.md` to `/app/out/northwind/` in about 15 s. The 91 unit tests pass, and I haven't committed anything.

I checked the W44 schedule with a separate checker I wrote from the SOW text. It finds zero violations of §2.1–2.6, and its attainment, scheduled hours, required hours and understaffed hours match `eval.json` and the RUNBOOK. W42 and W43 run clean too, and a synthetic spring-forward week (334 intervals) ran without rule violations.

| | W44 |
|---|---|
| Intervals in week (fall-back week) | 338 |
| priority / standard / vip attainment | 1.000 / 1.000 / 0.917 |
| Scheduled hours vs bound (1.57 × required) | 1660.0 vs 1751.3 |

**vip shortfall.** Only 11 agents hold `vip`, all full-time, so vip cover is capped at 440 h a week and the schedule uses 436–438 h. Relaxing the rest rule or the five-day limit in a test did not change the result, and different search seeds converged on the same value, so I believe this is the limit for this roster. Other weeks come out at 0.905–0.923. `exceptions.md` lists vip for W44 with achievable 0.917 and shortfall 0.033.

**Gaps found in the existing service, for the §2.8 handover note:**
- **Occupancy cap:** the 0.85 cap was never applied in staffing (WFM-212).
- **Handle time:** required staffing used the queue's mean AHT, and `interval` mode still averaged it.
- **Attainment:** it was computed on `coverage` and left zero-volume intervals out of the denominator.
- **Queues:** the loader dropped `vip` because it only knew two queues.
- **UTC offset:** the loader ignored `utc_offset`, which breaks the repeated hour on 2026-11-01.
- **Scheduling rules:** the scheduler placed breaks at the shift midpoint and had no rest rule. Split shifts were open to every contract.
- **Draft scheduler:** the unfinished `greedy_v2.py` has its rest check inverted, so I didn't use it.

**Data oddity to raise with Northwind's WFM contact.** W44 has two rows stamped one minute off the grid: `2026-10-27 10:01` (priority) and `2026-10-29 10:01` (standard). Their 10:00 rows are missing, so I treated them as the 10:00 intervals rather than dropping them.

**Live clients.** I re-ran every committed week for Contoso, Fabrikam and Wingtip before and after the change. All schedules and evals are byte-identical. Everything new sits behind Northwind config keys, so `defaults.yaml` and the other configs are untouched.

**What changed in the code:**
- **Config:** new `configs/northwind.yaml`.
- **Scheduler:** a new week-aware local search in `wfm/scheduler/search.py` that recomputes breaks per the §2.3 surplus rule for every candidate schedule. It uses a fixed seed, so output is deterministic.
- **Ingest, staffing, rules, evaluator:** the loader, staffing and greedy scheduler gained opt-in options for the SOW rules, and the evaluator now audits them.
- **Report, registry, docs and tests:** a new RUNBOOK/exceptions writer in `wfm/report/runbook.py`, the registry and docs updated, and a new test file `tests_unit/test_northwind.py`. I edited two existing registry tests that asserted Northwind was still pending.

**Not decided by me:**
- WFM-212 stays open for the service defaults. Turning the cap on there would change every live client's staffing, which I left for the account teams to sign off.
- `files_changed` in the RUNBOOK is a fixed list in `configs/northwind.yaml`, so it needs updating if more files change.
