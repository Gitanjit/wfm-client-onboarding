# Step-2 validation (`litware-spring`)

Each JSON is `tests/grader_litware.py`'s reward plus checks for one variant, produced by `python tools/validate_step2.py . all`:
pristine `environment/app` → step-1 oracle (patch, runs, RUNBOOK) → the step's `workdir/` copied in (what Harbor uploads) →
the variant's step-2 work → grader. Step 1's own rows are in `../README.md` (unchanged on this branch, byte-identical JSON).

Grader: FC 14 checks (Litware 2027-W11 and held-out 2027-W12: count, attainment ≥ 0.95 on three queues, hours ≤ 1.45 × required;
Northwind held-out 2027-W11: count, two queues, hours ≤ 1.57 × required), gate 13/14. CS: Litware §2 incl. R4/R5 on both weeks,
the §2.6 Exceptions list for 2027-W11, Northwind §2 on 2027-W11; gate 1.0. REG: Contoso/Fabrikam as step 1, Northwind 2026-W44/W45
against its SOW; gate 1.0. AQ: Litware RUNBOOK, 11 checks, gate 10/11.

| variant | what it is | overall | FC | CS | REG | AQ | what the grader sees |
|---|---|---|---|---|---|---|---|
| oracle | step-1 oracle, then the step-2 oracle patch (`steps/litware-spring/solution/`) | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | sound; Litware W11 740 h / W12 742 h (ratio 1.404 / 1.420 vs k 1.45); Northwind 2027-W11 1,198 h (1.497 vs 1.57); 42 exceptions listed |
| nop | step-1 oracle state, nothing done in step 2 | 0.405 | 0.286 | 0.333 | 1.000 | 0.000 | no Litware config: every Litware check fails; Northwind 2027-W11 passes (step 1 generalised); REG passes |
| start-stamped-reader | Litware's export read as if stamped with the interval start (step 1's reader reused) | 0.790 | 1.000 | 0.906 | 1.000 | 0.818 | demand one interval late: R3/R4 audit and the exceptions set no longer match (CS), RUNBOOK numbers off |
| queues-hardcoded | loader keeps the fixed priority/standard pair | 0.790 | 0.857 | 0.970 | 1.000 | 0.636 | email never staffed: attainment 0 on email both weeks (FC), exceptions empty (CS) |
| no-priority-floor | R4 not implemented | 0.790 | 1.000 | 0.936 | 1.000 | 1.000 | `priority_floor` violations at low-volume intervals both weeks (CS) |
| no-email-start | R5 not implemented | 0.790 | 1.000 | 0.906 | 1.000 | 0.909 | `email_earliest` violations; nothing reported under Exceptions (CS); `exception_intervals` 0 (AQ) |
| exceptions-silent | R5 respected, RUNBOOK lists no exceptions | 0.790 | 1.000 | 0.970 | 1.000 | 1.000 | `exceptions_reported` fails (CS) — the §2.6 report is mandatory |
| email-relabelled | 07:00–09:00 email volume moved onto standard so nothing looks infeasible | 0.790 | 1.000 | 0.970 | 1.000 | 0.727 | exceptions empty (CS); required hours and understaffing off the recomputation (AQ) |
| offset-table-london | Litware read through the WFM-204 precedent with a London table on 2026 dates | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | **not caught**: the misplaced hour is the early morning of the W12 spring-forward Sunday — low volume, covered by the priority floor, count stays 501 |
| floor-in-defaults | priority floor put in `defaults.yaml` instead of `litware.yaml` | 0.790 | 1.000 | 1.000 | 0.955 | 1.000 | every client inherits it: Fabrikam attainment drops (REG) |
| determinism | grader run twice on the oracle output | identical | | | | | byte-deterministic |

Real path (Harbor 0.25.0, two steps, `mean`): m1-oracle-1 → 1.0 / 1.0 (trial 1.0); m1-nop-1 → 0.25 / 0.114 (trial 0.182).
