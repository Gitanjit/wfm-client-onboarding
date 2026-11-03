# Agent's final message (verbatim, step 68)

Litware 2027-W11 is delivered: `out/litware/schedule.csv`, `eval.json`, `RUNBOOK.md`, and `exceptions.md`. All three SOW targets are met with zero §2 violations, and the existing clients' schedules are unchanged. Nothing is committed. I built on the uncommitted Northwind work already in the tree and didn't revert it.

**Litware 2027-W11 results**

| queue | attainment (§1.6) | target |
|---|---|---|
| priority | 0.959 | 0.95 |
| standard | 0.973 | 0.95 |
| email | 0.990 | 0.95 |

- Scheduled hours are 736.0 against 527.0 required, a ratio of 1.40 under the 1.45 bound.
- The RUNBOOK has all §3 keys, 42 §2.6 exceptions (email 07:00–09:00 each day, which §2.5 makes unstaffable), and the handover note.

**What changed**
- `configs/litware.yaml` holds every SOW term, each tied to its section.
- The loader reads Litware's end-stamped export and starts each interval one grain earlier.
- Two new keys, both off by default: `queue_start_hours` implements the §2.5 email start rule, and `plan_first` plans email for the whole week first, because the greedy was spending its five email agents on standard. Without that, email was at 0.905.
- §2.6 intervals are left out of attainment and understaffed hours, as §1.6 and §3 require. The evaluator audits the start rule and reports the exceptions.
- `wfm sow` writes the RUNBOOK's `exception_intervals` key and the `## Exceptions` section.
- I fixed a latent bug: the five-consecutive-day check only looked at earlier days. A queue planned first could then exceed five days. The handover lists it under §2.8.

**Verification**
- The 86 existing unit tests pass, along with 6 new Litware tests (92 total).
- All 10 existing client-weeks (Contoso, Fabrikam, Wingtip, Northwind 2026-W42–W44) produce byte-identical schedules to the pre-change tree.
- Litware 2027-W10 also meets 0.95 on every queue (priority 0.956).
- I built a synthetic 2027-W12 by shifting W11 a week in UTC. It contains the 28 March DST change, and it ran with zero violations and all targets met. This is my construction, not real data.
- A fresh agent, given only the SOW and raw data, reproduced the §3 figures and found no §2 violations. Its email attainment is 0.992 against my 0.990, within the §1.7 tolerance.

**Open items**
- **Priority margin is thin.** It has two spare misses against 0.95. Most shortfalls come from breaks landing on the same surplus interval, and priority, as the floor queue, is never repaired. I tried repairing it and standard fell to 0.935, so I didn't adopt that.
- **Northwind W10:** vip is 0.839, so §2.7 requires an exceptions row: `vip | 2027-W10 | 0.839 | 0.111`. Priority and standard are 1.0, and the schedule is 1.523× required with zero violations. I did not write this into `out/northwind`, because that directory holds the 2026-W44 run and its RUNBOOK. Tell me if you want it there.
- **Readings to confirm with Litware:** understaffed hours are net of breaks (10.3), and zero-volume intervals count as meeting target. The §2.6 set is the 42 email intervals before 09:00 that carry demand.
- The registry entry for Litware is `onboarding`, following the Northwind pattern. I updated three tests that pinned the old client count.
