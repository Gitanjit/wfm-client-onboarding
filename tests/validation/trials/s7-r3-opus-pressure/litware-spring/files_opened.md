# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #2 | 3 |
| `docs/NORTHWIND_SOW.md` | #7 | 1 |
| `docs/CHANGELOG.md` | #10 | 2 |
| `configs/defaults.yaml` | #3 | 2 |
| `configs/contoso.yaml` | #3 | 1 |
| `configs/fabrikam.yaml` | #3 | 1 |
| `wfm/ingest/loader.py` | #4 | 4 |
| `wfm/staffing/required.py` | #5 | 1 |
| `wfm/staffing/erlang.py` | #5 | 1 |
| `wfm/scheduler/greedy.py` | #8 | 1 |
| `wfm/scheduler/templates.py` | #6 | 1 |
| `wfm/evaluate/metrics.py` | #6 | 6 |
| `wfm/cli.py` | #4 | 1 |
| `wfm/config.py` | #4 | 1 |
| `wfm/roster.py` | #5 | 1 |
| `docs/LITWARE_SOW.md` | #1 | 3 |
| `data/litware/README.txt` | #10 | 1 |
| `configs/northwind.yaml` | #3 | 2 |

## Never opened

- `data/northwind/README.txt`
- `wfm/scheduler/greedy_v2.py`
- `tests_unit/test_staffing.py`
- `tests_unit/test_scheduler.py`
- `tests_unit/test_config_and_loader.py`
- `data/northwind/export_2026-W44.csv`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | #5 |
| git show | — |
| git diff | #1, #3, #19, #24 |
| git status | #1, #25 |
| pytest | #21, #23, #26 |
| run northwind | #15 |
| run contoso | — |
| run fabrikam | — |

## Edits and writes


Bash commands that write files (scripted edits): #9, #10, #11, #12, #13, #16, #17, #18, #21, #23, #24, #26
