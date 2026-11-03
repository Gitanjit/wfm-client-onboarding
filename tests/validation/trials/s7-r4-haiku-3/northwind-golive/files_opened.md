# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #1 | 4 |
| `docs/NORTHWIND_SOW.md` | #2 | 1 |
| `docs/CHANGELOG.md` | #3 | 4 |
| `data/northwind/README.txt` | #4 | 1 |
| `configs/defaults.yaml` | #4 | 5 |
| `wfm/ingest/loader.py` | #6 | 4 |
| `wfm/staffing/required.py` | #6 | 3 |
| `wfm/staffing/erlang.py` | #6 | 1 |
| `wfm/scheduler/greedy.py` | #7 | 15 |
| `wfm/scheduler/greedy_v2.py` | #8 | 1 |
| `wfm/scheduler/templates.py` | #7 | 1 |
| `wfm/evaluate/metrics.py` | #8 | 3 |
| `wfm/cli.py` | #5 | 4 |
| `wfm/config.py` | #5 | 5 |
| `wfm/roster.py` | #7 | 1 |
| `data/northwind/export_2026-W44.csv` | #4 | 5 |

## Never opened

- `configs/contoso.yaml`
- `configs/fabrikam.yaml`
- `tests_unit/test_staffing.py`
- `tests_unit/test_scheduler.py`
- `tests_unit/test_config_and_loader.py`

## Behaviours (Bash commands)

| behaviour | tool calls |
|---|---|
| git log | #1 |
| git show | — |
| git diff | — |
| git status | #1 |
| pytest | #9, #11, #55, #57, #58, #59, #60, #65, #72, #85 |
| run northwind | #29, #30, #35, #40, #44, #45, #46, #47, #48, #49, #51, #52, #66, #70, #78, #81 |
| run contoso | — |
| run fabrikam | — |

## Edits and writes

- #13 `/app/configs/defaults.yaml`
- #14 `/app/wfm/config.py`
- #15 `/app/wfm/ingest/loader.py`
- #16 `/app/wfm/ingest/loader.py`
- #17 `/app/wfm/ingest/loader.py`
- #18 `/app/wfm/staffing/required.py`
- #19 `/app/wfm/scheduler/greedy.py`
- #20 `/app/wfm/scheduler/greedy.py`
- #21 `/app/wfm/scheduler/greedy.py`
- #22 `/app/wfm/scheduler/greedy.py`
- #23 `/app/wfm/scheduler/greedy.py`
- #24 `/app/wfm/evaluate/metrics.py`
- #25 `/app/wfm/evaluate/metrics.py`
- #26 `/app/wfm/evaluate/metrics.py`
- #27 `/app/wfm/evaluate/metrics.py`
- #28 `/app/configs/northwind.yaml`
- #32 `/app/wfm/scheduler/greedy.py`
- #33 `/app/wfm/scheduler/greedy.py`
- #34 `/app/wfm/scheduler/greedy.py`
- #39 `/app/wfm/scheduler/greedy.py`
- #62 `/app/wfm/sow.py`
- #64 `/app/tests_unit/test_northwind.py`
- #67 `/app/docs/handover/northwind-2026-W44.md`

Bash commands that write files (scripted edits): #30, #31, #35, #36, #37, #40, #44, #45, #46, #48, #49, #50, #51, #52, #53, #54, #57, #58, #59, #60, #63, #65, #71, #77, #81, #86
