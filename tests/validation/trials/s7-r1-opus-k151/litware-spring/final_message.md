# Agent's final message (verbatim, step 42)

Litware is onboarded. `python -m wfm run --client litware --week 2027-W11` writes `schedule.csv`, `eval.json`, `RUNBOOK.md` and `exceptions.md` under `/app/out/litware/`. They meet the SOW, and a separate checker I wrote from the SOW text (`/tmp/check/verify.py`) agrees with every reported figure.

**Litware results**

| week | priority | standard | email | hours / required | rule violations |
|---|---|---|---|---|---|
| 2027-W11 | 1.000 | 1.000 | 0.988 | 657 / 527 = 1.247 (bound 1.45) | 0 |
| 2027-W10 | 1.000 | 1.000 | 0.992 | 666 / 528.7 = 1.260 | 0 |

- **Exceptions (§2.6):** each week has 42 email intervals from 07:00 to 09:00, six a day. Email contacts arrive then, but §2.5 bars anyone from email before 09:00. They stay in the week and in required hours, are left out of attainment, and are listed under `## Exceptions`.
- **Checker:** it recomputes attainment, hours and the exception list from the raw export and `schedule.csv`, and checks every §2 rule. Its figures match `eval.json` and the RUNBOOK on every key.
- **Other weeks:** I tested synthetic Litware weeks. The spring-forward week (501 intervals), the fall-back week (507), and volume from 0.6× up to 1.6× all came out clean. At 1.6× the scheduler first broke the two-agent priority floor in 3 intervals. I added a repair pass that only runs when a floor is short, which fixed it. That week takes about 50 s to run; real weeks take about 3 s.

**Existing clients**
- Northwind 2027-W10 (its spring-forward week) meets its SOW: vip 0.970, ratio 1.374 against 1.51. Its outputs are byte-identical to before my changes.
- Northwind W42–W44 still pass every check, with vip at 0.976–0.988.
- Contoso and Fabrikam use code paths I didn't touch, and both still run.
- All 90 unit tests pass, including the new `tests_unit/test_litware.py`.

**What changed.** Everything new is switched on by keys in `configs/litware.yaml`; the defaults are unchanged.
- **Loader:** reads Litware's export, which stamps each row with the end of its interval rather than the start.
- **New key `queue_staff_hours`:** keeps everyone off email before 09:00, and the evaluator now audits it.
- **New key `infeasible_intervals`:** marks intervals the rules make impossible to staff and leaves them out of attainment.
- **RUNBOOK:** the table keys now follow each client's queues, and Litware's report adds the Exceptions section and the `exception_intervals` key.
- **Templates:** Litware gets its own 8, 6, 5 and 4-hour shifts starting on every hour.
- **Registry and docs:** Litware added to the registry and to the architecture notes and changelog.

The handover note is in `docs/clients/litware.md`, and each run copies it into RUNBOOK.md. It lists the §2.8 deviations Litware would have inherited from the service defaults. The main one is the default weekly-average handle time, which would understate W11's required hours (524.3 against 527.0 by the SOW method). It also covers start-stamped ingest, the attainment denominator, cross-skilled agents counting toward floors, and midpoint breaks. It warns not to copy Fabrikam's abandonment model or coverage scoring, or Contoso's lowered target.

**Decisions for you**
- **Email's operating hours.** I read them as 07:00–21:00, the same as the other queues, because the SOW doesn't narrow them the way Northwind's does for vip. Email after 19:00 has no volume, so those intervals count as met. Reading them as 07:00–19:00 instead would only move email attainment by about 0.004, well inside the 0.03 audit tolerance.
- **Contoso's `sla_target: 0.72`.** Its own comment says to revert it after WFM-212, which is now fixed. I left it alone because it is outside Litware's scope and only changes the `meets_target` verdict in `eval.json`; it's flagged in the handover note for Contoso's account team.

`out/litware/RUNBOOK.md` currently holds W11; running another Litware week will overwrite it. Nothing has been committed.
