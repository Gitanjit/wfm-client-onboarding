# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #1 | 1 |
| `docs/NORTHWIND_SOW.md` | #2 | 2 |
| `docs/CHANGELOG.md` | #2 | 3 |
| `data/northwind/README.txt` | #2 | 2 |
| `configs/defaults.yaml` | #3 | 1 |
| `configs/contoso.yaml` | #3 | 1 |
| `configs/fabrikam.yaml` | #3 | 1 |
| `wfm/ingest/loader.py` | #4 | 3 |
| `wfm/staffing/required.py` | #13 | 2 |
| `wfm/staffing/erlang.py` | #13 | 1 |
| `wfm/scheduler/greedy.py` | #15 | 6 |
| `wfm/scheduler/templates.py` | #7 | 5 |
| `wfm/evaluate/metrics.py` | #5 | 4 |
| `wfm/cli.py` | #4 | 3 |
| `wfm/config.py` | #4 | 1 |
| `wfm/roster.py` | #4 | 1 |
| `data/northwind/export_2026-W44.csv` | #7 | 1 |

## Never opened

- `wfm/scheduler/greedy_v2.py`
- `tests_unit/test_staffing.py`
- `tests_unit/test_scheduler.py`
- `tests_unit/test_config_and_loader.py`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | #1, #7 |
| git show | — |
| git diff | — |
| git status | #53 |
| pytest | #8, #47, #48, #50, #53 |
| run northwind | #16, #22, #30, #38, #39, #44, #45, #46, #51, #53, #54 |
| run contoso | #9 |
| run fabrikam | — |

## Edits and writes

- #29 `/app/wfm/scheduler/improve.py`
- #52 `/app/docs/clients/northwind_handover.md`

Bash commands that write files (scripted edits): #12, #13, #14, #15, #16, #17, #19, #22, #23, #25, #26, #27, #30, #32, #35, #37, #38, #39, #41, #42, #43, #46, #47, #49, #50, #53, #54
