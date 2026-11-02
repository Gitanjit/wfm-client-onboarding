# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #1 | 3 |
| `docs/NORTHWIND_SOW.md` | #1 | 4 |
| `docs/CHANGELOG.md` | #1 | 3 |
| `data/northwind/README.txt` | #2 | 1 |
| `configs/defaults.yaml` | #2 | 2 |
| `configs/contoso.yaml` | #2 | 1 |
| `configs/fabrikam.yaml` | #2 | 1 |
| `wfm/ingest/loader.py` | #12 | 4 |
| `wfm/staffing/required.py` | #13 | 3 |
| `wfm/evaluate/metrics.py` | #17 | 5 |
| `wfm/cli.py` | #5 | 4 |
| `tests_unit/test_scheduler.py` | #50 | 1 |
| `data/northwind/export_2026-W44.csv` | #10 | 3 |

## Never opened

- `wfm/staffing/erlang.py`
- `wfm/scheduler/greedy.py`
- `wfm/scheduler/greedy_v2.py`
- `wfm/scheduler/templates.py`
- `wfm/config.py`
- `wfm/roster.py`
- `tests_unit/test_staffing.py`
- `tests_unit/test_config_and_loader.py`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | — |
| git show | — |
| git diff | #30 |
| git status | #2, #9, #54 |
| pytest | #45, #46, #47, #51, #53, #55 |
| run northwind | #17, #22, #23, #24, #28, #31, #32, #39, #43, #44, #53, #54, #55 |
| run contoso | — |
| run fabrikam | — |

## Edits and writes

- #15 `/app/wfm/scheduler/weekly.py`

Bash commands that write files (scripted edits): #12, #13, #14, #16, #17, #21, #22, #23, #24, #25, #26, #27, #28, #29, #30, #31, #32, #33, #39, #40, #41, #42, #43, #45, #47, #49, #50, #51, #52, #53, #55
