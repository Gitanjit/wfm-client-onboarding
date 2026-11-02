# PR #9 — Tailspin onboarding

Merged 2025-01-09 · Author: Dana Vexley · WFM-019

## Problem

Tailspin Toys starts on 2025-01-13 (2025-W03). It plans in 30-minute intervals on Irish time,
opens 07:00–21:00, and contracts a slower answer target on its standard queue (80 % in 30 s).
It is the first client that does not fit the service defaults.

## Change

- Tailspin's settings: 30-minute grain, Europe/Dublin, operating hours 07:00–21:00, standard queue
  at 80/30.
- Roster `data/agents/tailspin.csv`: 30 agents, 6 part-time.
- Converter for Tailspin's local-time export: UTC from the offset on each row.

## Approved by

Joel Mbeki (schedule review). Tailspin's operations lead confirmed the operating hours.

## Outcome

Dry run on the sample week 2025-W01: 336 intervals per queue, every day staffed 07:00–21:00, no
rule violations. Live from 2025-W03. Client-specific settings need a proper home before the next
client signs.
