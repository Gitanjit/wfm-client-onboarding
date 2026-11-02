# 0003 — Deterministic scheduling

Date: 2024-11-21 · Status: accepted · Author: Dana Vexley

## Context

Weekly schedules are compared with the previous week, re-run after data corrections and reviewed as
diffs. A planner that gives a different answer on every run makes all three useless: a reviewer
cannot tell a change caused by new data from noise.

## Decision

- No randomness in planning code. Template order is fixed; ties between agents are broken by
  `agent_id`; every output is sorted before it is written.
- The same inputs (data file, config, roster, code) give byte-identical `schedule.csv` and `eval.json`.
- Anything outside the service that needs random numbers (synthetic test data, sampling) takes an
  explicit seed.

## Consequences

- Re-running a week after a fix shows exactly what the fix changed; `diff` is the review tool.
- The greedy placement does not search, so it can miss better schedules. A future solver must keep this
  property: fixed seeds, stable sorts, no dependence on dictionary or set iteration order.
