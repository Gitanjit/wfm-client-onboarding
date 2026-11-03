# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #1 | 2 |
| `docs/NORTHWIND_SOW.md` | #9 | 1 |
| `docs/CHANGELOG.md` | #5 | 2 |
| `data/northwind/README.txt` | #10 | 1 |
| `configs/defaults.yaml` | #3 | 1 |
| `configs/contoso.yaml` | #3 | 1 |
| `configs/fabrikam.yaml` | #3 | 1 |
| `wfm/ingest/loader.py` | #6 | 2 |
| `wfm/staffing/required.py` | #6 | 1 |
| `wfm/staffing/erlang.py` | #6 | 2 |
| `wfm/scheduler/greedy.py` | #34 | 1 |
| `wfm/scheduler/greedy_v2.py` | #7 | 4 |
| `wfm/scheduler/templates.py` | #6 | 2 |
| `wfm/evaluate/metrics.py` | #8 | 3 |
| `wfm/cli.py` | #8 | 2 |
| `wfm/config.py` | #6 | 1 |
| `wfm/roster.py` | #6 | 1 |
| `docs/LITWARE_SOW.md` | #2 | 3 |
| `data/litware/README.txt` | #20 | 1 |
| `configs/northwind.yaml` | #3 | 1 |

## Never opened

- `tests_unit/test_staffing.py`
- `tests_unit/test_scheduler.py`
- `tests_unit/test_config_and_loader.py`
- `data/northwind/export_2026-W44.csv`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | #5, #13 |
| git show | — |
| git diff | #4, #34 |
| git status | #1, #44 |
| pytest | #23, #31, #33, #44 |
| run northwind | #11, #23, #27 |
| run contoso | #34 |
| run fabrikam | #34 |

## Edits and writes

- #37 `/app/docs/clients/litware.md`
- #39 `/app/docs/clients/litware.md`

Bash commands that write files (scripted edits): #14, #15, #16, #17, #18, #19, #20, #22, #24, #26, #31, #32, #33, #36
