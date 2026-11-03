# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #1 | 2 |
| `docs/NORTHWIND_SOW.md` | #2 | 2 |
| `docs/CHANGELOG.md` | #2 | 2 |
| `data/northwind/README.txt` | #3 | 1 |
| `configs/defaults.yaml` | #4 | 1 |
| `configs/contoso.yaml` | #4 | 1 |
| `configs/fabrikam.yaml` | #4 | 1 |
| `wfm/ingest/loader.py` | #5 | 2 |
| `wfm/staffing/required.py` | #12 | 1 |
| `wfm/scheduler/greedy.py` | #6 | 1 |
| `wfm/scheduler/greedy_v2.py` | #6 | 2 |
| `wfm/scheduler/templates.py` | #6 | 1 |
| `wfm/evaluate/metrics.py` | #6 | 6 |
| `wfm/cli.py` | #5 | 4 |
| `wfm/config.py` | #5 | 1 |
| `wfm/roster.py` | #5 | 1 |
| `tests_unit/test_staffing.py` | #11 | 1 |
| `data/northwind/export_2026-W44.csv` | #8 | 17 |

## Never opened

- `wfm/staffing/erlang.py`
- `tests_unit/test_scheduler.py`
- `tests_unit/test_config_and_loader.py`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | #1 |
| git show | #8 |
| git diff | #12 |
| git status | #67, #68 |
| pytest | #10, #55, #59, #66, #69 |
| run northwind | #16, #24, #28, #35, #39, #40, #41, #44, #49, #53, #54, #55, #60, #61, #65, #68 |
| run contoso | — |
| run fabrikam | — |

## Edits and writes

- #13 `/app/configs/northwind.yaml`
- #15 `/app/wfm/scheduler/week.py`
- #17 `/tmp/sowcheck/check.py`
- #27 `/app/wfm/scheduler/week.py`
- #62 `/app/wfm/runbook.py`
- #64 `/app/docs/clients/northwind.md`

Bash commands that write files (scripted edits): #12, #16, #19, #22, #24, #25, #30, #31, #32, #33, #34, #35, #39, #40, #41, #44, #45, #46, #47, #48, #49, #52, #53, #54, #57, #59, #60, #61, #63, #66, #67
