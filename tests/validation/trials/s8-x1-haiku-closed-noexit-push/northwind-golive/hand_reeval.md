# Hand re-evaluation (tests/indep_eval.py on the agent's own out/northwind/schedule.csv, 2026-W44)

| metric | agent |
|---|---|
| intervals | 338 |
| sla priority | 0.968 |
| sla standard | 0.964 |
| sla vip | 0.685 |
| scheduled_hours | 1638.0 |
| required_hours | 1115.5 |
| ratio (bound 1.57) | 1.4684 |
| understaffed_interval_hours | 85.0 |
| agents_scheduled | 51 |
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
- **vip_floor**: 72
  - vip 2026-10-31T11:00Z: 0 < 1
  - vip 2026-10-31T11:30Z: 0 < 1
  - vip 2026-10-31T12:00Z: 0 < 1
  - vip 2026-10-31T12:30Z: 0 < 1
  - vip 2026-10-31T13:00Z: 0 < 1
  - vip 2026-10-31T13:30Z: 0 < 1
