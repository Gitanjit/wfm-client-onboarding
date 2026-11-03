# Agent's final message (verbatim, step 46)

Litware is onboarded. `python -m wfm run --client litware --week 2027-W11` writes `/app/out/litware/schedule.csv`, `eval.json` and `RUNBOOK.md`. I checked every output with a separate SOW checker I wrote that doesn't use the service's code. All 89 unit tests pass. Nothing is committed.

## Litware 2027-W11

| | result | SOW requirement |
|---|---|---|
| Attainment: priority / standard / email | 1.000 / 0.997 / 1.000 | ≥ 0.95 each |
| Scheduled vs required hours | 590.0 / 527.0 = 1.12× | ≤ 1.45× |
| §2 rule violations | 0 | 0 |
| Exceptions (§2.6) | 42 | — |

- **Exceptions:** all 42 are email intervals between 07:00 and 09:00. Email contacts arrive from 07:00, but §2.5 bars email staff before 09:00, so these can't be met. The handover note asks Litware to confirm.
- **Audit (§1.7):** `eval.json` and the RUNBOOK agree with my independent recalculation to within 0.0004 on every queue.
- **Priority cover (§2.4):** "breaks aside" could mean agents on break still count, or that they don't. The schedule keeps at least two priority agents even net of breaks, so it meets either reading.
- **Other weeks:** 2027-W10 also passes. Synthetic weeks I generated and then deleted also passed: a spring-forward week (501 intervals), a fall-back week (507), and weeks at 1.3× and 1.6× volume.

## What changed
- **`configs/litware.yaml`** holds every Litware rule. `defaults.yaml` is untouched.
- **Data loading:** Litware stamps each row with the time its interval *ends*. Read as a start time, every interval would land 20 minutes late, so the loader now converts these rows.
- **New per-client settings:**
  - `queue_earliest_start`: no email before 09:00.
  - `min_cover_net`: floors hold net of breaks.
  - `exceptions`: impossible intervals are listed in `eval.json` and the RUNBOOK, and left out of attainment.
- **Bug fix in the post-scheduling optimisation (`wfm/scheduler/improve.py`):** if the first draft went over the hours bound, it rejected every change, even ones that cut hours. Litware's first draft was at 1.48× with three priority-cover gaps and couldn't recover. This fix changes no existing client's output.

## Existing clients
- **Contoso and Fabrikam:** schedules and evals are byte-identical for all their weeks.
- **Northwind:** I turned on `min_cover_net` and raised its optimisation margin from 0.02 to 0.03. For every week from 2026-W42 to 2027-W10, each queue is at or above its previous attainment. There are zero violations, and hours are 1.14–1.17× required against the 1.57 bound. A synthetic Northwind fall-back week also passed.

## Before you commit
- The earlier Northwind onboarding was never committed, and Litware builds on it. The RUNBOOK's `files_changed` therefore lists everything that differs from the last commit, including those Northwind files; the handover note explains this.
- Litware is listed in `clients/registry.yaml` as `onboarding` until ops confirm go-live.
