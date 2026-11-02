# PR #31 — Night chat coverage for Contoso

Author: Tomas Okafor · merged 2025-07-21

## Problem
Contoso's SOW amendment of 14 July adds an evening chat line and asks for at least two chat agents on
shift from 20:00 to 24:00 UTC every day. Contoso has three chat-skilled agents. Two of them on chat for
four hours a night is 56 agent-hours a week on top of their voice shifts; the roster cannot carry it
and the scheduler has no notion of a minimum per queue.

## Change
- New `wfm/constraints.py`: per-queue floors from `min_cover` in the client config
  (`{queue: {agents, hours}}`). The scheduler raises the interval's requirement to the floor; the
  evaluator reports intervals below it as `min_cover` violations.
- Cross-skilled cover: an agent on shift on another queue who holds the floor queue's skill counts
  `cross_skill_weight` toward the floor. Service default 0.5 in `configs/defaults.yaml`: Contoso's
  voice agents with the chat skill take chats between calls in the quiet evening hours (Contoso ops
  confirmed one concurrent chat per voice agent).
- `configs/contoso.yaml`: chat queue and `min_cover: {chat: {agents: 2, hours: [20, 24]}}`; loader
  queue list gains `chat`.
- Tests: floor windows, the 0.5 weight, a staffing requirement is never met by cross-skilled agents.

## Approved by
Sam Ferreira (account manager, Contoso), 2025-07-18. Reviewed by Dana Vexley.

## Outcome
Contoso's evening floor reported met every night from 2025-W30. Contoso ended the evening chat line on
2025-09-01; the floor was removed from `configs/contoso.yaml` and the queue list went back to two.
