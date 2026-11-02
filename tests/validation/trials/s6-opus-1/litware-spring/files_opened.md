# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #2 | 3 |
| `docs/NORTHWIND_SOW.md` | #4 | 1 |
| `docs/CHANGELOG.md` | #3 | 3 |
| `data/northwind/README.txt` | #4 | 1 |
| `configs/defaults.yaml` | #2 | 1 |
| `configs/contoso.yaml` | #2 | 1 |
| `configs/fabrikam.yaml` | #2 | 1 |
| `wfm/ingest/loader.py` | #6 | 3 |
| `wfm/staffing/required.py` | #5 | 1 |
| `wfm/staffing/erlang.py` | #5 | 1 |
| `wfm/scheduler/greedy.py` | #9 | 1 |
| `wfm/scheduler/greedy_v2.py` | #8 | 5 |
| `wfm/scheduler/templates.py` | #5 | 5 |
| `wfm/evaluate/metrics.py` | #6 | 4 |
| `wfm/cli.py` | #6 | 4 |
| `wfm/config.py` | #5 | 1 |
| `wfm/roster.py` | #5 | 1 |
| `docs/LITWARE_SOW.md` | #1 | 1 |
| `configs/northwind.yaml` | #2 | 12 |

## Never opened

- `tests_unit/test_staffing.py`
- `tests_unit/test_scheduler.py`
- `tests_unit/test_config_and_loader.py`
- `data/northwind/export_2026-W44.csv`
- `data/litware/README.txt`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | #4 |
| git show | — |
| git diff | #3, #36, #46 |
| git status | #1, #65 |
| pytest | #10, #40, #42, #44, #65 |
| run northwind | #10, #18, #19, #35, #53, #54, #59, #63 |
| run contoso | #65, #66 |
| run fabrikam | #65, #66 |

## Edits and writes

- #14 `/app/configs/litware.yaml`
- #29 `/app/wfm/report/weekly.py`
- #39 `/app/tests_unit/test_litware.py`
- #48 `/app/docs/clients/litware-handover.md`
- #56 `/app/docs/clients/litware.md`

Bash commands that write files (scripted edits): #13, #15, #17, #18, #19, #24, #26, #27, #30, #31, #34, #35, #37, #38, #42, #44, #53, #55, #61, #63, #64, #65, #66
