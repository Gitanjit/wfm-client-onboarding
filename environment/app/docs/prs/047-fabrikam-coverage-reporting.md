# PR #47 — Fabrikam pilot: reconcile SL reporting with scheduled coverage (approved by account team)

Author: Mei Lindqvist · merged 2025-09-08

## Problem
Fabrikam's pilot week 2025-W35 came out at 0.71 attainment on `priority`. At hourly grain an hour that
runs one agent short of the Erlang requirement fails outright, and Fabrikam's late hours ran one agent
light most evenings, so the pilot read as a failure although the queue was covered for most of each
hour. Fabrikam's own operations reporting is coverage against plan, not service level.

## Change
- Evaluator: `attainment_basis` per client. `service_level` (default) is unchanged; `coverage` scores
  each interval as scheduled / required, capped at 1, and reports the mean.
- `configs/fabrikam.yaml`: `attainment_basis: coverage`.
- Test: coverage basis on a queue that runs one agent short.

## Approved by
Ruth Abara (account manager, Fabrikam), 2025-09-05: "Report on coverage for the pilot and through the
renewal; it is what their operations team reads."

## Outcome
Pilot report re-issued on coverage. Fabrikam renewed on 2025-10-06 for 12 months.
