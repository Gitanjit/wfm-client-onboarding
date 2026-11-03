# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #2 | 4 |
| `docs/NORTHWIND_SOW.md` | #4 | 1 |
| `docs/CHANGELOG.md` | #4 | 3 |
| `data/northwind/README.txt` | #10 | 1 |
| `configs/defaults.yaml` | #3 | 1 |
| `wfm/ingest/loader.py` | #5 | 4 |
| `wfm/staffing/required.py` | #5 | 3 |
| `wfm/staffing/erlang.py` | #5 | 4 |
| `wfm/scheduler/templates.py` | #7 | 1 |
| `wfm/evaluate/metrics.py` | #9 | 2 |
| `wfm/cli.py` | #5 | 5 |
| `wfm/config.py` | #5 | 1 |
| `wfm/roster.py` | #7 | 1 |
| `data/northwind/export_2026-W44.csv` | #10 | 1 |
| `docs/LITWARE_SOW.md` | #1 | 4 |
| `data/litware/README.txt` | #3 | 2 |
| `configs/northwind.yaml` | #3 | 1 |

## Never opened

- `configs/contoso.yaml`
- `configs/fabrikam.yaml`
- `wfm/scheduler/greedy.py`
- `wfm/scheduler/greedy_v2.py`
- `tests_unit/test_staffing.py`
- `tests_unit/test_scheduler.py`
- `tests_unit/test_config_and_loader.py`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | — |
| git show | — |
| git diff | #3, #9, #13 |
| git status | #11, #31 |
| pytest | #26, #28, #29, #30 |
| run northwind | #10, #11, #25 |
| run contoso | #31 |
| run fabrikam | — |

## Edits and writes


Bash commands that write files (scripted edits): #14, #15, #16, #17, #18, #20, #22, #24, #28, #29, #30
