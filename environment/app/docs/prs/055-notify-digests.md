# PR #55 — Weekly digests and agent shift lists

Merged 2026-06-12 · Author: Mei Lindqvist · WFM-171

## Problem

The weekly status mail to each account manager was written by hand from `eval.json`, and team
leads copied each agent's shifts out of the export to send round. Both took most of Monday
afternoon and both had typos in them.

## Change

- `python -m wfm notify --client <c> --week <week>` writes `out/<client>/notify/<week>/digest.txt`
  (attainment against target per queue, hours, agents, understaffed hours, any rule violations)
  one shift list per agent in local time under `agents/`, and one sheet per local day under
  `days/` for the floor.
- Nothing is sent from the service. The ops mailbox sends the digest; team leads forward the
  shift lists.

## Approved by

Ruth Abara and Sam Ferreira (digest wording). Dana Vexley (review).

## Outcome

Used for every live client from 2026-W24.
