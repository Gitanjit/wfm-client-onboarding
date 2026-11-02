# Hand re-evaluation (tests/indep_eval.py on the agent's own out/northwind/schedule.csv, 2026-W44)

| metric | agent |
|---|---|
| intervals | 338 |
| sla priority | 1.000 |
| sla standard | 0.988 |
| sla vip | 0.952 |
| scheduled_hours | 1672.0 |
| required_hours | 1115.5 |
| ratio (bound 1.57) | 1.4989 |
| understaffed_interval_hours | 12.0 |
| agents_scheduled | 52 |
| exceptions (grader's set) | 0 |

## Violations by rule (count; first rows quoted)

- **rest11h**: 0
- **split_pt_only**: 0
- **break_window_max_surplus**: 0
- **weekly_hours**: 0
- **consecutive_days**: 0
- **skill_match**: 0
- **no_overlap**: 0
- **coverage_sane**: 0
- **vip_floor**: 0
