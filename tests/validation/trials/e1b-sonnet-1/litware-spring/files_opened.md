# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #2 | 4 |
| `docs/NORTHWIND_SOW.md` | #5 | 2 |
| `docs/CHANGELOG.md` | #3 | 3 |
| `data/northwind/README.txt` | #6 | 1 |
| `configs/defaults.yaml` | #3 | 2 |
| `configs/fabrikam.yaml` | #3 | 1 |
| `wfm/ingest/loader.py` | #4 | 5 |
| `wfm/staffing/required.py` | #4 | 2 |
| `wfm/staffing/erlang.py` | #4 | 1 |
| `wfm/scheduler/greedy.py` | #8 | 2 |
| `wfm/scheduler/templates.py` | #4 | 1 |
| `wfm/evaluate/metrics.py` | #8 | 4 |
| `wfm/cli.py` | #5 | 2 |
| `wfm/config.py` | #4 | 1 |
| `wfm/roster.py` | #4 | 1 |
| `docs/LITWARE_SOW.md` | #1 | 5 |
| `data/litware/README.txt` | #3 | 1 |
| `configs/northwind.yaml` | #3 | 1 |

## Never opened

- `configs/contoso.yaml`
- `wfm/scheduler/greedy_v2.py`
- `tests_unit/test_staffing.py`
- `tests_unit/test_scheduler.py`
- `tests_unit/test_config_and_loader.py`
- `data/northwind/export_2026-W44.csv`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | — |
| git show | — |
| git diff | #3, #9, #14, #27 |
| git status | #39 |
| pytest | #9, #29, #30, #31, #37, #38 |
| run northwind | — |
| run contoso | — |
| run fabrikam | — |

## Edits and writes


Bash commands that write files (scripted edits): #13, #14, #15, #16, #17, #19, #21, #22, #23, #25, #29, #30, #31, #34, #36, #37, #38
