# Agent's final message (verbatim, step 76)

`python -m wfm run --client northwind --week 2026-W44` now writes `schedule.csv`, `eval.json` and `RUNBOOK.md` to `/app/out/northwind/` in about 9 s. One contract target is still missed: VIP attainment is 0.905 against the SOW's 0.95, and it can't reach 0.95 with the current roster.

**W44 results**

| | value |
|---|---|
| Attainment: priority / standard / vip | 0.960 / 0.960 / **0.905** |
| Scheduled vs required hours | 1534.0 / 1115.5 = 1.375 (cap 1.57) |
| SOW §2 violations | 0 |

A separate from-scratch checker (its own Erlang C and rule checks, not the service's code) gives exactly the same figures as `eval.json` and the RUNBOOK. W42 and W43 also run with zero violations (VIP 0.887 and 0.905). The 84 unit tests pass. Contoso, Fabrikam, Wingtip and the paused/retired clients give byte-identical output to the old code on all 231 data weeks on file.

**Why VIP can't reach 0.95:** only 11 agents hold the `vip` skill, all full-time, so VIP gets at most 440 h a week. An exhaustive per-day search over the SOW templates, ignoring breaks and rest, shows W44 needs 534 h for full VIP cover and about 486 h even at 0.95. With two more full-time VIP-skilled agents (new hires, or VIP added to two priority agents), the same scheduler reaches 0.964 at 1.44× required hours. The account team and Northwind need to agree on that staffing, or a temporary VIP target, before W44 is signed off as compliant.

**What I changed**
- **Ingest:** the loader now takes UTC from the export's `utc_offset`. Before, the DST fall-back on 1 Nov broke: the 01:00 hour happens twice, and the code tried to work out UTC from the wall-clock label. The `vip` queue is no longer dropped, and every week gets its full interval grid (338 intervals in W44, 336 otherwise).
- **Staffing:** the setting to use each interval's own handle time was being silently ignored, so the queue average was always used. That's fixed. The 0.85 occupancy cap is now applied for every client (it was open ticket WFM-212). It doesn't change any live client's results on current data.
- **Scheduler:** Northwind uses a new week-aware scheduler, `wfm/scheduler/week.py`, switched on in its config. It enforces 11 h rest, split shifts for part-timers only, the surplus-based break rule, and at least one VIP agent net of breaks from 06:00 to 24:00. It then runs a deterministic search to keep hours down. The live clients still use the old greedy scheduler. I didn't use the existing draft (`greedy_v2.py`) because its rest check is inverted.
- **Evaluation and runbook:** attainment counts every operating interval (08:00–20:00 for VIP), and `eval.json` now reports violations for rest, split shifts, templates and breaks. The RUNBOOK table is recalculated from the written schedule on every run, and the handover note is copied in from `docs/clients/northwind.md`.
- **Config and records:** I added `configs/northwind.yaml` and didn't change `defaults.yaml`. Northwind is marked config schema 1 in the client registry but stays `onboarding`; switching it to `live` is a separate registry change. Two registry tests that checked Northwind had no config yet are updated. I also updated the client README, ARCHITECTURE and CHANGELOG, and added `tests_unit/test_northwind.py`.

**Two things to know**
- **Data to raise with Northwind:** the W44 export has two rows stamped 10:01 instead of on the half hour (27 Oct priority, 29 Oct standard). Each is the only row for its slot, so the loader puts it at 10:00 and no demand is lost.
- **Breaks at exactly 5 h:** three W44 breaks start exactly 5 h into the shift, because that interval has the largest surplus. That's valid if "between two and five hours" (SOW §2.3) includes 5 h, which I assumed. A checker that excludes 5 h would flag these three; every other break is valid either way.

The handover note covers what §2.8 asks for: the old deviations from the SOW method that affect Northwind (occupancy cap, handle-time averaging, which intervals count toward attainment, half-credit for cross-skilled agents, the old scheduler's break and rest gaps, the loader issues). It also lists, for completeness, the ones that only affect other clients: Fabrikam's abandonment model and coverage basis, Contoso's 0.72 target override, and Fabrikam's fixed-offset fallback. Nothing is committed.
