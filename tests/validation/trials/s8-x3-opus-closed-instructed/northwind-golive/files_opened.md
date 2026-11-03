# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #1 | 3 |
| `docs/NORTHWIND_SOW.md` | #2 | 3 |
| `docs/CHANGELOG.md` | #2 | 3 |
| `data/northwind/README.txt` | #2 | 1 |
| `configs/defaults.yaml` | #3 | 1 |
| `configs/contoso.yaml` | #3 | 1 |
| `configs/fabrikam.yaml` | #3 | 1 |
| `wfm/ingest/loader.py` | #4 | 4 |
| `wfm/staffing/required.py` | #19 | 1 |
| `wfm/scheduler/greedy.py` | #5 | 1 |
| `wfm/scheduler/greedy_v2.py` | #6 | 1 |
| `wfm/scheduler/templates.py` | #5 | 2 |
| `wfm/evaluate/metrics.py` | #30 | 2 |
| `wfm/cli.py` | #4 | 4 |
| `wfm/config.py` | #4 | 1 |
| `wfm/roster.py` | #4 | 1 |
| `tests_unit/test_staffing.py` | #13 | 1 |
| `tests_unit/test_scheduler.py` | #14 | 1 |
| `data/northwind/export_2026-W44.csv` | #3 | 6 |

## Never opened

- `wfm/staffing/erlang.py`
- `tests_unit/test_config_and_loader.py`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | #1 |
| git show | — |
| git diff | — |
| git status | #40, #42 |
| pytest | #12, #19, #35, #37, #43 |
| run northwind | #21, #30, #31, #38, #40, #41, #42 |
| run contoso | #31 |
| run fabrikam | #31 |

## Edits and writes

- #20 `/app/wfm/scheduler/week.py`
- #22 `/tmp/nwcheck/check.py`
- #32 `/app/wfm/report/reconciliation.py`
- #39 `/app/docs/clients/northwind_handover.md`

Bash commands that write files (scripted edits): #16, #17, #18, #19, #21, #24, #26, #28, #29, #30, #33, #34, #37, #40, #41
