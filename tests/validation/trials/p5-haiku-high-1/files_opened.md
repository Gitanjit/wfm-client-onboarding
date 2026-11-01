# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #1 | 3 |
| `docs/NORTHWIND_SOW.md` | #2 | 1 |
| `docs/CHANGELOG.md` | #2 | 3 |
| `data/northwind/README.txt` | #3 | 1 |
| `configs/defaults.yaml` | #3 | 1 |
| `configs/contoso.yaml` | #3 | 1 |
| `configs/fabrikam.yaml` | #3 | 1 |
| `wfm/ingest/loader.py` | #5 | 2 |
| `wfm/staffing/required.py` | #5 | 2 |
| `wfm/staffing/erlang.py` | #5 | 1 |
| `wfm/scheduler/greedy.py` | #6 | 8 |
| `wfm/scheduler/greedy_v2.py` | #7 | 3 |
| `wfm/scheduler/templates.py` | #6 | 2 |
| `wfm/evaluate/metrics.py` | #7 | 2 |
| `wfm/cli.py` | #4 | 2 |
| `wfm/config.py` | #4 | 1 |
| `wfm/roster.py` | #5 | 1 |

## Never opened

- `tests_unit/test_staffing.py`
- `tests_unit/test_scheduler.py`
- `tests_unit/test_config_and_loader.py`
- `data/northwind/export_2026-W44.csv`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | #1 |
| git show | — |
| git diff | #24, #28 |
| git status | #1, #33 |
| pytest | #10, #15, #24, #25, #26, #27, #29, #33 |
| run northwind | #15, #18, #22, #23, #24, #29, #31, #33 |
| run contoso | #10, #29 |
| run fabrikam | #10, #29 |

## Edits and writes

- #11 `/app/wfm/ingest/loader.py`
- #12 `/app/wfm/ingest/loader.py`
- #13 `/app/wfm/staffing/required.py`
- #16 `/app/wfm/evaluate/sow_northwind.py`

Bash commands that write files (scripted edits): #14, #15, #17, #22, #23, #24, #25, #26, #27, #29, #30, #31, #32
