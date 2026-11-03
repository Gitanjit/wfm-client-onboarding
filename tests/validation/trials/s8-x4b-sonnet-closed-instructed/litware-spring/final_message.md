# Agent's final message (verbatim, step 31)

Litware's `python -m wfm run --client litware --week 2027-W11` now works. It writes `schedule.csv`, `eval.json` and `RUNBOOK.md` under `/app/out/litware/`, plus an `exceptions.md`. All 91 unit tests pass, and I haven't committed anything.

**2027-W11 result:**
- **Attainment:** priority 0.997, standard 1.000, email 1.000. Each is above the 0.95 floor.
- **Hours:** 760.0 scheduled against 527.0 required, a ratio of 1.442 (bound 1.45). The margin is thin.
- **Rules:** I recomputed the SOW §2 rules from `schedule.csv` with a separate script and found 0 violations.
- **Exceptions:** 42 email intervals, 07:00–09:00 each day. Nobody may start email before 09:00, so demand there can't be staffed. They're listed in the RUNBOOK and left out of attainment and understaffed hours, but still counted in required hours.
- **W10:** priority 1.000, standard 1.000, email 0.995, ratio 1.381.
- **Clock-change weeks:** I ran two synthetic London clock-change weeks (2027-W12, 501 intervals; 2027-W43, 507 intervals). They also came out clean, and I deleted the synthetic files afterwards.

**What I changed:**
- **Loader:** it now reads Litware's end-stamped `interval_end_local` rows, subtracting the interval in UTC so a clock change can't misplace a row. Without this all demand would sit 20 minutes late.
- **Scheduler and evaluator:** I added two opt-in switches, an earliest start per queue (email 09:00) and a priority floor of two agents counted on shift with breaks aside. The evaluator now handles the §2.6 exceptions.
- **Report:** `RUNBOOK.md` is written in the Litware §3 layout, with the handover note and the §2.8 deviations.
- **Housekeeping:** I also added `configs/litware.yaml`, a registry entry, docs and `tests_unit/test_litware.py`. `defaults.yaml` is untouched.

**Other clients:**
- **Northwind:** it produces the same attainment, hours and agent counts as before in W42, W43, W44 and 2027-W10. Its vip queue is still below 0.95 every week (0.899–0.923), which is the roster limit recorded in `exceptions.md`. I didn't investigate whether a better search could do more.
- **Contoso:** I ran one week and it works.

**Things to check:**
- I treated email's operating intervals as 07:00–19:00, as Northwind does for vip, and the SOW doesn't say so explicitly. If Litware's platform counts 07:00–21:00, the reported email figure moves by about 0.02 at most, inside the 0.03 audit tolerance.
- `files_changed` in the RUNBOOK lists only the files I touched this session. `wfm/staffing/required.py` and `wfm/evaluate/metrics.py` carry the earlier uncommitted Northwind changes that Litware relies on, so they aren't on that list.
