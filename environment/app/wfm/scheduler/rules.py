"""Contractual scheduling rules as predicates. Which ones apply is a per-client config choice.

Northwind SOW §2 is the first contract to use all three (configs/northwind.yaml).
"""
from __future__ import annotations

from datetime import datetime, timedelta
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


def break_slot(window: list[datetime], surplus: Callable[[datetime], float]) -> datetime:
    """SOW §2.3: the window slot where gross coverage surplus (scheduled on the queue, ignoring
    breaks, minus required) is largest; ties go to the earliest slot."""
    return max(window, key=lambda t: (surplus(t), -t.timestamp()))
