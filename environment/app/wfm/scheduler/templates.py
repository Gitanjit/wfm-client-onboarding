"""Shift templates: local wall-clock segments on one local day; none crosses local midnight."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class Template:
    id: str
    segments: tuple[tuple[int, int], ...]  # (start_hour, end_hour) local, end may be 24
    eligibility: str = "all"               # "all" or a contract code

    @property
    def hours(self) -> float:
        return float(sum(e - s for s, e in self.segments))

    @property
    def is_split(self) -> bool:
        return len(self.segments) > 1

    def segments_utc(self, day: date, tz: str) -> list[tuple[datetime, datetime]]:
        """Local wall-clock segments on `day` -> UTC datetimes."""
        z = ZoneInfo(tz)
        midnight = datetime(day.year, day.month, day.day, tzinfo=z)
        return [((midnight + timedelta(hours=s)).astimezone(timezone.utc),
                 (midnight + timedelta(hours=e)).astimezone(timezone.utc)) for s, e in self.segments]


TEMPLATES: list[Template] = [
    Template("E8", ((6, 14),)),
    Template("D8", ((9, 17),)),
    Template("L8", ((13, 21),)),
    Template("N8", ((16, 24),)),
    Template("P6a", ((7, 13),)),
    Template("P6b", ((15, 21),)),
    Template("P4", ((10, 14),)),
    Template("S44", ((8, 12), (16, 20)), eligibility="all"),
]


def templates_for(cfg: dict) -> list[Template]:
    """Templates that fit inside the client's local operating hours."""
    open_h, close_h = cfg["operating_hours"]
    return [t for t in TEMPLATES if all(open_h <= s and e <= close_h for s, e in t.segments)]


def eligible(template: Template, contract: str) -> bool:
    return template.eligibility == "all" or template.eligibility == contract
