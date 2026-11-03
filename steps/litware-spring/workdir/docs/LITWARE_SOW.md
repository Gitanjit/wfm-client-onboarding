# Statement of Work — Litware Support (WFM onboarding)

Effective from ISO week 2027-W11. For the WFM service team.

## 1. Service levels and operating parameters

1.1  Queues: `priority`, `standard` and `email`.

1.2  Service-level targets, per queue, per interval:
     - priority: 90% of contacts answered within 30 seconds (90/30)
     - standard: 80% of contacts answered within 30 seconds (80/30)
     - email: 80% of contacts answered within 300 seconds (80/300)

     An interval meets its target when the agents scheduled on that queue, net of breaks, are at
     least the number the Erlang C model requires at that target, using the interval's own volume
     and the interval's own average handle time; equivalently, when the Erlang C service level those
     agents achieve is at least the target. The Erlang C model has no caller abandonment. An agent is
     one person on shift: a person counts once, on the queue they are scheduled on.

1.3  Agent occupancy shall not exceed 0.85 in any interval's required-staffing calculation.

1.4  Operating hours: 07:00–21:00 local time (Europe/London), seven days a week. `email` contacts
     arrive between 07:00 and 19:00. Intervals outside operating hours carry zero volume and need no
     staff.

1.5  Planning interval: 20 minutes. Litware's demand export is in local time and stamps each row with
     the end of its interval. See `data/litware/README.txt`.

1.6  Schedule efficiency and attainment. In every planning week, total scheduled agent-hours shall not
     exceed 1.45 × the week's required agent-hours. Required agent-hours are the agents required under
     §1.2–§1.3, summed over every 20-minute interval of the week and all three queues, times 1/3 h.
     Weekly attainment (the fraction of operating intervals meeting §1.2, leaving out intervals
     reported under §2.6) shall be at least 0.95 on each queue.

1.7  Audit. Litware measures attainment on its own platform under the §1.2 definition and compares it
     with the figures the service reports each week (`eval.json`, the §3 report). A reported weekly figure
     more than 0.03 away from Litware's on any queue is a reporting defect.

## 2. Scheduling rules

2.1  Rest. At least 11 hours of elapsed time between the end of one shift and the start of the agent's
     next shift. This holds across consecutive days within the planning week.

2.2  Split shifts. A split shift (two segments on one local day) goes only to agents on part-time (PT)
     contracts.

2.3  Breaks. Every shift of six hours or more has exactly one 20-minute paid break. The break starts
     between two and five hours after the shift starts. Within that window it goes in the 20-minute
     planning interval where the queue's gross coverage surplus is largest. Gross coverage surplus is
     agents scheduled on the queue, ignoring breaks, minus agents required. Ties: any tied interval.

2.4  Priority cover. At least two agents are scheduled on `priority` (breaks aside) in every operating
     interval, whatever the volume.

2.5  Email start. No agent is scheduled on `email` before 09:00 local time.

2.6  Infeasible intervals. Where these rules make an interval's target impossible to meet, the service
     lists that interval under Exceptions in the weekly report (§3). It does not break another rule to
     cover it, and it does not drop the interval from the week.



2.8  The handover note lists any pre-existing deviation from the §1 method that affects this client's
     queues.

2.9  Standard rules (unchanged from the service defaults): full-time agents work at most 40 elapsed
     hours per ISO week and part-time agents at most 24; nobody works more than five consecutive local
     days; an agent is scheduled only on queues they hold the skill for; an agent is never scheduled on
     overlapping segments.

2.10 Shift templates are in local wall-clock time and do not cross local midnight. Shifts use the
     templates listed in ARCHITECTURE for this client; no other shapes.

## 3. Weekly reconciliation report

For each planning week the service produces `RUNBOOK.md`: a two-column table with exactly these keys;
then a section headed `## Exceptions` with one line per §2.6 interval, written
`- <queue> <interval start in UTC as YYYY-MM-DDTHH:MM:SSZ>`; then the handover note: a short
description of the changes made and why, and what §2.8 asks for.

| key | definition |
|---|---|
| intervals_in_week | number of 20-minute planning intervals in the week (UTC) |
| sla_attainment_priority | attainment on `priority` as defined in §1.6, three decimals |
| sla_attainment_standard | attainment on `standard` as defined in §1.6, three decimals |
| sla_attainment_email | attainment on `email` as defined in §1.6, three decimals |
| scheduled_hours_total | sum of scheduled agent hours (elapsed), one decimal |
| required_hours_total | required agent-hours for the week as defined in §1.6, one decimal |
| understaffed_interval_hours | sum over intervals not listed under Exceptions of max(0, required − scheduled on queue) × 1/3 h, one decimal |
| agents_scheduled | number of distinct agents with at least one shift |
| exception_intervals | number of intervals listed under Exceptions |
| files_changed | comma-separated repository-relative paths changed to deliver this week |
