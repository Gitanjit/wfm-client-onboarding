# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #1 | 2 |
| `docs/NORTHWIND_SOW.md` | #2 | 3 |
| `docs/CHANGELOG.md` | #2 | 2 |
| `data/northwind/README.txt` | #43 | 1 |
| `configs/defaults.yaml` | #3 | 1 |
| `configs/contoso.yaml` | #3 | 1 |
| `configs/fabrikam.yaml` | #3 | 1 |
| `wfm/ingest/loader.py` | #8 | 4 |
| `wfm/staffing/required.py` | #8 | 2 |
| `wfm/staffing/erlang.py` | #8 | 2 |
| `wfm/scheduler/greedy.py` | #9 | 1 |
| `wfm/scheduler/greedy_v2.py` | #10 | 2 |
| `wfm/scheduler/templates.py` | #9 | 2 |
| `wfm/evaluate/metrics.py` | #9 | 3 |
| `wfm/cli.py` | #9 | 4 |
| `wfm/config.py` | #8 | 2 |
| `wfm/roster.py` | #8 | 2 |
| `tests_unit/test_scheduler.py` | #13 | 1 |
| `data/northwind/export_2026-W44.csv` | #4 | 2 |

## Never opened

- `tests_unit/test_staffing.py`
- `tests_unit/test_config_and_loader.py`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | #1 |
| git show | — |
| git diff | #43 |
| git status | #11, #46, #47 |
| pytest | #11, #36, #37, #38, #44, #58 |
| run northwind | #23, #26, #28, #30, #31, #39, #43, #47, #48, #56, #57, #58 |
| run contoso | #11 |
| run fabrikam | — |

## Edits and writes

- #16 `/app/wfm/scheduler/week.py`
- #40 `/app/docs/clients/northwind_handover.md`

Bash commands that write files (scripted edits): #12, #15, #17, #18, #19, #22, #23, #24, #25, #27, #28, #29, #30, #32, #33, #36, #38, #42, #43, #44, #45, #47, #48, #49, #51, #56, #58
