# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #1 | 3 |
| `docs/NORTHWIND_SOW.md` | #2 | 2 |
| `docs/CHANGELOG.md` | #3 | 2 |
| `data/northwind/README.txt` | #2 | 1 |
| `configs/defaults.yaml` | #3 | 1 |
| `configs/contoso.yaml` | #3 | 1 |
| `configs/fabrikam.yaml` | #3 | 1 |
| `wfm/ingest/loader.py` | #4 | 3 |
| `wfm/staffing/required.py` | #5 | 3 |
| `wfm/staffing/erlang.py` | #5 | 2 |
| `wfm/scheduler/greedy.py` | #5 | 1 |
| `wfm/scheduler/greedy_v2.py` | #6 | 1 |
| `wfm/scheduler/templates.py` | #5 | 3 |
| `wfm/evaluate/metrics.py` | #5 | 3 |
| `wfm/cli.py` | #4 | 4 |
| `wfm/config.py` | #4 | 1 |
| `wfm/roster.py` | #5 | 1 |
| `tests_unit/test_staffing.py` | #9 | 1 |
| `tests_unit/test_scheduler.py` | #9 | 1 |
| `data/northwind/export_2026-W44.csv` | #2 | 5 |

## Never opened

- `tests_unit/test_config_and_loader.py`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | #6 |
| git show | — |
| git diff | #12 |
| git status | #26, #43 |
| pytest | #32, #33, #35, #41, #43 |
| run northwind | #14, #15, #21, #22, #23, #25, #26, #31, #36, #42, #43 |
| run contoso | #32, #42 |
| run fabrikam | #32, #42 |

## Edits and writes

- #13 `/app/wfm/scheduler/week_aware.py`
- #39 `/app/docs/clients/northwind_handover.md`

Bash commands that write files (scripted edits): #11, #12, #14, #15, #19, #21, #22, #23, #25, #28, #31, #35, #37, #40, #41, #43
