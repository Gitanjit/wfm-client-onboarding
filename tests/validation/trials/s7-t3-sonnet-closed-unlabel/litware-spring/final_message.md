# Agent's final message (verbatim, step 53)

`python -m wfm run --client litware --week 2027-W11` now writes `schedule.csv`, `eval.json` and `RUNBOOK.md` under `/app/out/litware/`, and the schedule meets every SOW §2 rule I checked. I checked it with a separate script that doesn't import `wfm`. I haven't committed anything.

**Litware W11**
- All three queues reach 1.000 attainment.
- Scheduled hours are 718.0 against a bound of 764.1, which is 1.45 × the 527.0 required hours.
- The independent script found no violations on rest, split shifts, breaks, priority cover, email start, hours or consecutive days. It also confirmed `eval.json`'s attainment exactly.
- W10 came out the same, and `exceptions.md` has no rows.
- The Exceptions section lists 42 email intervals a week, 07:00–09:00 local. They have demand, but §2.5 bars anyone from email before 09:00.
- DST weeks are not covered by real data. I generated synthetic London weeks for the clock changes (501 and 507 intervals) and they ran clean. I deleted those files afterwards.

**What was changed for Litware**
- **Ingest:** reads the export stamped with the interval end, using the row's own UTC offset.
- **Config:** `configs/litware.yaml` holds all client-specific settings, so the service defaults are untouched.
- **Scheduler:** email shifts can't start before 09:00.
- **Reporting:** attainment excludes the §2.6 intervals. The runbook writer now builds its table from each client's queues.
- **Tests and docs:** `tests_unit/test_litware.py` was added, the registry, README, changelog and architecture notes were updated, and the handover note is `docs/clients/litware.md`. The note lists seven §2.8 deviations that were in effect before this change.
- **Test suite:** 97 tests pass.

**Existing clients**
- **Contoso, Fabrikam, Wingtip and Proseware:** every committed week gives byte-identical `schedule.csv` and `eval.json` compared with HEAD. I did not re-run the three retired clients (Tailspin, Woodgrove, Adatum).
- **Northwind (all four weeks, W10 included):** no rule violations and hours under the 1.57 bound. **`vip` attainment is 0.905–0.917, below the 0.95 target.** The shortfall is recorded in `out/northwind/exceptions.md` as §2.7 asks. Letting the 11 vip agents work 48 h instead of 40 h lifts vip attainment to 0.97, so their weekly hours are what limit it. Relaxing the rest rule doesn't help. I haven't proven the current figure is the maximum.

I read §1.4 literally, so 19:00–21:00 email intervals count as operating and as met. That is about 14% of the email denominator. If Litware counts only 07:00–19:00, the email figure moves by under 0.01.

`files_changed` in the RUNBOOK lists every path that differs from HEAD, including Northwind's earlier uncommitted work. The only exceptions are the Litware SOW and the data files.
