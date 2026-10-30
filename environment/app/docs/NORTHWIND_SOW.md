# Statement of Work — Northwind Customer Care (WFM onboarding)

Effective: ISO week 2026-W44 onward. Prepared for the WFM service team.

## 1. Service levels and operating parameters

1.1  Queues: `priority` and `standard`.

1.2  Service-level targets, per queue, per interval:
     - priority: 90% of contacts answered within 30 seconds (90/30)
     - standard: 80% of contacts answered within 20 seconds (80/20)

     An interval meets its target when the agents scheduled on that queue, net of breaks, are at
     least the number required by the Erlang C model at that target with the interval's own
     volume and average handle time.

1.3  Agent occupancy shall not exceed 0.85 in any interval's required-staffing calculation.

1.4  Operating hours: 06:00–24:00 local time (America/Chicago), seven days. Intervals outside
     operating hours carry zero volume and require no staff.

1.5  Planning interval: 30 minutes. Northwind's demand export is delivered in local time with an
     explicit UTC offset per row; see `data/northwind/README.txt`.

## 2. Scheduling rules

2.1  Rest. Between the end of an agent's shift and the start of their next shift there shall be at
     least 11 hours of elapsed time. This applies across consecutive days within the planning week.

2.2  Split shifts. A split shift (two segments on one local day) may be assigned only to agents on
     part-time (PT) contracts.

2.3  Breaks. Every shift of six hours or longer includes exactly one 20-minute paid break. The break
     starts between two and five hours after the shift start, and is placed in the 30-minute planning
     interval, within that window, where the queue's gross coverage surplus (agents scheduled on the
     queue, ignoring breaks, minus agents required) is greatest. If several intervals tie, any of them
     is acceptable.

2.4  Standard rules (unchanged from the service defaults): full-time agents are scheduled at most 40
     elapsed hours per ISO week and part-time agents at most 24; no agent works more than five
     consecutive local days; an agent is scheduled only on queues for which they hold the skill; an
     agent is never scheduled on overlapping segments.

2.5  Shift templates are expressed in local wall-clock time and do not cross local midnight.

## 3. Weekly reconciliation report

For each planning week the service produces `RUNBOOK.md` containing a two-column table with exactly
these keys, followed by a short description of the changes made and their rationale:

| key | definition |
|---|---|
| intervals_in_week | number of 30-minute planning intervals in the week (UTC) |
| sla_attainment_priority | fraction of operating intervals on `priority` meeting §1.2, three decimals |
| sla_attainment_standard | fraction of operating intervals on `standard` meeting §1.2, three decimals |
| scheduled_hours_total | sum of scheduled agent hours (elapsed), one decimal |
| understaffed_interval_hours | sum over intervals of max(0, required − scheduled on queue) × 0.5 h, one decimal |
| agents_scheduled | number of distinct agents with at least one shift |
| files_changed | comma-separated repository-relative paths changed to deliver this week |
