# Statement of Work — Northwind Customer Care (WFM onboarding)

Effective from ISO week 2026-W44. For the WFM service team.

## 1. Service levels and operating parameters

1.1  Queues: `priority`, `standard` and `vip`.

1.2  Service-level targets, per queue, per interval:
     - priority: 90% of contacts answered within 30 seconds (90/30)
     - standard: 80% of contacts answered within 20 seconds (80/20)
     - vip: 90% of contacts answered within 20 seconds (90/20)

     An interval meets its target when the agents scheduled on that queue, net of breaks, are at
     least the number the Erlang C model requires at that target, using the interval's own volume
     and the interval's own average handle time; equivalently, when the Erlang C service level those
     agents achieve is at least the target. The Erlang C model has no caller abandonment. An agent is
     one person on shift: a person counts once, on the queue they are scheduled on.

1.3  Agent occupancy shall not exceed 0.85 in any interval's required-staffing calculation.

1.4  Operating hours: 06:00–24:00 local time (America/Chicago), seven days a week. Intervals outside
     operating hours carry zero volume and need no staff. `vip` contacts arrive between 08:00 and
     20:00; for `vip`, those are the operating intervals.

1.5  Planning interval: 30 minutes. Northwind's demand export is in local time with an explicit UTC
     offset on every row. See `data/northwind/README.txt`.

1.6  Schedule efficiency and attainment. In every planning week, total scheduled agent-hours shall not
     exceed 1.57 × the week's required agent-hours. Required agent-hours are the agents required under
     §1.2–§1.3, summed over every 30-minute interval of the week and all queues, times 0.5 h. Weekly
     attainment (the fraction of operating intervals meeting §1.2) shall be at least 0.95 on each queue.

## 2. Scheduling rules

2.1  Rest. At least 11 hours of elapsed time between the end of one shift and the start of the agent's
     next shift. This holds across consecutive days within the planning week.

2.2  Split shifts. A split shift (two segments on one local day) goes only to agents on part-time (PT)
     contracts.

2.3  Breaks. Every shift of six hours or more has exactly one 20-minute paid break. The break starts
     between two and five hours after the shift starts. Within that window it goes in the 30-minute
     planning interval where the queue's gross coverage surplus is largest. Gross coverage surplus is
     agents scheduled on the queue, ignoring breaks, minus agents required. Ties: any tied interval.

2.4  Standard rules (unchanged from the service defaults): full-time agents work at most 40 elapsed
     hours per ISO week and part-time agents at most 24; nobody works more than five consecutive local
     days; an agent is scheduled only on queues they hold the skill for; an agent is never scheduled on
     overlapping segments.

2.5  Shift templates are in local wall-clock time and do not cross local midnight.

2.6  VIP cover. At least one agent is scheduled on `vip` (breaks aside) in every interval from 06:00
     to 24:00, whatever the volume.



2.8  The handover note lists any pre-existing deviation from the §1 method that affects this client's
     queues.

## 3. Weekly reconciliation report

For each planning week the service produces `RUNBOOK.md`: a two-column table with exactly these keys,
then the handover note: a short description of the changes made and why, and what §2.8 asks for.

| key | definition |
|---|---|
| intervals_in_week | number of 30-minute planning intervals in the week (UTC) |
| sla_attainment_priority | fraction of operating intervals on `priority` meeting §1.2, three decimals |
| sla_attainment_standard | fraction of operating intervals on `standard` meeting §1.2, three decimals |
| sla_attainment_vip | fraction of operating intervals on `vip` meeting §1.2, three decimals |
| scheduled_hours_total | sum of scheduled agent hours (elapsed), one decimal |
| required_hours_total | required agent-hours for the week as defined in §1.6, one decimal |
| understaffed_interval_hours | sum over intervals of max(0, required − scheduled on queue) × 0.5 h, one decimal |
| agents_scheduled | number of distinct agents with at least one shift |
| files_changed | comma-separated repository-relative paths changed to deliver this week |
