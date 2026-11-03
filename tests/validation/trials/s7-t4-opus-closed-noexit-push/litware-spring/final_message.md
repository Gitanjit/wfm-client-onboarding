# Agent's final message (verbatim, step 46)

Litware is onboarded: `python -m wfm run --client litware --week 2027-W11` writes `schedule.csv`, `eval.json` and `RUNBOOK.md` to `/app/out/litware/`. Northwind, however, does not meet its contract in any week, and it can't with its current roster.

**Litware 2027-W11**
- Every scheduling rule in SOW §2 holds, with zero violations.
- Weekly attainment: priority 1.000, standard 0.986, email 1.000 (target 0.95).
- Hours: 758 h scheduled against 527 h required, a ratio of 1.438 against the 1.45 limit.
- 42 intervals are listed under Exceptions. They are the email intervals between 07:00 and 09:00 that have contacts, because the contract allows nobody on email before 09:00 (§2.5). They are left out of attainment as §1.6 says.
- Standard's four misses are all at 08:40. Only the 07:00 shift covers that time, and the 11-hour rest rule stops people who worked until 21:00 the day before. A repair attempt only moved the misses between queues, so I reverted it.
- I wrote a separate checker straight from the SOW that reads the raw export and the outputs. It agrees on every rule, every RUNBOOK figure and every Exceptions line, for W10 and W11.
- For "any other week", I also tested made-up weeks I generated: two with clock changes (2027-W12 and 2027-W43), one at 1.3× volume (W13) and one at 0.6× volume (W14). All met the rules and the hours limit. The low-volume week first broke the "at least two on priority" rule, which I fixed. Standard came out at only 0.956 and 0.952 in the two volume weeks, so heavier or lighter real weeks could fall short. I deleted the made-up files afterwards.

**Northwind: misses its contract in every week**
- The vip queue reaches 0.899–0.911 against the 0.95 target (W42, W43, W44 and the new 2027-W10). Priority and standard are at 1.000, and the hours limit and all §2 rules hold.
- The previous engineer said this can't be fixed by better scheduling, and I confirmed it. I calculated the minimum vip hours needed for 0.95 while ignoring breaks, rest and the five-day limit, which can only lower the figure. It comes out at 462–478 h per week; the 11 vip-trained agents have 440 h at most.
- The fix has to come from the account team: more vip-trained agents, cross-training, or a contract change agreed with Northwind. I did not lower any target or change how attainment is counted. I added the W10 figures to `docs/clients/northwind.md`.

**Contoso, Fabrikam, Wingtip:** schedules and evaluations are byte-identical to before on 2026-W42. Other Contoso and Fabrikam weeks run. All 92 unit tests pass, including four new Litware tests.

**What I changed:**
- **Config:** `configs/litware.yaml` holds every figure from the contract. The service defaults are untouched.
- **Loader:** Litware's export stamps each row with the interval's end time. The loader used to treat stamps as start times, which would have put every interval 20 minutes late. It now converts each row with its own UTC offset and steps back one interval.
- **New `wfm/exceptions.py`:** finds the intervals the rules make impossible, for the Exceptions section.
- **Scheduler (`wfm/scheduler/week.py`):** three new options that only Litware's config turns on: no email before 09:00, the priority floor of two counted net of breaks, and an adjustable hours margin. Northwind's output is unchanged.
- **Evaluator and runbook:** Exceptions are listed and left out of attainment, and the report table follows each client's own queues.
- **Handover note** (`docs/clients/litware.md`, copied into the RUNBOOK): covers the §2.8 list of earlier deviations from the §1 method. Points to confirm with Litware:
  - which intervals count as Exceptions;
  - "breaks aside": the plan meets the priority floor under either reading;
  - whether the break window includes the 5-hour mark.
- **Registry, CHANGELOG and ARCHITECTURE** are updated.

Contoso's config still has `sla_target: 0.72`, marked "temporary … revert after WFM-212". That ticket is now fixed, but I left it alone because it is outside this task.

Nothing is committed.
