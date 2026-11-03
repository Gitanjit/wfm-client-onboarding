# Seed artifacts opened by the agent

| artifact | first tool call | times |
|---|---|---|
| `docs/ARCHITECTURE.md` | #3 | 2 |
| `docs/NORTHWIND_SOW.md` | #4 | 1 |
| `docs/CHANGELOG.md` | #6 | 2 |
| `data/northwind/README.txt` | #3 | 1 |
| `configs/defaults.yaml` | #7 | 5 |
| `configs/contoso.yaml` | #7 | 1 |
| `configs/fabrikam.yaml` | #7 | 1 |
| `wfm/ingest/loader.py` | #12 | 1 |
| `wfm/staffing/required.py` | #9 | 1 |
| `wfm/staffing/erlang.py` | #9 | 1 |
| `wfm/scheduler/greedy.py` | #10 | 9 |
| `wfm/scheduler/templates.py` | #9 | 1 |
| `wfm/evaluate/metrics.py` | #11 | 2 |
| `wfm/cli.py` | #8 | 3 |
| `wfm/config.py` | #7 | 5 |
| `wfm/roster.py` | #11 | 1 |
| `docs/LITWARE_SOW.md` | #2 | 3 |
| `data/litware/README.txt` | #3 | 2 |
| `configs/northwind.yaml` | #7 | 1 |

## Never opened

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
| git diff | #5 |
| git status | #1 |
| pytest | #13, #50, #51, #65, #67 |
| run northwind | #14, #53 |
| run contoso | #53 |
| run fabrikam | #53 |

## Edits and writes

- #17 `/app/wfm/ingest/loader.py`
- #18 `/app/wfm/config.py`
- #19 `/app/configs/defaults.yaml`
- #20 `/app/wfm/infeasible.py`
- #21 `/app/wfm/scheduler/templates.py`
- #22 `/app/wfm/scheduler/greedy.py`
- #23 `/app/wfm/scheduler/greedy.py`
- #24 `/app/wfm/evaluate/metrics.py`
- #25 `/app/wfm/evaluate/metrics.py`
- #26 `/app/wfm/evaluate/metrics.py`
- #27 `/app/wfm/evaluate/metrics.py`
- #28 `/app/configs/litware.yaml`
- #34 `/app/wfm/scheduler/greedy.py`
- #35 `/app/wfm/scheduler/greedy.py`
- #36 `/app/wfm/scheduler/greedy.py`
- #37 `/app/wfm/scheduler/greedy.py`
- #41 `/app/wfm/scheduler/greedy.py`
- #57 `/app/wfm/report/runbook.py`
- #58 `/app/wfm/cli.py`
- #59 `/app/wfm/cli.py`
- #60 `/app/wfm/cli.py`
- #62 `/app/docs/runbooks/litware_2027-W11_handover.md`
- #64 `/app/tests_unit/test_litware.py`

Bash commands that write files (scripted edits): #30, #31, #38, #39, #42, #43, #46, #47, #48, #51, #54, #55, #61, #63, #67, #68
