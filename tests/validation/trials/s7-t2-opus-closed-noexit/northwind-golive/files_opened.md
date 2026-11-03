# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #1 | 2 |
| `docs/NORTHWIND_SOW.md` | #2 | 5 |
| `docs/CHANGELOG.md` | #2 | 3 |
| `configs/defaults.yaml` | #4 | 1 |
| `configs/contoso.yaml` | #4 | 1 |
| `configs/fabrikam.yaml` | #4 | 1 |
| `wfm/ingest/loader.py` | #5 | 4 |
| `wfm/staffing/required.py` | #5 | 2 |
| `wfm/staffing/erlang.py` | #5 | 3 |
| `wfm/scheduler/greedy.py` | #6 | 1 |
| `wfm/scheduler/greedy_v2.py` | #7 | 1 |
| `wfm/scheduler/templates.py` | #6 | 1 |
| `wfm/evaluate/metrics.py` | #6 | 3 |
| `wfm/cli.py` | #7 | 3 |
| `wfm/config.py` | #5 | 1 |
| `wfm/roster.py` | #5 | 1 |
| `tests_unit/test_scheduler.py` | #18 | 1 |
| `data/northwind/export_2026-W44.csv` | #21 | 10 |

## Never opened

- `data/northwind/README.txt`
- `tests_unit/test_staffing.py`
- `tests_unit/test_config_and_loader.py`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | #1, #35 |
| git show | — |
| git diff | — |
| git status | #51, #55 |
| pytest | #11, #16, #42, #46, #47, #50, #55 |
| run northwind | #20, #24, #25, #28, #37, #40, #47, #48, #51, #52, #55 |
| run contoso | — |
| run fabrikam | — |

## Edits and writes

- #19 `/app/wfm/scheduler/week.py`
- #54 `/app/out/northwind/RUNBOOK.md`

Bash commands that write files (scripted edits): #15, #16, #17, #20, #21, #24, #25, #28, #29, #32, #34, #35, #37, #40, #42, #44, #47, #49, #50, #52, #53
