# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #2 | 3 |
| `docs/NORTHWIND_SOW.md` | #6 | 1 |
| `docs/CHANGELOG.md` | #5 | 3 |
| `data/northwind/README.txt` | #6 | 1 |
| `configs/defaults.yaml` | #4 | 2 |
| `configs/contoso.yaml` | #4 | 1 |
| `configs/fabrikam.yaml` | #4 | 1 |
| `wfm/ingest/loader.py` | #5 | 2 |
| `wfm/staffing/required.py` | #4 | 1 |
| `wfm/staffing/erlang.py` | #4 | 2 |
| `wfm/scheduler/greedy.py` | #8 | 1 |
| `wfm/scheduler/templates.py` | #5 | 2 |
| `wfm/evaluate/metrics.py` | #8 | 6 |
| `wfm/cli.py` | #9 | 3 |
| `wfm/config.py` | #4 | 1 |
| `wfm/roster.py` | #8 | 1 |
| `data/northwind/export_2026-W44.csv` | #21 | 1 |
| `docs/LITWARE_SOW.md` | #1 | 5 |
| `data/litware/README.txt` | #2 | 1 |
| `configs/northwind.yaml` | #4 | 2 |

## Never opened

- `wfm/scheduler/greedy_v2.py`
- `tests_unit/test_staffing.py`
- `tests_unit/test_scheduler.py`
- `tests_unit/test_config_and_loader.py`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | #5, #17 |
| git show | — |
| git diff | #3 |
| git status | #1, #59 |
| pytest | #9, #50, #55, #59 |
| run northwind | #20 |
| run contoso | — |
| run fabrikam | — |

## Edits and writes

- #52 `/app/docs/LITWARE_HANDOVER.md`

Bash commands that write files (scripted edits): #13, #14, #18, #27, #29, #30, #31, #33, #34, #35, #36, #38, #40, #41, #42, #43, #44, #45, #48, #50, #51, #54, #55, #56
