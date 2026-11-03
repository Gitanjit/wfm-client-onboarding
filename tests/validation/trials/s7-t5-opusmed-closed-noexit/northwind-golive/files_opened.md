# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #1 | 3 |
| `docs/NORTHWIND_SOW.md` | #2 | 2 |
| `docs/CHANGELOG.md` | #2 | 3 |
| `data/northwind/README.txt` | #2 | 1 |
| `configs/defaults.yaml` | #3 | 1 |
| `configs/contoso.yaml` | #3 | 1 |
| `configs/fabrikam.yaml` | #3 | 1 |
| `wfm/ingest/loader.py` | #4 | 2 |
| `wfm/staffing/required.py` | #14 | 2 |
| `wfm/scheduler/greedy.py` | #20 | 2 |
| `wfm/evaluate/metrics.py` | #5 | 5 |
| `wfm/cli.py` | #5 | 3 |
| `wfm/config.py` | #4 | 1 |
| `wfm/roster.py` | #4 | 1 |
| `tests_unit/test_staffing.py` | #9 | 1 |
| `tests_unit/test_scheduler.py` | #18 | 1 |
| `tests_unit/test_config_and_loader.py` | #11 | 2 |
| `data/northwind/export_2026-W44.csv` | #2 | 2 |

## Never opened

- `wfm/staffing/erlang.py`
- `wfm/scheduler/greedy_v2.py`
- `wfm/scheduler/templates.py`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | #34 |
| git show | #6, #35 |
| git diff | — |
| git status | #71, #78 |
| pytest | #9, #15, #16, #42, #68, #77 |
| run northwind | #20, #43, #46, #49, #69, #71, #77 |
| run contoso | — |
| run fabrikam | — |

## Edits and writes

- #19 `/app/wfm/scheduler/week.py`
- #64 `/app/tests_unit/test_northwind.py`
- #66 `/app/docs/clients/northwind.md`

Bash commands that write files (scripted edits): #12, #13, #14, #15, #20, #21, #26, #27, #29, #31, #32, #33, #37, #38, #39, #42, #43, #45, #46, #49, #52, #53, #56, #59, #60, #69, #70, #71, #72, #73, #76, #77
