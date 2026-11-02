# 2025-06-24 — Hosted telephony outage (Contoso, Tailspin, Adatum, Woodgrove)

Incident: Tuesday 2025-06-24, 13:40–16:20 UTC · Written: 2025-07-01 · Author: Mei Lindqvist · WFM-068

## Summary

The hosted telephony platform that carries inbound calls for four of our clients rejected calls for
2 h 40 min. No contacts reached those clients' queues in that window. The service itself was not
affected. This note records what the outage looks like in the data and how the week is treated.

## What the 2025-W26 files show

Zero volume on both queues for every interval wholly inside the window; the interval on each side
keeps the share of its contacts that arrived outside it. The files were committed as delivered.

| client | grain | local time of the window | zero-volume intervals (local) |
|---|---|---|---|
| contoso | 15 min | 13:40–16:20 UTC | 13:45–16:15, 10 intervals |
| tailspin | 30 min | 14:40–17:20 Europe/Dublin | 15:00–17:00, 4 intervals |
| adatum | 60 min | 07:40–10:20 America/Denver | 08:00–10:00, 2 intervals |
| woodgrove | 30 min | 06:40–09:20 America/Los_Angeles | 07:00–09:00, 4 intervals |

## Effect on planning and reporting

- The evaluator skips intervals without volume, so 2025-W26 attainment for these clients is computed
  over slightly fewer intervals. The weekly figures were reported as computed, with a line on the
  outage in each digest.
- Schedules built on the W26 files plan less cover inside the window. Each client's planners were
  told to take Tuesday afternoon from the W25 baseline instead.
- When W26 is used as a reference week later, treat Tuesday 24 June as an outage, not as demand.

## Detection and follow-up

Contoso's account team heard about the outage from the client on the day. For the other three clients
it surfaced in Monday's weekly run (30 June), when the reviewer saw Tuesday's schedules thin out in
the afternoon, after the files had been committed. Follow-up: a volume report that lists zero-volume runs inside operating hours at drop
time (PR #24).
