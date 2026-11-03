# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #2 | 3 |
| `docs/NORTHWIND_SOW.md` | #5 | 1 |
| `docs/CHANGELOG.md` | #42 | 2 |
| `data/northwind/README.txt` | #8 | 1 |
| `configs/defaults.yaml` | #3 | 2 |
| `configs/contoso.yaml` | #3 | 1 |
| `configs/fabrikam.yaml` | #3 | 1 |
| `wfm/ingest/loader.py` | #7 | 6 |
| `wfm/staffing/required.py` | #13 | 1 |
| `wfm/staffing/erlang.py` | #7 | 1 |
| `wfm/scheduler/templates.py` | #7 | 1 |
| `wfm/evaluate/metrics.py` | #11 | 3 |
| `wfm/cli.py` | #20 | 2 |
| `wfm/config.py` | #7 | 1 |
| `wfm/roster.py` | #7 | 1 |
| `docs/LITWARE_SOW.md` | #1 | 5 |
| `data/litware/README.txt` | #42 | 2 |
| `configs/northwind.yaml` | #3 | 2 |

## Never opened

- `wfm/scheduler/greedy.py`
- `wfm/scheduler/greedy_v2.py`
- `tests_unit/test_staffing.py`
- `tests_unit/test_scheduler.py`
- `tests_unit/test_config_and_loader.py`
- `data/northwind/export_2026-W44.csv`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | #2, #12 |
| git show | #13 |
| git diff | #2, #3 |
| git status | #1, #44 |
| pytest | #31, #38, #39, #41, #44 |
| run northwind | #11, #31 |
| run contoso | — |
| run fabrikam | — |

## Edits and writes


Bash commands that write files (scripted edits): #15, #16, #17, #18, #19, #20, #23, #24, #25, #26, #28, #32, #33, #36, #37, #39, #41, #42, #43
