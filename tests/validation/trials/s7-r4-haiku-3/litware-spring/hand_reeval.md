# Hand re-evaluation (tests/indep_eval.py on the agent's own out/litware/schedule.csv, 2027-W11)

| metric | agent |
|---|---|
| intervals | 504 |
| sla priority | 0.959 |
| sla standard | 0.973 |
| sla email | 0.990 |
| scheduled_hours | 736.0 |
| required_hours | 527.0 |
| ratio (bound 1.45) | 1.3966 |
| understaffed_interval_hours | 10.3 |
| agents_scheduled | 24 |
| exceptions (grader's set) | 42 |

## Violations by rule (count; first rows quoted)

- **rest11h**: 0
- **split_pt_only**: 0
- **break_window_max_surplus**: 0
- **weekly_hours**: 0
- **consecutive_days**: 0
- **skill_match**: 0
- **no_overlap**: 0
- **coverage_sane**: 0
- **priority_floor**: 0
- **email_earliest**: 0
