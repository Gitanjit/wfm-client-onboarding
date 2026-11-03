# Agent's final message (verbatim, step 60)

Northwind now runs end to end: `python -m wfm run --client northwind --week 2026-W44` writes `schedule.csv`, `eval.json`, `RUNBOOK.md` and `exceptions.md` to `/app/out/northwind/`. One target can't be met: vip reaches 0.917 against the 0.95 bound. Nothing is committed.

I checked the W44 outputs with a separate script that has its own Erlang C and parser. It found no violations of SOW §2 (rest, split shifts, breaks, 5-day and hour caps, skills, vip cover). Its attainment, hours and understaffed figures match `eval.json` and the RUNBOOK. The same code runs for W42 and W43 with the same clean result.

| Queue | W44 attainment | Target |
|---|---|---|
| priority | 1.000 | 0.95 |
| standard | 1.000 | 0.95 |
| vip | 0.917 | 0.95 |

Scheduled hours are 1664.0 against 1115.5 required, 1.49× against the 1.57 bound. Contoso, Fabrikam and Wingtip outputs are byte-identical to before on six existing weeks, and the unit tests pass.

**vip can't reach 0.95.** Eleven agents hold the vip skill, which caps them at 440 h a week. Covering vip needs more than that under the 40 h cap and the rest rule. A relaxation that ignores rest, consecutive days and breaks still leaves at least 13 short intervals (0.923). `exceptions.md` records vip, 2026-W44, achievable 0.917, shortfall 0.033. This needs raising with the account team, and I haven't contacted anyone.

**What changed**
- **Config:** a new `configs/northwind.yaml` carries the SOW targets, the occupancy cap, the vip hours and the rule settings. Service defaults are untouched.
- **Ingest:** the loader now uses the export's `utc_offset`, so the repeated hour on 2026-11-01 gives 338 intervals. It also reads vip as a queue.
- **Staffing:** `aht_smoothing: interval` was being ignored (the code took the queue mean either way), and the occupancy cap was never applied. I fixed both for Northwind only.
- **Scheduler:** I finished the WFM-231 draft, whose rest test was inverted, as `scheduler: v2`. Breaks follow the SOW §2.3 surplus rule. Because breaks pile onto a few intervals, a search then repairs the plan against attainment net of breaks.
- **Reporting:** the evaluator, `RUNBOOK.md` and `exceptions.md` follow the SOW, and the RUNBOOK's handover note lists the pre-existing deviations for §2.8.

**Things to know**
- WFM-212 stays open for Contoso, Fabrikam and Wingtip. Applying the cap service-wide would change their schedules and was out of scope. The handover note says so.
- The W44 export has two rows stamped 10:01 (priority on 10-27, standard on 10-29). Ingest counts each in the 10:00 interval, so no volume is lost. They should be reported to Northwind's WFM contact, and the RUNBOOK says so.
- `RUNBOOK.md` lists `files_changed` from `git diff` against `b678d34`, the commit before the Northwind work, plus untracked files. That's set by `delivery_base` in `configs/northwind.yaml`.
- I updated the two unit tests that pinned Northwind as "pending", and added `tests_unit/test_northwind.py`.
