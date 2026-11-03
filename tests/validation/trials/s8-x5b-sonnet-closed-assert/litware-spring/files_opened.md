# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #2 | 3 |
| `docs/NORTHWIND_SOW.md` | #10 | 2 |
| `docs/CHANGELOG.md` | #3 | 3 |
| `data/northwind/README.txt` | #8 | 1 |
| `configs/defaults.yaml` | #3 | 3 |
| `configs/contoso.yaml` | #12 | 1 |
| `configs/fabrikam.yaml` | #12 | 1 |
| `wfm/ingest/loader.py` | #4 | 3 |
| `wfm/staffing/required.py` | #4 | 3 |
| `wfm/staffing/erlang.py` | #4 | 2 |
| `wfm/scheduler/greedy.py` | #7 | 2 |
| `wfm/scheduler/templates.py` | #7 | 1 |
| `wfm/evaluate/metrics.py` | #7 | 3 |
| `wfm/cli.py` | #4 | 1 |
| `wfm/config.py` | #4 | 4 |
| `wfm/roster.py` | #5 | 1 |
| `docs/LITWARE_SOW.md` | #1 | 5 |
| `data/litware/README.txt` | #3 | 1 |
| `configs/northwind.yaml` | #3 | 1 |

## Never opened

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
| git diff | #8, #20, #24 |
| git status | #1, #43 |
| pytest | #8, #31, #41, #42 |
| run northwind | #13, #34, #35 |
| run contoso | #11 |
| run fabrikam | — |

## Edits and writes

- #19 `/app/wfm/ingest/loader.py`

Bash commands that write files (scripted edits): #11, #20, #21, #22, #25, #26, #31, #34, #41, #42
