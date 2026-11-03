# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #3 | 2 |
| `docs/NORTHWIND_SOW.md` | #10 | 1 |
| `docs/CHANGELOG.md` | #45 | 1 |
| `data/northwind/README.txt` | #10 | 1 |
| `configs/defaults.yaml` | #4 | 1 |
| `configs/contoso.yaml` | #4 | 1 |
| `configs/fabrikam.yaml` | #4 | 1 |
| `wfm/ingest/loader.py` | #5 | 2 |
| `wfm/scheduler/greedy.py` | #8 | 1 |
| `wfm/scheduler/greedy_v2.py` | #11 | 1 |
| `wfm/scheduler/templates.py` | #4 | 1 |
| `wfm/evaluate/metrics.py` | #8 | 4 |
| `wfm/cli.py` | #45 | 1 |
| `wfm/config.py` | #4 | 1 |
| `wfm/roster.py` | #4 | 1 |
| `docs/LITWARE_SOW.md` | #1 | 3 |
| `data/litware/README.txt` | #12 | 1 |
| `configs/northwind.yaml` | #4 | 1 |

## Never opened

- `wfm/staffing/required.py`
- `wfm/staffing/erlang.py`
- `tests_unit/test_staffing.py`
- `tests_unit/test_scheduler.py`
- `tests_unit/test_config_and_loader.py`
- `data/northwind/export_2026-W44.csv`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | — |
| git show | #11 |
| git diff | #2, #19 |
| git status | #1, #47 |
| pytest | #28, #38, #40, #46 |
| run northwind | #19, #20, #46 |
| run contoso | #46 |
| run fabrikam | #46 |

## Edits and writes

- #41 `/app/docs/clients/litware.md`

Bash commands that write files (scripted edits): #12, #13, #14, #15, #16, #17, #26, #32, #35, #36, #38, #40, #43, #45
