# Agent's final message (verbatim, step 37)

Litware's `python -m wfm run --client litware --week 2027-W11` now writes `schedule.csv`, `eval.json`, `RUNBOOK.md` and `exceptions.md` to `/app/out/litware/`. The unit tests pass (92). I also checked the W11 schedule with a separate script that recomputes Erlang C and the §2 rules directly from the raw export and the written schedule. It found no violations, and its figures match `eval.json`.

**Litware W11 result**
- **Attainment:** 1.000 on `priority`, `standard` and `email`.
- **Hours:** 746.0 scheduled against 527.0 required, a ratio of 1.416 against the 1.45 limit.
- **Exceptions:** 42 intervals are listed, all `email` between 07:00 and 09:00 local. §2.5 bars email agents before 09:00, so those intervals can't be met. They are excluded from attainment and understaffed hours, and the planner doesn't try to cover them.
- **Other weeks:** it also ran clean on W10 and on synthetic DST weeks (spring-forward W12, fall-back W43). I built the DST exports myself from W11 data, so their format is my guess.

**What I changed**
- **Ingest:** Litware stamps each row with the end of its interval, so the loader now steps back 20 minutes after applying the row's UTC offset. Reading the stamps as starts would shift all demand 20 minutes late.
- **Config:** `configs/litware.yaml` holds the SOW targets and rules, and `defaults.yaml` is untouched.
- **Scheduler and evaluator:** the Northwind scheduler, evaluator and report code is reused, with two additions:
  - A rule that bars `email` from templates starting before 09:00, and the §2.6 exception handling that goes with it.
  - A break tie-break that prefers start times strictly inside the 2–5 hour window, so the schedule is valid whether or not the window's ends count. This is on for Litware only.
- **Report:** the reconciliation report now takes its queues from the client's config and adds the `exception_intervals` key and `## Exceptions` section for Litware.
- **Housekeeping:** I added Litware to the client registry and README, plus docs, a CHANGELOG entry and `tests_unit/test_litware.py`.
- **Handover note:** it is in `docs/clients/litware_handover.md` and embedded in `RUNBOOK.md`. It lists six service deviations that predate Litware (for example the occupancy cap not being applied, queue-mean handle time and the 80/20 defaults).

**Existing clients**
- **Contoso, Fabrikam and Wingtip:** schedules and `eval.json` are byte-identical to before.
- **Northwind W44:** the schedule is identical to before.
- **Northwind other weeks:** its other weeks, including the new W10 file (a 334-interval DST week), run with no rule violations. `vip` stays short of 0.95 (0.905 in W10), and each week's `exceptions.md` records the achievable value and shortfall.
- **Reverted tie-break:** my first version of the break tie-break lowered Northwind W44 `vip` from 0.917 to 0.911. I made it opt-in for Litware, which restored the old result exactly.

**Judgment calls**
- **Email attainment:** I counted email attainment over all operating hours, 07:00–21:00, rather than only the 07:00–19:00 arrival window. The 19:00–21:00 intervals have no volume, so they count as met. The SOW doesn't say which, and with every interval met the choice doesn't change today's figures.
- **Not committed:** nothing is committed. The Northwind work was already uncommitted in the tree and is still there.
