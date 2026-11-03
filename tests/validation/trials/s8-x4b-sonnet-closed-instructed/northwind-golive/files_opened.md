# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #1 | 3 |
| `docs/NORTHWIND_SOW.md` | #2 | 3 |
| `docs/CHANGELOG.md` | #3 | 2 |
| `data/northwind/README.txt` | #4 | 1 |
| `configs/defaults.yaml` | #4 | 1 |
| `configs/contoso.yaml` | #4 | 1 |
| `configs/fabrikam.yaml` | #4 | 1 |
| `wfm/ingest/loader.py` | #5 | 3 |
| `wfm/staffing/required.py` | #13 | 1 |
| `wfm/scheduler/greedy.py` | #6 | 1 |
| `wfm/scheduler/greedy_v2.py` | #6 | 2 |
| `wfm/scheduler/templates.py` | #6 | 1 |
| `wfm/evaluate/metrics.py` | #6 | 2 |
| `wfm/cli.py` | #5 | 4 |
| `wfm/config.py` | #5 | 1 |
| `wfm/roster.py` | #5 | 1 |
| `tests_unit/test_scheduler.py` | #12 | 1 |
| `data/northwind/export_2026-W44.csv` | #7 | 4 |

## Never opened

- `wfm/staffing/erlang.py`
- `tests_unit/test_staffing.py`
- `tests_unit/test_config_and_loader.py`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | #1 |
| git show | — |
| git diff | #53, #61 |
| git status | #9, #11, #62 |
| pytest | #8, #10, #51, #52, #54, #59, #60, #63 |
| run northwind | #18, #21, #22, #23, #28, #30, #31, #34, #36, #41, #43, #44, #46, #50, #55, #62, #63 |
| run contoso | #10 |
| run fabrikam | — |

## Edits and writes

- #15 `/app/configs/northwind.yaml`
- #16 `/app/wfm/scheduler/weekly.py`
- #17 `/app/wfm/evaluate/sow.py`
- #35 `/app/wfm/report/runbook.py`

Bash commands that write files (scripted edits): #10, #13, #18, #21, #22, #24, #25, #27, #29, #30, #31, #32, #33, #34, #36, #40, #41, #42, #45, #46, #47, #48, #49, #53, #54, #57, #58, #59, #60, #61, #62
