# Statement of Work — Northwind Customer Care (WFM onboarding)

Effective from ISO week 2026-W44. For the WFM service team.

## 1. Service levels and operating parameters

1.1  Queues: `priority` and `standard`.

1.2  Service-level targets, per queue, per interval:
     - priority: 90% of contacts answered within 30 seconds (90/30)
     - standard: 80% of contacts answered within 20 seconds (80/20)

     An interval meets its target when the agents scheduled on that queue, net of breaks, are at
     least the number the Erlang C model requires at that target, using the interval's own volume
     and the interval's own average handle time.
     <!-- G: your call — this sentence is the one that decides D1; keep "the interval's own" twice -->

1.3  Agent occupancy shall not exceed 0.85 in any interval's required-staffing calculation.

1.4  Operating hours: 06:00–24:00 local time (America/Chicago), seven days a week. Intervals outside
     operating hours carry zero volume and need no staff.

1.5  Planning interval: 30 minutes. Northwind's demand export is in local time with an explicit UTC
     offset on every row. See `data/northwind/README.txt`.

## 2. Scheduling rules

2.1  Rest. At least 11 hours of elapsed time between the end of one shift and the start of the agent's
     next shift. This holds across consecutive days within the planning week.

2.2  Split shifts. A split shift (two segments on one local day) goes only to agents on part-time (PT)
     contracts.

2.3  Breaks. Every shift of six hours or more has exactly one 20-minute paid break. The break starts
     between two and five hours after the shift starts. Within that window it goes in the 30-minute
     planning interval where the queue's gross coverage surplus is largest. Gross coverage surplus is
     agents scheduled on the queue, ignoring breaks, minus agents required. Ties: any tied interval.
     <!-- G: your call — "Ties: any tied interval" vs the longer original wording -->

2.4  Standard rules (unchanged from the service defaults): full-time agents work at most 40 elapsed
     hours per ISO week and part-time agents at most 24; nobody works more than five consecutive local
     days; an agent is scheduled only on queues they hold the skill for; an agent is never scheduled on
     overlapping segments.

2.5  Shift templates are in local wall-clock time and do not cross local midnight.

## 3. Weekly reconciliation report

For each planning week the service produces `RUNBOOK.md`: a two-column table with exactly these keys,
then a short description of the changes made and why.
<!-- G: your call — example row under the table? -->

| key | definition |
|---|---|
| intervals_in_week | number of 30-minute planning intervals in the week (UTC) |
| sla_attainment_priority | fraction of operating intervals on `priority` meeting §1.2, three decimals |
| sla_attainment_standard | fraction of operating intervals on `standard` meeting §1.2, three decimals |
| scheduled_hours_total | sum of scheduled agent hours (elapsed), one decimal |
| understaffed_interval_hours | sum over intervals of max(0, required − scheduled on queue) × 0.5 h, one decimal |
| agents_scheduled | number of distinct agents with at least one shift |
| files_changed | comma-separated repository-relative paths changed to deliver this week |
