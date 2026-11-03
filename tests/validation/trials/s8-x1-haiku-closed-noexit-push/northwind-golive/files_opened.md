# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #1 | 1 |
| `docs/NORTHWIND_SOW.md` | #2 | 1 |
| `docs/CHANGELOG.md` | #3 | 1 |
| `data/northwind/README.txt` | #4 | 1 |
| `configs/defaults.yaml` | #4 | 3 |
| `configs/fabrikam.yaml` | #4 | 1 |
| `wfm/ingest/loader.py` | #5 | 4 |
| `wfm/staffing/required.py` | #6 | 2 |
| `wfm/staffing/erlang.py` | #6 | 1 |
| `wfm/scheduler/greedy.py` | #7 | 9 |
| `wfm/scheduler/greedy_v2.py` | #9 | 1 |
| `wfm/scheduler/templates.py` | #7 | 1 |
| `wfm/evaluate/metrics.py` | #8 | 4 |
| `wfm/cli.py` | #5 | 1 |
| `wfm/config.py` | #5 | 3 |
| `wfm/roster.py` | #7 | 1 |
| `tests_unit/test_scheduler.py` | #15 | 1 |
| `data/northwind/export_2026-W44.csv` | #4 | 3 |

## Never opened

- `configs/contoso.yaml`
- `tests_unit/test_staffing.py`
- `tests_unit/test_config_and_loader.py`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | #1 |
| git show | — |
| git diff | #21, #28, #31 |
| git status | #1, #11, #45, #48 |
| pytest | #11, #15, #23, #24, #25, #26, #27, #29, #30, #42, #43, #48 |
| run northwind | #29, #30, #43, #45 |
| run contoso | #43 |
| run fabrikam | #43 |

## Edits and writes

- #17 `/app/wfm/ingest/loader.py`
- #18 `/app/wfm/ingest/loader.py`
- #19 `/app/wfm/ingest/loader.py`
- #20 `/app/wfm/staffing/required.py`
- #22 `/app/configs/northwind.yaml`
- #47 `/app/out/northwind/RUNBOOK.md`

Bash commands that write files (scripted edits): #21, #23, #25, #27, #28, #29, #30, #34, #35, #40, #41, #42, #43, #48
