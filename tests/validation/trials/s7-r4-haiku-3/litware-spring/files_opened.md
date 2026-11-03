# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #2 | 5 |
| `docs/NORTHWIND_SOW.md` | #40 | 1 |
| `docs/CHANGELOG.md` | #5 | 5 |
| `data/northwind/README.txt` | #3 | 1 |
| `configs/defaults.yaml` | #3 | 7 |
| `wfm/ingest/loader.py` | #4 | 4 |
| `wfm/staffing/required.py` | #4 | 3 |
| `wfm/staffing/erlang.py` | #7 | 1 |
| `wfm/scheduler/greedy.py` | #4 | 11 |
| `wfm/scheduler/templates.py` | #6 | 1 |
| `wfm/evaluate/metrics.py` | #4 | 5 |
| `wfm/cli.py` | #5 | 2 |
| `wfm/config.py` | #4 | 8 |
| `wfm/roster.py` | #7 | 1 |
| `docs/LITWARE_SOW.md` | #1 | 3 |
| `data/litware/README.txt` | #3 | 3 |
| `configs/northwind.yaml` | #3 | 1 |

## Never opened

- `configs/contoso.yaml`
- `configs/fabrikam.yaml`
- `wfm/scheduler/greedy_v2.py`
- `tests_unit/test_staffing.py`
- `tests_unit/test_scheduler.py`
- `tests_unit/test_config_and_loader.py`
- `data/northwind/export_2026-W44.csv`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | — |
| git show | — |
| git diff | #4, #5, #14 |
| git status | #1 |
| pytest | #28, #49, #55, #59, #70 |
| run northwind | #32, #70 |
| run contoso | — |
| run fabrikam | — |

## Edits and writes

- #15 `/app/wfm/ingest/loader.py`
- #44 `/app/docs/handover/litware-2027-W11.md`
- #47 `/app/tests_unit/test_litware.py`
- #48 `/app/tests_unit/test_litware.py`

Bash commands that write files (scripted edits): #11, #14, #16, #17, #18, #19, #20, #23, #28, #31, #33, #34, #35, #36, #37, #39, #45, #49, #50, #51, #53, #54, #55, #56, #58, #59, #60, #61, #62, #63, #64, #65
