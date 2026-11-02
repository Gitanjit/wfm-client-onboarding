"""Minimum cover: queues that need a number of agents on shift whatever the volume.

A client config names them under `min_cover`, with the local hours the floor applies:

    min_cover:
      chat: {agents: 2, hours: [20, 24]}

The scheduler raises each interval's requirement on the queue to the floor; the evaluator reports
intervals below it as `min_cover` violations.

Cross-skilled cover (PR #31). An agent on shift on another queue who also holds the floor queue's
skill counts `cross_skill_weight` of an agent toward the floor (service default 0.5: a voice agent
with the chat skill picks up chats between calls). The weight applies to the floor only; required
agents from the staffing model are always counted on the queue itself.
"""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo


def floor(queue: str, t: datetime, cfg: dict) -> int:
    """Agents the floor asks for on `queue` in the interval starting at `t` (0 if none applies)."""
    rule = (cfg.get("min_cover") or {}).get(queue)
    if not rule:
        return 0
    loc = t.astimezone(ZoneInfo(cfg["tz"]))
    h = loc.hour + loc.minute / 60
    lo, hi = rule.get("hours", cfg["operating_hours"])
    return int(rule["agents"]) if lo <= h < hi else 0


def weight(cfg: dict) -> float:
    return float(cfg.get("cross_skill_weight", 0.0))


def cover(on_queue: float, cross_skilled: float, cfg: dict) -> float:
    """Cover counted toward a floor: agents on the queue plus weighted cross-skilled agents elsewhere."""
    return on_queue + weight(cfg) * cross_skilled


def uncovered(required: int, floor_need: int, on_queue: float, cross_skilled: float, cfg: dict) -> float:
    """What the interval still lacks: the staffing requirement (agents on the queue) or the floor
    (cover as above), whichever is short by more."""
    return max(0.0, required - on_queue, floor_need - cover(on_queue, cross_skilled, cfg))
