# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #1 | 2 |
| `docs/NORTHWIND_SOW.md` | #1 | 4 |
| `docs/CHANGELOG.md` | #1 | 2 |
| `data/northwind/README.txt` | #2 | 1 |
| `configs/defaults.yaml` | #2 | 1 |
| `configs/contoso.yaml` | #2 | 1 |
| `configs/fabrikam.yaml` | #2 | 1 |
| `wfm/ingest/loader.py` | #3 | 3 |
| `wfm/staffing/required.py` | #11 | 2 |
| `wfm/scheduler/greedy.py` | #3 | 2 |
| `wfm/scheduler/greedy_v2.py` | #6 | 12 |
| `wfm/scheduler/templates.py` | #3 | 2 |
| `wfm/evaluate/metrics.py` | #3 | 5 |
| `wfm/cli.py` | #3 | 6 |
| `wfm/config.py` | #3 | 1 |
| `wfm/roster.py` | #3 | 2 |
| `tests_unit/test_scheduler.py` | #15 | 2 |
| `tests_unit/test_config_and_loader.py` | #40 | 1 |
| `data/northwind/export_2026-W44.csv` | #7 | 4 |

## Never opened

- `wfm/staffing/erlang.py`
- `tests_unit/test_staffing.py`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | #38 |
| git show | — |
| git diff | #10, #47 |
| git status | #12, #59 |
| pytest | #8, #42, #43, #44, #47, #58 |
| run northwind | #18, #22, #24, #26, #29, #35, #49, #50, #55, #59 |
| run contoso | — |
| run fabrikam | — |

## Edits and writes

- #16 ``

Bash commands that write files (scripted edits): #10, #11, #13, #14, #17, #18, #19, #21, #22, #24, #26, #27, #28, #29, #32, #33, #36, #39, #42, #44, #45, #47, #49, #50, #55, #57, #58
