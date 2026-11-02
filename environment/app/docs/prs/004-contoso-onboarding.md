# PR #4 — Contoso onboarding

Merged 2024-11-29 · Author: Dana Vexley · WFM-006

## Problem

Contoso signed for weekly planning from 2024-W49 (Monday 2 December 2024). Its platform exports
15-minute intervals in UTC for two queues, priority and standard, which is the shape the service
plans in. Nothing in the service had yet run on a real client's week.

## Change

- Contoso runs on the service defaults: 15-minute grain, UTC, 06:00–24:00, 80/20 on both queues.
- Roster `data/agents/contoso.csv`: 40 agents, 8 of them part-time, skills as Contoso's team
  leads listed them.
- Drop folder and naming agreed: `week_<ISO>.csv`, canonical layout (ADR 0001), Mondays by 07:00 UTC.

## Approved by

Dana Vexley (code). Sam Ferreira (Contoso account) for the drop arrangement. Joel Mbeki reviewed
the dry-run schedule.

## Outcome

Dry run on Contoso's sample week 2024-W47: all 672 intervals per queue present, 40 agents placed,
no rule violations. Live from 2024-W49.
