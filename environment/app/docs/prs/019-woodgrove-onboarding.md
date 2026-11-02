# PR #19 — Woodgrove onboarding

Merged 2025-05-08 · Author: Tomas Okafor · WFM-052

## Problem

Woodgrove Bank starts on 2025-05-12 (2025-W20): 30-minute intervals on US Pacific time,
06:00–21:00, and a contractual 90 % in 30 s on the priority queue.

## Change

- `configs/woodgrove.yaml`: grain, timezone, operating hours, and `sla` with both queues (the
  overlay replaces `sla` whole, so the standard queue's 80/20 is restated).
- Roster `data/agents/woodgrove.csv`: 40 agents, 8 part-time.
- Converter for Woodgrove's export (Pacific wall-clock, no offset column).

## Approved by

Dana Vexley (review). Joel Mbeki (schedule review).

## Outcome

Dry run on 2025-W18: 336 intervals per queue, the 06:00 and 21:00 edges staffed by E8 and L8, no
rule violations. Live from 2025-W20.
