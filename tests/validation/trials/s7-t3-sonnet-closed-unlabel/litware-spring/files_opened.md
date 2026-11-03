# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #2 | 4 |
| `docs/NORTHWIND_SOW.md` | #4 | 1 |
| `docs/CHANGELOG.md` | #3 | 3 |
| `data/northwind/README.txt` | #9 | 1 |
| `configs/defaults.yaml` | #4 | 1 |
| `configs/fabrikam.yaml` | #4 | 1 |
| `wfm/ingest/loader.py` | #6 | 3 |
| `wfm/staffing/required.py` | #8 | 3 |
| `wfm/staffing/erlang.py` | #6 | 1 |
| `wfm/scheduler/greedy.py` | #7 | 4 |
| `wfm/scheduler/greedy_v2.py` | #11 | 1 |
| `wfm/scheduler/templates.py` | #6 | 3 |
| `wfm/evaluate/metrics.py` | #8 | 5 |
| `wfm/cli.py` | #50 | 1 |
| `wfm/config.py` | #6 | 1 |
| `wfm/roster.py` | #6 | 1 |
| `docs/LITWARE_SOW.md` | #1 | 5 |
| `data/litware/README.txt` | #3 | 1 |
| `configs/northwind.yaml` | #4 | 3 |

## Never opened

- `configs/contoso.yaml`
- `tests_unit/test_staffing.py`
- `tests_unit/test_scheduler.py`
- `tests_unit/test_config_and_loader.py`
- `data/northwind/export_2026-W44.csv`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | — |
| git show | — |
| git diff | #3, #5, #17, #19, #23, #40 |
| git status | #1, #13, #14, #49, #53 |
| pytest | #40, #41, #43, #44, #53 |
| run northwind | #26, #46, #53 |
| run contoso | #38 |
| run fabrikam | #38 |

## Edits and writes

- #36 `/app/docs/clients/litware.md`

Bash commands that write files (scripted edits): #10, #13, #18, #19, #20, #21, #23, #24, #25, #29, #30, #37, #38, #39, #40, #41, #43, #44, #47, #50, #53
