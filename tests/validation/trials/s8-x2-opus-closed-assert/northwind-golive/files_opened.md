# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #1 | 2 |
| `docs/NORTHWIND_SOW.md` | #2 | 2 |
| `docs/CHANGELOG.md` | #1 | 2 |
| `data/northwind/README.txt` | #2 | 1 |
| `configs/defaults.yaml` | #3 | 1 |
| `configs/contoso.yaml` | #3 | 1 |
| `configs/fabrikam.yaml` | #3 | 1 |
| `wfm/ingest/loader.py` | #4 | 3 |
| `wfm/staffing/required.py` | #4 | 2 |
| `wfm/staffing/erlang.py` | #4 | 1 |
| `wfm/scheduler/greedy.py` | #5 | 1 |
| `wfm/scheduler/greedy_v2.py` | #6 | 1 |
| `wfm/scheduler/templates.py` | #5 | 2 |
| `wfm/evaluate/metrics.py` | #5 | 4 |
| `wfm/cli.py` | #3 | 4 |
| `wfm/config.py` | #3 | 1 |
| `wfm/roster.py` | #4 | 1 |
| `tests_unit/test_staffing.py` | #10 | 1 |
| `tests_unit/test_scheduler.py` | #8 | 1 |
| `tests_unit/test_config_and_loader.py` | #10 | 1 |
| `data/northwind/export_2026-W44.csv` | #2 | 14 |

## Never opened


## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | #6 |
| git show | — |
| git diff | #14, #51, #56 |
| git status | #58 |
| pytest | #10, #44, #45, #47, #53, #58 |
| run northwind | #27, #33, #34, #36, #39, #41, #43, #44, #54, #55, #57, #58, #59 |
| run contoso | #12, #44 |
| run fabrikam | #44 |

## Edits and writes

- #15 `/app/configs/northwind.yaml`
- #17 `/app/wfm/scheduler/search.py`
- #48 `/app/wfm/reconcile.py`
- #50 `/app/docs/clients/northwind.md`
- #52 `/app/tests_unit/test_northwind.py`

Bash commands that write files (scripted edits): #14, #16, #18, #20, #21, #22, #23, #24, #26, #27, #28, #32, #33, #34, #35, #36, #39, #41, #43, #47, #49, #51, #54, #55, #56
