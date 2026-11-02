# PR #53 — Wingtip onboarding

Merged 2026-02-05 · Author: Mei Lindqvist · WFM-146

## Problem

Wingtip Toys starts on 2026-02-09 (2026-W07): 30-minute intervals on Arizona time (no DST),
06:00–24:00, 30-hour part-time contracts, and a workforce tool that imports schedules through an API.

## Change

- `configs/wingtip.yaml` in schema 2.
- Roster `data/agents/wingtip.csv`: 36 agents, 8 part-time.
- Export layout `segments_json`; checked against Wingtip's import on their test tenant.

## Approved by

Ruth Abara (Wingtip account). Tomas Okafor (review).

## Outcome

Dry run on 2026-W05: 336 intervals per queue, no rule violations; Wingtip's test import accepted
the file unchanged. Live from 2026-W07.
