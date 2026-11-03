# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #1 | 3 |
| `docs/NORTHWIND_SOW.md` | #2 | 7 |
| `docs/CHANGELOG.md` | #3 | 3 |
| `data/northwind/README.txt` | #4 | 1 |
| `configs/defaults.yaml` | #4 | 2 |
| `configs/contoso.yaml` | #8 | 1 |
| `configs/fabrikam.yaml` | #4 | 1 |
| `wfm/ingest/loader.py` | #5 | 4 |
| `wfm/staffing/required.py` | #13 | 3 |
| `wfm/staffing/erlang.py` | #45 | 1 |
| `wfm/scheduler/greedy.py` | #6 | 6 |
| `wfm/scheduler/greedy_v2.py` | #6 | 1 |
| `wfm/scheduler/templates.py` | #6 | 1 |
| `wfm/evaluate/metrics.py` | #6 | 4 |
| `wfm/cli.py` | #5 | 5 |
| `wfm/config.py` | #5 | 1 |
| `wfm/roster.py` | #5 | 1 |
| `tests_unit/test_staffing.py` | #11 | 1 |
| `tests_unit/test_scheduler.py` | #46 | 1 |
| `tests_unit/test_config_and_loader.py` | #46 | 1 |
| `data/northwind/export_2026-W44.csv` | #4 | 5 |

## Never opened


## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | #24 |
| git show | — |
| git diff | #14, #44 |
| git status | #1, #4, #45, #52 |
| pytest | #8, #41, #44, #47, #48, #51 |
| run northwind | #39, #45, #51, #52 |
| run contoso | — |
| run fabrikam | — |

## Edits and writes

- #25 `/app/wfm/scheduler/search.py`

Bash commands that write files (scripted edits): #9, #11, #12, #13, #14, #15, #16, #19, #20, #22, #26, #27, #28, #29, #31, #32, #33, #34, #35, #38, #39, #40, #44, #45, #47, #48, #49, #51, #52
