# PR #14 — Adatum onboarding

Merged 2025-03-07 · Author: Tomas Okafor · WFM-034

## Problem

Adatum starts on 2025-03-10 (2025-W11): hourly intervals, US Mountain time, the service's default
hours and targets. Second client off the defaults.

## Change

- `configs/adatum.yaml`: `interval_minutes: 60`, `tz: America/Denver`. Everything else inherited
  (ADR 0004).
- Roster `data/agents/adatum.csv`: 30 agents, 6 part-time.
- Converter for Adatum's hourly report (offset per row).

## Approved by

Dana Vexley (review).

## Outcome

Dry run on 2025-W09: 168 intervals per queue, no rule violations. Live from 2025-W11, the week
after the US spring-forward.
