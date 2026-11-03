# Agent's final message (verbatim, step 44)

Litware is onboarded. `python -m wfm run --client litware --week 2027-W11` writes `schedule.csv`, `eval.json`, `RUNBOOK.md` and `exceptions.md` to `/app/out/litware/` in about 30 seconds. I checked the output with a separate script written from the SOW alone, not the service's own evaluator, and its figures match `eval.json` and the RUNBOOK exactly.

**Litware 2027-W11**
- **Attainment:** 1.000 on priority, standard and email.
- **Hours:** 742.0 h scheduled against 527.0 required (ratio 1.408; the limit is 1.45).
- **Agents:** all 24 are used.
- **Rule violations:** none.
- **Exceptions (§2.6):** 42 intervals, all email between 07:00 and 09:00 local. Email arrives from 07:00, but nobody may work email before 09:00. These intervals stay in required hours and are left out of attainment, as §1.6 says.
- **Other weeks:** 2027-W10 also reaches 1.000 on every queue (734 h, ratio 1.388). Synthetic weeks I built around both clock changes (spring forward and fall back) run correctly. I deleted those test files afterwards.

**What changed** (all switched on only in `configs/litware.yaml`; `defaults.yaml` is untouched):
- **Loader:** Litware stamps each row with the end of its interval. The old reader treated every label as a start, which would have put all Litware demand 20 minutes late.
- **Email start (§2.5):** a new setting, `queue_start_hours: {email: 9}`. The scheduler respects it and the evaluator audits it.
- **Exceptions:** a new module, `wfm/infeasible.py`, finds intervals the rules make impossible. They are listed under `## Exceptions` in the RUNBOOK, with times in UTC.
- **Priority floor (§2.4):** at least two agents, counted net of breaks, so it holds on either reading of "breaks aside".
- **Templates:** D8, L8, P6a, P6b and P4, now listed per client in ARCHITECTURE.
- **Scheduler search:** two new options, Litware only. One lets the search move shifts between queues, which fixed W10 standard (it had nobody 07:00–09:00 on Tuesday). The other makes it avoid breaks at exactly +5 h unless that costs attainment.
- **Paperwork:** registry and client list, a client note, the handover note, CHANGELOG, and 4 new tests. All 91 tests pass.

**Other clients:** Contoso, Fabrikam and Wingtip produce byte-identical output for 2026-W42, and Northwind's 2027-W10 output is identical to its run before my changes. Northwind's new W10 export (a US clock-change week) runs, with vip at 0.905. `exceptions.md` records that shortfall under §2.7, as the roster limit the earlier onboarding documented.

**Decision for you:** 3 of this week's breaks start exactly 5 hours into the shift. That's valid if "between two and five hours" includes five, which is how the existing evaluator reads it. Forcing every break strictly inside the window dropped W10 standard attainment to about 0.96–0.98, so I chose attainment. If Litware reads the window as excluding five hours, those 3 breaks become violations.

The RUNBOOK's handover note covers what changed and why, and the eight §1 deviations the service had before Litware. Nothing is committed yet.
