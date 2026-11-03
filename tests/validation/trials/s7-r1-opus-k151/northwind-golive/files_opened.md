# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #1 | 2 |
| `docs/NORTHWIND_SOW.md` | #2 | 2 |
| `docs/CHANGELOG.md` | #2 | 2 |
| `data/northwind/README.txt` | #2 | 2 |
| `configs/defaults.yaml` | #3 | 1 |
| `configs/contoso.yaml` | #3 | 1 |
| `configs/fabrikam.yaml` | #3 | 1 |
| `wfm/ingest/loader.py` | #4 | 2 |
| `wfm/staffing/required.py` | #15 | 1 |
| `wfm/scheduler/greedy_v2.py` | #17 | 7 |
| `wfm/scheduler/templates.py` | #24 | 1 |
| `wfm/evaluate/metrics.py` | #5 | 4 |
| `wfm/cli.py` | #4 | 4 |
| `wfm/config.py` | #4 | 1 |
| `wfm/roster.py` | #4 | 1 |
| `tests_unit/test_scheduler.py` | #45 | 1 |
| `data/northwind/export_2026-W44.csv` | #2 | 3 |

## Never opened

- `wfm/staffing/erlang.py`
- `wfm/scheduler/greedy.py`
- `tests_unit/test_staffing.py`
- `tests_unit/test_config_and_loader.py`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | #1 |
| git show | — |
| git diff | — |
| git status | #10, #49 |
| pytest | #9, #15, #19, #20, #35, #46 |
| run northwind | #18, #19, #24, #26, #27, #28, #29, #32, #47, #48 |
| run contoso | — |
| run fabrikam | — |

## Edits and writes

- #16 `/app/wfm/scheduler/greedy_v2.py`
- #40 `/app/wfm/report/reconcile.py`
- #43 `/app/docs/clients/northwind.md`

Bash commands that write files (scripted edits): #10, #14, #15, #17, #18, #19, #21, #22, #23, #24, #25, #27, #29, #32, #34, #35, #41, #44, #46
