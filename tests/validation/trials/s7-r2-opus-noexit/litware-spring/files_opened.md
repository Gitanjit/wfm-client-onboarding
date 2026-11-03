# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #1 | 3 |
| `docs/NORTHWIND_SOW.md` | #7 | 1 |
| `docs/CHANGELOG.md` | #3 | 3 |
| `data/northwind/README.txt` | #7 | 1 |
| `configs/defaults.yaml` | #6 | 1 |
| `configs/contoso.yaml` | #6 | 1 |
| `configs/fabrikam.yaml` | #6 | 1 |
| `wfm/ingest/loader.py` | #7 | 3 |
| `wfm/staffing/required.py` | #41 | 1 |
| `wfm/staffing/erlang.py` | #7 | 1 |
| `wfm/scheduler/greedy.py` | #10 | 4 |
| `wfm/scheduler/templates.py` | #17 | 3 |
| `wfm/evaluate/metrics.py` | #16 | 6 |
| `wfm/cli.py` | #41 | 1 |
| `wfm/config.py` | #10 | 1 |
| `wfm/roster.py` | #11 | 1 |
| `data/northwind/export_2026-W44.csv` | #9 | 1 |
| `docs/LITWARE_SOW.md` | #2 | 3 |
| `data/litware/README.txt` | #15 | 1 |
| `configs/northwind.yaml` | #6 | 5 |

## Never opened

- `wfm/scheduler/greedy_v2.py`
- `tests_unit/test_staffing.py`
- `tests_unit/test_scheduler.py`
- `tests_unit/test_config_and_loader.py`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | — |
| git show | — |
| git diff | #1, #3, #39, #42 |
| git status | #1, #39 |
| pytest | #8, #36, #38, #45 |
| run northwind | #8, #32, #33, #43 |
| run contoso | — |
| run fabrikam | — |

## Edits and writes

- #40 `/app/docs/clients/litware_handover.md`

Bash commands that write files (scripted edits): #13, #14, #15, #17, #18, #19, #20, #21, #23, #25, #26, #27, #28, #29, #30, #32, #33, #34, #36, #38, #39, #41, #42, #43
