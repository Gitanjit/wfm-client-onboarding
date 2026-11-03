# Agent's final message (verbatim, step 57)

Northwind is onboarded: the W44 run writes `schedule.csv` and `eval.json` with zero SOW §2 violations. But **VIP cannot reach its 0.95 target with the roster Northwind provided**, so I've recorded that as a §2.7 exception. Nothing is committed; the changes are in the working tree.

**W44 results**

| | value |
|---|---|
| intervals | 338 (Sunday 1 Nov has 25 local hours because the clocks go back) |
| attainment priority / standard / vip | 1.000 / 1.000 / **0.917** |
| scheduled / required hours | 1688.0 / 1115.5, ratio 1.513 (bound 1.57) |
| understaffed interval-hours | 15.5 |
| agents scheduled | 51 |

A separate checker I wrote straight from the SOW, reading the raw export and `schedule.csv` without the service's code, gives the same figures and finds no violations. Output is the same on every run. W42, W43 and a made-up week with the spring clock change, a missing row and a duplicate row all run without violations.

**The VIP shortfall (`exceptions.md`: vip | 2026-W44 | 0.917 | 0.033)**
- Only 11 agents can take VIP, all full-time, so VIP has at most 440 hours a week.
- Hitting 0.95 would need about 486 hours, even ignoring breaks, rest and per-agent limits. The best possible with 440 hours is roughly 0.923; the schedule gets 0.917.
- Priority and standard have spare capacity, so the fix is more VIP-skilled agents, not more hours.
- Northwind's WFM lead most likely checked the roster with the service's old method, which understates VIP need. The account team needs to take this up with Northwind.

**What I changed.** Everything is switched on from `configs/northwind.yaml` only. `defaults.yaml` is untouched, and Contoso, Fabrikam and Wingtip give byte-identical outputs for W41–W43.
- **Ingest:** the queue list now comes from config; before, VIP was silently dropped. UTC is taken from each row's `utc_offset`, which the clock-change night needs, and the week always has its full set of intervals, with warnings for missing or duplicate rows.
- **Staffing:** each interval's own handle time is now really used (the setting for it was ignored before), and the 0.85 occupancy cap is applied for Northwind only. That cap bug (WFM-212) is still open for the other clients.
- **Scheduler:** a new week-level scheduler (`wfm/scheduler/search.py`) enforces the 11-hour rest, split shifts for part-timers only, the break rule, the one-agent VIP minimum and the hours bound. The old day-by-day scheduler couldn't enforce any of these. A Northwind run takes about 40 seconds.
- **Evaluation and reports:** `eval.json` now counts attainment over operating hours and adds required hours, the efficiency ratio and a check for every §2 rule. `wfm/reconcile.py` writes `RUNBOOK.md` and `exceptions.md` on every run.
- **Housekeeping:** I updated two existing tests that expected Northwind to still be pending, and added 9 new ones; all 89 pass. The registry, `clients/README.md`, ARCHITECTURE and the CHANGELOG are updated. The handover note lives in `docs/clients/northwind.md` and is copied into `RUNBOOK.md` on each run.

**Points to confirm with Northwind** (they're in the handover note, which also covers the §2.8 list of earlier departures from the SOW method):
- **Break window:** I read "between two and five hours" as including the 5-hour mark. On some days the VIP early shift has no other valid break slot, so the rule can't be met without including it. 4 of the W44 breaks start at exactly 5 hours.
- **Split shift:** I don't use the 4+4 split template, because the SOW doesn't say whether it counts as a shift of six hours or more for the break rule.
- **Data:** the W44 export has two off-the-half-hour timestamps (`10:01` on 27 and 29 Oct). They're read as 10:00, but they should be reported to Northwind's WFM contact.
