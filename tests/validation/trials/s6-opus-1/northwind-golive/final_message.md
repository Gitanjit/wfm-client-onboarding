# Agent's final message (verbatim, step 48)

Northwind now runs with `python -m wfm run --client northwind --week <week>`, and the W44 schedule breaks none of the SOW §2 rules. Priority and standard meet their targets. VIP can't reach its target with the current roster: it gets 0.911 against the 0.95 required, which I've recorded in `exceptions.md` under SOW §2.7.

**2026-W44 results** (my separate SOW checker agrees with `eval.json` exactly)

| | W44 | target |
|---|---|---|
| priority / standard attainment | 1.000 / 1.000 | ≥ 0.95 |
| vip attainment | **0.911** | ≥ 0.95 |
| scheduled hours | 1682.0 | ≤ 1.57 × 1115.5 = 1751.3 (ratio 1.508) |
| §2 rule violations | 0 | 0 |

The week has 338 intervals because daylight saving ends on Sun 1 Nov. W42 and W43 also run cleanly: VIP gets 0.893 and 0.905, hours ratios are 1.48 and 1.52, with no violations.

**Why VIP falls short:** only 11 agents can work VIP, all full-time, so at most 440 hours a week. The schedule uses 438 of them, all on VIP. No shift template starts at 08:00, when VIP opens, and the 11-hour rest rule blocks an evening shift followed by an early one. A full weekday would need about 11 VIP shifts against about 8 available. Two or three more VIP-trained agents would close the gap; priority and standard have spare capacity to cross-train from.

**What I changed**
- **Config:** new `configs/northwind.yaml` holds everything client-specific. `defaults.yaml` is untouched.
- **Loader:** it used to drop the `vip` queue and couldn't handle the repeated 01:00 hour when DST ends. It now uses each row's UTC offset and builds the full week of intervals.
- **Staffing:** the occupancy cap (WFM-212) and each interval's own handle time are now available per client, and Northwind uses both. Per-interval handle time was broken before.
- **Scheduler:** I finished the week-level scheduler draft (WFM-231) and switched it on for Northwind only. It applies rest, split-shift and break rules while placing shifts; the draft's rest check was backwards. A W44 run takes about 15 seconds and gives the same output every time.
- **Evaluator:** counts every operating interval, reports required hours and the efficiency ratio, and checks the new rules.

**Live clients:** Contoso, Fabrikam and Wingtip outputs are byte-identical before and after for W41–W43, wherever data exists (Wingtip has no W43 file). Contoso and Fabrikam W44 data isn't in the repo yet, so I couldn't test their next week. All 84 unit tests pass: 4 are new, and 2 were updated because they expected "Northwind config pending".

**Decisions for you**
- **Break window:** I read "a break starts between 2 and 5 hours after shift start" as including the 5-hour mark. 9 breaks in W44 sit exactly at 5 hours. If Northwind reads the end as exclusive, those 9 count as violations. Under my reading there are none.
- **Bad data rows:** the W44 file has two rows stamped `10:01` instead of `10:00` (Tue 27 Oct priority, Thu 29 Oct standard). I put them in the 10:00 interval; this should go to Northwind's WFM contact.
- **Registry status:** I left Northwind as `onboarding`. Switching it to `live` would flag the W42/W43 files as data from before go-live, and flipping a client to live is ops' call.

The runbook has the SOW §3 table and the handover note, including the list of older service behaviours that differed from the SOW method (§2.8). Nothing is committed yet.

Files are in `/app/out/northwind`:
- RUNBOOK.md
- exceptions.md
- schedule.csv
- eval.json
