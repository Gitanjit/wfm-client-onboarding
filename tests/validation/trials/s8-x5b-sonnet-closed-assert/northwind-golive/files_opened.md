# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #1 | 3 |
| `docs/NORTHWIND_SOW.md` | #1 | 5 |
| `docs/CHANGELOG.md` | #1 | 3 |
| `data/northwind/README.txt` | #2 | 1 |
| `configs/defaults.yaml` | #2 | 6 |
| `configs/contoso.yaml` | #2 | 1 |
| `configs/fabrikam.yaml` | #2 | 1 |
| `wfm/ingest/loader.py` | #3 | 4 |
| `wfm/staffing/required.py` | #10 | 3 |
| `wfm/scheduler/greedy.py` | #4 | 2 |
| `wfm/scheduler/greedy_v2.py` | #6 | 1 |
| `wfm/scheduler/templates.py` | #4 | 1 |
| `wfm/evaluate/metrics.py` | #4 | 4 |
| `wfm/cli.py` | #3 | 4 |
| `wfm/config.py` | #3 | 5 |
| `wfm/roster.py` | #3 | 1 |
| `tests_unit/test_scheduler.py` | #6 | 1 |
| `tests_unit/test_config_and_loader.py` | #34 | 1 |
| `data/northwind/export_2026-W44.csv` | #26 | 2 |

## Never opened

- `wfm/staffing/erlang.py`
- `tests_unit/test_staffing.py`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | — |
| git show | — |
| git diff | #9, #36 |
| git status | #6, #54, #65, #69 |
| pytest | #6, #32, #33, #35, #36, #37, #67, #69 |
| run northwind | #29, #38, #48, #65, #68, #69 |
| run contoso | — |
| run fabrikam | — |

## Edits and writes

- #11 `/app/wfm/scheduler/weekly.py`

Bash commands that write files (scripted edits): #7, #9, #10, #12, #13, #14, #15, #16, #17, #18, #19, #20, #21, #22, #23, #24, #25, #29, #30, #31, #35, #37, #39, #40, #41, #42, #43, #44, #46, #48, #49, #53, #55, #56, #57, #59, #61, #63, #64, #65, #68, #69
