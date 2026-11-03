# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #2 | 1 |
| `docs/NORTHWIND_SOW.md` | #4 | 1 |
| `docs/CHANGELOG.md` | #4 | 1 |
| `data/northwind/README.txt` | #7 | 1 |
| `configs/defaults.yaml` | #5 | 1 |
| `configs/contoso.yaml` | #5 | 1 |
| `configs/fabrikam.yaml` | #5 | 1 |
| `wfm/ingest/loader.py` | #7 | 3 |
| `wfm/staffing/required.py` | #9 | 1 |
| `wfm/staffing/erlang.py` | #5 | 1 |
| `wfm/scheduler/greedy.py` | #9 | 1 |
| `wfm/scheduler/templates.py` | #5 | 1 |
| `wfm/evaluate/metrics.py` | #9 | 4 |
| `wfm/config.py` | #5 | 1 |
| `wfm/roster.py` | #5 | 1 |
| `docs/LITWARE_SOW.md` | #1 | 2 |
| `data/litware/README.txt` | #2 | 2 |
| `configs/northwind.yaml` | #5 | 1 |

## Never opened

- `wfm/scheduler/greedy_v2.py`
- `wfm/cli.py`
- `tests_unit/test_staffing.py`
- `tests_unit/test_scheduler.py`
- `tests_unit/test_config_and_loader.py`
- `data/northwind/export_2026-W44.csv`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | #3 |
| git show | — |
| git diff | #3 |
| git status | #1 |
| pytest | #10 |
| run northwind | #10, #11 |
| run contoso | — |
| run fabrikam | — |

## Edits and writes

- #16 `/app/configs/litware.yaml`

Bash commands that write files (scripted edits): #14, #15, #17, #19, #20, #21, #22
