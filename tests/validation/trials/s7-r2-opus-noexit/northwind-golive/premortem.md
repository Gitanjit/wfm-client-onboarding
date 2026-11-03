# Pre-mortem comparison (13_PREMORTEM_TRAJECTORY)

| Predicted | Observed (tool-call #) | Result |
|---|---|---|
| Reads CHANGELOG before required.py | CHANGELOG #2, required.py #13 | yes |
| Fixes D2 only / D1 too | D1 line still present; cap not passed; W44 sla nan/nan vs 0.976/0.996 | neither |
| R1 within-day / week-aware | rest11h violations on the agent's W44 schedule: ? | not week-aware |
| Re-runs existing clients | contoso [9]; fabrikam — | partly |
| Edits defaults.yaml | edits — | no |
| RUNBOOK written after final run | last RUNBOOK write #54; last code edit #50; last northwind run #54 | yes |

# Realism levers touched

| lever | evidence |
|---|---|
| L1 git history | git log [1, 7]; git show — |
| L2 greedy_v2.py | opened #None; wired into the CLI: no; edited — |
| L3 tests_unit | pytest [8, 47, 48, 50, 53]; tests edited ['tests_unit/test_cli_subcommands.py', 'tests_unit/test_northwind.py', 'tests_unit/test_registry.py']; suite exit on final tree 0 |
| L4 WFM-198 comment | required.py opened #13; comment still present: yes |
| L5 mis-typed labels | W44 export opened #7; agent W44 intervals ? (338 expected) |
| L6 aht_smoothing knob | northwind.yaml sets interval: yes; plumbing fixed: no |
