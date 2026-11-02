# PR #50 — Client config schema 2

Merged 2025-11-13 · Author: Tomas Okafor · WFM-121

## Problem

Proseware's onboarding sheet comes in sections that map onto the flat config badly, and a
mistyped key in a flat file silently falls back to the default (ADR 0007).

## Change

- `wfm/config.py`: a client file with `schema: 2` is flattened on load (`_flatten_v2`), with four
  sections: service, targets, staffing, scheduling. Unknown sections and misplaced keys stop the
  run with the key named.
- Schema-1 files untouched; no client migrated.

## Approved by

Dana Vexley (review). Mei Lindqvist.

## Outcome

Every existing client's loaded config compared key by key before and after: identical. Proseware
(PR #51) is the first schema-2 client.
