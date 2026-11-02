# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #1 | 3 |
| `docs/NORTHWIND_SOW.md` | #2 | 3 |
| `docs/CHANGELOG.md` | #2 | 3 |
| `configs/defaults.yaml` | #3 | 2 |
| `configs/contoso.yaml` | #3 | 1 |
| `configs/fabrikam.yaml` | #3 | 1 |
| `wfm/ingest/loader.py` | #4 | 2 |
| `wfm/staffing/required.py` | #15 | 2 |
| `wfm/scheduler/greedy_v2.py` | #13 | 12 |
| `wfm/evaluate/metrics.py` | #5 | 4 |
| `wfm/cli.py` | #4 | 4 |
| `wfm/config.py` | #4 | 1 |
| `wfm/roster.py` | #4 | 1 |
| `tests_unit/test_scheduler.py` | #12 | 1 |
| `data/northwind/export_2026-W44.csv` | #7 | 11 |

## Never opened

- `data/northwind/README.txt`
- `wfm/staffing/erlang.py`
- `wfm/scheduler/greedy.py`
- `wfm/scheduler/templates.py`
- `tests_unit/test_staffing.py`
- `tests_unit/test_config_and_loader.py`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | #1 |
| git show | — |
| git diff | #45 |
| git status | #43, #48 |
| pytest | #10, #35, #36, #38, #44, #48 |
| run northwind | #17, #25, #29, #30, #34, #39, #41, #42, #43, #46, #47, #48 |
| run contoso | #11, #48 |
| run fabrikam | #11, #48 |

## Edits and writes

- #16 `/app/wfm/scheduler/greedy_v2.py`

Bash commands that write files (scripted edits): #8, #14, #15, #17, #18, #19, #22, #25, #26, #27, #29, #30, #31, #32, #33, #34, #38, #41, #42, #44, #45, #46, #47
