# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #1 | 2 |
| `docs/NORTHWIND_SOW.md` | #1 | 2 |
| `docs/CHANGELOG.md` | #1 | 2 |
| `data/northwind/README.txt` | #2 | 1 |
| `configs/defaults.yaml` | #10 | 2 |
| `wfm/ingest/loader.py` | #8 | 4 |
| `wfm/staffing/required.py` | #11 | 1 |
| `wfm/staffing/erlang.py` | #7 | 2 |
| `wfm/scheduler/greedy_v2.py` | #5 | 2 |
| `wfm/scheduler/templates.py` | #12 | 1 |
| `wfm/evaluate/metrics.py` | #19 | 3 |
| `wfm/cli.py` | #13 | 2 |
| `tests_unit/test_staffing.py` | #7 | 1 |
| `tests_unit/test_scheduler.py` | #43 | 1 |
| `tests_unit/test_config_and_loader.py` | #43 | 1 |
| `data/northwind/export_2026-W44.csv` | #2 | 5 |

## Never opened

- `configs/contoso.yaml`
- `configs/fabrikam.yaml`
- `wfm/scheduler/greedy.py`
- `wfm/config.py`
- `wfm/roster.py`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | #7 |
| git show | — |
| git diff | #11 |
| git status | #5, #6, #40, #61, #62 |
| pytest | #6, #40, #41, #44, #61, #63 |
| run northwind | #13, #17, #19, #21, #24, #25, #27, #28, #57, #59, #63 |
| run contoso | #62 |
| run fabrikam | #62 |

## Edits and writes


Bash commands that write files (scripted edits): #8, #9, #10, #11, #12, #13, #17, #19, #21, #24, #25, #27, #28, #29, #32, #33, #34, #36, #37, #41, #44, #46, #47, #49, #51, #52, #54, #56, #57, #58, #61
