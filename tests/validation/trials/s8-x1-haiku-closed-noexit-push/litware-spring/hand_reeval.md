# Hand re-evaluation (tests/indep_eval.py on the agent's own out/litware/schedule.csv, 2027-W11)

| metric | agent |
|---|---|
| intervals | 504 |
| sla priority | 0.000 |
| sla standard | 0.000 |
| sla email | 0.000 |
| scheduled_hours | 744.0 |
| required_hours | 527.0 |
| ratio (bound 1.45) | 1.4118 |
| understaffed_interval_hours | 512.7 |
| agents_scheduled | 24 |
| exceptions (grader's set) | 42 |

## Violations by rule (count; first rows quoted)

- **rest11h**: 0
- **split_pt_only**: 0
- **break_window_max_surplus**: 100
  - LW-001 2027-03-08: break slot not inside the shift's window
  - LW-001 2027-03-09: break slot not inside the shift's window
  - LW-001 2027-03-11: break slot not inside the shift's window
  - LW-002 2027-03-09: break slot not inside the shift's window
  - LW-002 2027-03-10: break slot not inside the shift's window
  - LW-003 2027-03-08: break slot not inside the shift's window
- **weekly_hours**: 0
- **consecutive_days**: 0
- **skill_match**: 0
- **no_overlap**: 0
- **coverage_sane**: 207
  - row 2: segment 2027-03-08T07:00Z-2027-03-08T13:00Z off the week grid
  - row 2: break 2027-03-08T11:00Z not on the grid inside its segment
  - row 3: segment 2027-03-08T07:00Z-2027-03-08T13:00Z off the week grid
  - row 3: break 2027-03-08T11:00Z not on the grid inside its segment
  - row 4: segment 2027-03-08T07:00Z-2027-03-08T13:00Z off the week grid
  - row 4: break 2027-03-08T11:20Z not on the grid inside its segment
- **priority_floor**: 294
  - priority 2027-03-15T07:00Z: 0 < 2
  - priority 2027-03-15T07:20Z: 0 < 2
  - priority 2027-03-15T07:40Z: 0 < 2
  - priority 2027-03-15T08:00Z: 0 < 2
  - priority 2027-03-15T08:20Z: 0 < 2
  - priority 2027-03-15T08:40Z: 0 < 2
- **email_earliest**: 0
