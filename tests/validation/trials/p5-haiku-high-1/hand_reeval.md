# Hand re-evaluation (tests/indep_eval.py on the agent's own out/northwind/schedule.csv, W44)

| metric | agent | reference (oracle) |
|---|---|---|
| intervals | 338 | 338 |
| sla priority | 1.000 | 0.976 |
| sla standard | 1.000 | 0.996 |
| scheduled_hours | 1328.0 | 1312.0 |
| understaffed_interval_hours | 0.0 | 3.5 |
| agents_scheduled | 40 | 40 |

## Violations by rule (count; first rows quoted)

- **rest11h**: 0
- **split_pt_only**: 0
- **break_window_max_surplus**: 0
- **weekly_hours**: 0
- **consecutive_days**: 0
- **skill_match**: 0
- **no_overlap**: 0
- **coverage_sane**: 0
