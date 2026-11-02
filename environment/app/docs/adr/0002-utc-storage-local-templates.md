# 0002 — Store UTC, plan in local wall-clock time

Date: 2024-11-15 · Status: accepted · Author: Dana Vexley

## Context

Clients sit in different timezones and most of them change offset twice a year. Agents work local
shifts ("09:00 to 17:00"), contracts count hours worked, and the platform exports we receive are
stamped in whatever the client's platform uses.

## Decision

- Every timestamp the service stores or writes is UTC (`*_utc` columns, ISO 8601 with `Z`).
- Shift templates are local wall-clock segments on one local day and never cross local midnight. A
  template becomes UTC per day through the client's IANA timezone (`tz`).
- Durations (shift length, weekly hours, rest) are elapsed time, measured in UTC.
- The planning week is the ISO week in the client's local time: local Monday 00:00 to the next local
  Monday 00:00.

## Consequences

- A week that contains a DST change has a different number of intervals: one hour fewer in spring,
  one more in autumn. Code that assumes 7 × 24 hours per week is wrong for those weeks.
- A template that spanned the change night would be an hour shorter or longer in elapsed time. The
  templates in use start at 06:00 local or later, so this does not arise today.
- Reports and exports for people convert back to local time at the edge, per row.
