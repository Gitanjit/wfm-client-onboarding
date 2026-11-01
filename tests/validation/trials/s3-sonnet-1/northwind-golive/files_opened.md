# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #1 | 3 |
| `docs/NORTHWIND_SOW.md` | #1 | 3 |
| `docs/CHANGELOG.md` | #1 | 3 |
| `data/northwind/README.txt` | #2 | 1 |
| `wfm/ingest/loader.py` | #3 | 4 |
| `wfm/staffing/required.py` | #27 | 2 |
| `wfm/scheduler/greedy.py` | #4 | 1 |
| `wfm/scheduler/greedy_v2.py` | #5 | 9 |
| `wfm/scheduler/templates.py` | #4 | 1 |
| `wfm/evaluate/metrics.py` | #4 | 4 |
| `wfm/cli.py` | #3 | 4 |
| `wfm/config.py` | #3 | 1 |
| `wfm/roster.py` | #3 | 1 |
| `data/northwind/export_2026-W44.csv` | #2 | 4 |

## Never opened

- `configs/defaults.yaml`
- `configs/contoso.yaml`
- `configs/fabrikam.yaml`
- `wfm/staffing/erlang.py`
- `tests_unit/test_staffing.py`
- `tests_unit/test_scheduler.py`
- `tests_unit/test_config_and_loader.py`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | — |
| git show | #10 |
| git diff | #15 |
| git status | #5, #10, #11, #25 |
| pytest | #5, #28, #29 |
| run northwind | #18, #21, #23, #24, #25, #26, #29 |
| run contoso | #10, #26 |
| run fabrikam | #10 |

## Edits and writes

- #13 `/app/wfm/staffing/required.py`
- #17 `/app/wfm/scheduler/greedy_v2.py`

Bash commands that write files (scripted edits): #15, #16, #18, #19, #21, #22, #24, #26, #27, #28, #29
