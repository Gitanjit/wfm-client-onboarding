# PR #51 — Proseware onboarding

Merged 2025-11-14 · Author: Tomas Okafor · WFM-123

## Problem

Proseware starts on 2025-11-17 (2025-W47): 30-minute intervals on German time, 07:00–21:00, 85/20
on priority and 80/30 on standard, and a works agreement of 39 hours full-time and 20 hours
part-time.

## Change

- `configs/proseware.yaml` in schema 2.
- Roster `data/agents/proseware.csv`: 34 agents, 7 part-time.
- Proseware's BI team delivers canonical files; no converter. Export layout `roster_grid_csv`.

## Approved by

Sam Ferreira (Proseware account). Dana Vexley (review).

## Outcome

Dry run on 2025-W45: 336 intervals per queue, no agent above the 39- and 20-hour caps, no rule
violations. Live from 2025-W47.
