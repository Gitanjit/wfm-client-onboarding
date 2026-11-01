# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #2 | 3 |
| `docs/NORTHWIND_SOW.md` | #8 | 1 |
| `docs/CHANGELOG.md` | #3 | 3 |
| `data/northwind/README.txt` | #3 | 1 |
| `configs/defaults.yaml` | #3 | 1 |
| `configs/contoso.yaml` | #9 | 1 |
| `configs/fabrikam.yaml` | #3 | 1 |
| `wfm/ingest/loader.py` | #5 | 3 |
| `wfm/staffing/required.py` | #5 | 4 |
| `wfm/staffing/erlang.py` | #5 | 1 |
| `wfm/scheduler/greedy.py` | #7 | 1 |
| `wfm/scheduler/greedy_v2.py` | #6 | 11 |
| `wfm/scheduler/templates.py` | #5 | 3 |
| `wfm/evaluate/metrics.py` | #7 | 4 |
| `wfm/cli.py` | #5 | 1 |
| `wfm/config.py` | #5 | 1 |
| `wfm/roster.py` | #5 | 1 |
| `docs/LITWARE_SOW.md` | #1 | 4 |
| `data/litware/README.txt` | #3 | 1 |
| `configs/northwind.yaml` | #3 | 1 |

## Never opened

- `tests_unit/test_staffing.py`
- `tests_unit/test_scheduler.py`
- `tests_unit/test_config_and_loader.py`
- `data/northwind/export_2026-W44.csv`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | #4 |
| git show | — |
| git diff | #4, #42 |
| git status | #1, #8, #9, #49 |
| pytest | #39, #40, #41, #49, #51 |
| run northwind | #49 |
| run contoso | — |
| run fabrikam | — |

## Edits and writes


Bash commands that write files (scripted edits): #10, #12, #14, #15, #17, #18, #19, #20, #21, #22, #24, #26, #28, #29, #32, #33, #34, #38, #39, #41, #42, #44, #51
