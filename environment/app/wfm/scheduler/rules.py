"""Contractual scheduling rules as predicates. Which ones apply is a per-client config choice.

Northwind SOW §2 is the first contract to use rest, PT-only splits and surplus breaks
(configs/northwind.yaml); Litware adds a per-queue floor, a per-queue earliest start and the
infeasible-interval report (configs/litware.yaml).
"""
from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Callable

from wfm.scheduler.templates import Template


def rest_ok(last_end: datetime | None, start: datetime, min_rest_hours: float) -> bool:
    """SOW §2.1: at least `min_rest_hours` of elapsed time between the end of an agent's previous
    shift and the start of the next, across days within the week. No predecessor -> ok."""
    return last_end is None or start - last_end >= timedelta(hours=min_rest_hours)


def split_allowed(template: Template, contract: str, policy: str) -> bool:
    """SOW §2.2: split shifts (two segments on one local day) only for contracts named by the
    policy ("all" keeps the service default)."""
    return not template.is_split or policy == "all" or contract == policy


def queue_allows(template: Template, queue: str, earliest: dict) -> bool:
    """Litware SOW §2.5 (R5): nobody on `queue` before its earliest local hour."""
    return template.segments[0][0] >= earliest.get(queue, 0)


def operating(t: datetime, tz: str, hours) -> bool:
    loc = t.astimezone(ZoneInfo(tz))
    return hours[0] <= loc.hour + loc.minute / 60 < hours[1]


def floor_need(queue: str, t: datetime, cfg: dict) -> int:
    """Litware SOW §2.4 (R4): agents scheduled on `queue` in every operating interval (0 when not configured)."""
    n = cfg.get("min_agents", {}).get(queue, 0)
    return n if n and operating(t, cfg["tz"], cfg["operating_hours"]) else 0


def infeasible(req, cfg: dict, templates: list[Template]) -> list[tuple[str, datetime]]:
    """Intervals with volume that no template allowed on their queue can cover (SOW §2.6 exceptions)."""
    earliest = cfg.get("queue_earliest_hour", {})
    out = []
    for q, g in req.groupby("queue", sort=False):
        allowed = [t for t in templates if queue_allows(t, q, earliest)]
        for t, v in zip(g["interval_start_utc"], g["volume"]):
            if v <= 0:
                continue
            day = t.astimezone(ZoneInfo(cfg["tz"])).date()
            if not any(s <= t < e for tpl in allowed for s, e in tpl.segments_utc(day, cfg["tz"])):
                out.append((q, t))
    return sorted(out, key=lambda x: (x[1], x[0]))


def break_slot(window: list[datetime], surplus: Callable[[datetime], float]) -> datetime:
    """SOW §2.3: the window slot where gross coverage surplus (scheduled on the queue, ignoring
    breaks, minus required) is largest; ties go to the earliest slot."""
    return max(window, key=lambda t: (surplus(t), -t.timestamp()))
