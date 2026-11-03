# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #2 | 2 |
| `docs/NORTHWIND_SOW.md` | #8 | 2 |
| `docs/CHANGELOG.md` | #4 | 2 |
| `data/northwind/README.txt` | #11 | 1 |
| `configs/defaults.yaml` | #3 | 2 |
| `configs/contoso.yaml` | #26 | 1 |
| `configs/fabrikam.yaml` | #26 | 1 |
| `wfm/ingest/loader.py` | #5 | 2 |
| `wfm/staffing/required.py` | #5 | 1 |
| `wfm/staffing/erlang.py` | #5 | 1 |
| `wfm/scheduler/templates.py` | #5 | 1 |
| `wfm/evaluate/metrics.py` | #6 | 2 |
| `wfm/cli.py` | #22 | 1 |
| `wfm/config.py` | #5 | 1 |
| `docs/LITWARE_SOW.md` | #1 | 3 |
| `data/litware/README.txt` | #2 | 1 |
| `configs/northwind.yaml` | #3 | 2 |

## Never opened

- `wfm/scheduler/greedy.py`
- `wfm/scheduler/greedy_v2.py`
- `wfm/roster.py`
- `tests_unit/test_staffing.py`
- `tests_unit/test_scheduler.py`
- `tests_unit/test_config_and_loader.py`
- `data/northwind/export_2026-W44.csv`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | #6 |
| git show | — |
| git diff | #1, #3, #4, #11 |
| git status | #1, #11 |
| pytest | #10, #32, #33, #34, #38 |
| run northwind | #10, #28, #38 |
| run contoso | — |
| run fabrikam | — |

## Edits and writes

- #36 `/app/docs/clients/litware.md`

Bash commands that write files (scripted edits): #12, #14, #15, #16, #17, #18, #19, #20, #22, #23, #25, #30, #32, #34, #35, #38
