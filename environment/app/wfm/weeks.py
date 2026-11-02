"""ISO-week helpers for the reporting, export and notification commands.

Weeks are written `YYYY-Www` (ISO 8601, Monday first), the form `wfm run --week` takes. A client's
week runs from local Monday 00:00 to the next local Monday 00:00 in the client's timezone, so a week
that contains a DST change is 167 or 169 hours long and has a different number of intervals.
"""
from __future__ import annotations

import re
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from wfm.ingest.loader import iso_week_monday

WEEK_RE = re.compile(r"^(\d{4})-W(\d{2})$")
DAY_NAMES = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")


def weeks_in_year(year: int) -> int:
    """52 or 53: the ISO week of 28 December is always the year's last week."""
    return date(year, 12, 28).isocalendar().week


def parse(week: str) -> tuple[int, int]:
    """'2026-W44' -> (2026, 44). Raises ValueError for anything else, including W53 in a 52-week year."""
    m = WEEK_RE.match(week or "")
    if not m:
        raise ValueError(f"not an ISO week: {week!r} (expected YYYY-Www, e.g. 2026-W44)")
    year, wk = int(m.group(1)), int(m.group(2))
    if not 1 <= wk <= weeks_in_year(year):
        raise ValueError(f"{week}: {year} has {weeks_in_year(year)} ISO weeks")
    return year, wk


def fmt(year: int, wk: int) -> str:
    return f"{year}-W{wk:02d}"


def monday(week: str) -> date:
    parse(week)
    return iso_week_monday(week)


def week_of(d: date) -> str:
    """The ISO week containing the date `d`."""
    iso = d.isocalendar()
    return fmt(iso.year, iso.week)


def add_weeks(week: str, n: int) -> str:
    return week_of(monday(week) + timedelta(weeks=n))


def key(week: str) -> tuple[int, int]:
    """Sort key; plain string order is also correct for zero-padded weeks, this one validates."""
    return parse(week)


def week_range(first: str, last: str) -> list[str]:
    """Every ISO week from `first` to `last`, both included. Empty when last < first."""
    out, w = [], first
    while key(w) <= key(last):
        out.append(w)
        w = add_weeks(w, 1)
    return out


def days(week: str) -> list[date]:
    mon = monday(week)
    return [mon + timedelta(days=i) for i in range(7)]


def label(week: str) -> str:
    """'2026-W43' -> '2026-W43 (Mon 19 Oct - Sun 25 Oct 2026)'."""
    d = days(week)
    return f"{week} ({DAY_NAMES[0]} {d[0]:%d %b} - {DAY_NAMES[6]} {d[6]:%d %b %Y})"


def bounds_utc(week: str, tz: str) -> tuple[datetime, datetime]:
    """UTC instants of local Monday 00:00 and the following local Monday 00:00."""
    z = ZoneInfo(tz)
    mon = monday(week)
    start = datetime(mon.year, mon.month, mon.day, tzinfo=z)
    end = start + timedelta(days=7)   # wall-clock arithmetic: the next local midnight, DST included
    return start.astimezone(timezone.utc), end.astimezone(timezone.utc)


def week_hours(week: str, tz: str) -> float:
    start, end = bounds_utc(week, tz)
    return (end - start).total_seconds() / 3600


def expected_intervals(week: str, tz: str, grain_min: int) -> int:
    """Intervals of `grain_min` minutes in the client's local week (336 at 30 min without a DST change)."""
    return int(week_hours(week, tz) * 60 // grain_min)


def to_local(t: datetime, tz: str) -> datetime:
    if t.tzinfo is None:
        raise ValueError(f"naive timestamp {t!r}: expected UTC")
    return t.astimezone(ZoneInfo(tz))


def local_hour(t: datetime, tz: str) -> float:
    loc = to_local(t, tz)
    return loc.hour + loc.minute / 60


def in_operating_hours(t: datetime, tz: str, hours) -> bool:
    """True if the interval starting at UTC `t` starts inside the local operating hours [open, close)."""
    open_h, close_h = hours
    return open_h <= local_hour(t, tz) < close_h


def hour_starts(day: date, tz: str, hours=(0, 24)) -> list[tuple[int, datetime]]:
    """(local hour, UTC instant) for each whole local hour of `day` in [open, close). A local hour
    that does not exist (spring-forward) is skipped; a repeated one is listed once."""
    z = ZoneInfo(tz)
    out = []
    for h in range(int(hours[0]), int(hours[1])):
        loc = datetime(day.year, day.month, day.day, h, tzinfo=z)
        if loc.astimezone(timezone.utc).astimezone(z).hour == h:
            out.append((h, loc.astimezone(timezone.utc)))
    return out


def offset(t_local: datetime) -> str:
    """UTC offset of an aware datetime as '+HH:MM' / '-HH:MM'."""
    z = t_local.strftime("%z")
    return f"{z[:3]}:{z[3:]}"


def hhmm(t_local: datetime, day: date | None = None) -> str:
    """Local wall-clock 'HH:MM'. With `day`, a time at midnight after that day is written '24:00'."""
    if day is not None and t_local.date() > day and t_local.hour == 0 and t_local.minute == 0:
        return "24:00"
    return t_local.strftime("%H:%M")
