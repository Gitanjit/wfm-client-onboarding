"""Shared reading for the schedule exporters: out/<client>/schedule.csv -> segments, shifts and
activities, with local wall-clock times computed per row from the client's timezone.

schedule.csv has one row per segment in UTC; a split template has two segments with the same
template and agent; the break sits on the segment that contains it (docs/ARCHITECTURE.md). The
exporters never change times: they regroup and relabel what the run wrote.
"""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

from wfm import weeks

SCHEDULE_COLUMNS = ("agent_id", "queue", "segment_start_utc", "segment_end_utc", "template_id", "segment_idx",
                    "break_start_utc", "break_minutes")
WORK, BREAK = "WORK", "BREAK"


@dataclass(frozen=True)
class Segment:
    agent_id: str
    queue: str
    template_id: str
    segment_idx: int
    start: datetime                 # UTC
    end: datetime                   # UTC
    break_start: datetime | None    # UTC, only on the segment holding the break
    break_minutes: int

    @property
    def hours(self) -> float:
        return (self.end - self.start).total_seconds() / 3600

    @property
    def break_end(self) -> datetime | None:
        return None if self.break_start is None else self.break_start + timedelta(minutes=self.break_minutes)


@dataclass(frozen=True)
class Activity:
    agent_id: str
    queue: str
    kind: str                       # WORK or BREAK
    start: datetime                 # UTC
    end: datetime                   # UTC

    @property
    def minutes(self) -> int:
        return int((self.end - self.start).total_seconds() // 60)


@dataclass
class Shift:
    """One template placement: an agent's segments on one local day."""
    agent_id: str
    queue: str
    template_id: str
    day: date                       # local date of the first segment
    segments: list[Segment] = field(default_factory=list)

    @property
    def hours(self) -> float:
        return sum(s.hours for s in self.segments)

    @property
    def start(self) -> datetime:
        return self.segments[0].start

    @property
    def end(self) -> datetime:
        return self.segments[-1].end

    @property
    def breaks(self) -> list[Segment]:
        return [s for s in self.segments if s.break_start is not None]


def _utc(s) -> datetime | None:
    """ISO timestamp -> aware UTC datetime; empty cells (no break) -> None."""
    if not isinstance(s, str) or not s:
        return None
    ts = pd.Timestamp(s)
    return (ts.tz_localize("UTC") if ts.tzinfo is None else ts.tz_convert("UTC")).to_pydatetime()


def read_schedule(path: Path) -> list[Segment]:
    """Segments of a schedule.csv, sorted by agent, start, segment index."""
    try:
        df = pd.read_csv(path, dtype={"agent_id": str, "queue": str, "template_id": str, "break_start_utc": str})
    except FileNotFoundError:
        raise SystemExit(f"no {path}: run the week first (python -m wfm run ...)") from None
    missing = [c for c in SCHEDULE_COLUMNS if c not in df.columns]
    if missing:
        raise SystemExit(f"{path}: missing column(s) {', '.join(missing)}")
    segs = []
    for r in df.itertuples(index=False):
        bstart = _utc(r.break_start_utc)
        bmin = int(r.break_minutes) if r.break_minutes == r.break_minutes else 0
        segs.append(Segment(r.agent_id, r.queue, r.template_id, int(r.segment_idx), _utc(r.segment_start_utc),
                            _utc(r.segment_end_utc), bstart if bmin else None, bmin if bstart else 0))
    return sorted(segs, key=lambda s: (s.agent_id, s.start, s.segment_idx))


def check_week(segments: list[Segment], week: str, tz: str) -> None:
    """Every segment must start inside the client's local week; otherwise schedule.csv is from
    another week's run."""
    lo, hi = weeks.bounds_utc(week, tz)
    outside = [s for s in segments if not lo <= s.start < hi]
    if outside:
        raise SystemExit(f"schedule.csv has {len(outside)} segment(s) outside {week} ({tz}); "
                         f"first at {outside[0].start:%Y-%m-%dT%H:%MZ}: run {week} first")


def shifts(segments: list[Segment], tz: str) -> list[Shift]:
    """Group segments into shifts: a shift starts at segment 0 and takes the agent's following
    segments of the same template."""
    out: list[Shift] = []
    current: dict[str, Shift] = {}
    for s in segments:
        sh = current.get(s.agent_id)
        if s.segment_idx == 0 or sh is None or sh.template_id != s.template_id:
            sh = Shift(s.agent_id, s.queue, s.template_id, weeks.to_local(s.start, tz).date())
            current[s.agent_id] = sh
            out.append(sh)
        sh.segments.append(s)
    return sorted(out, key=lambda x: (x.agent_id, x.start))


def activities(seg: Segment) -> list[Activity]:
    """A segment as WORK / BREAK / WORK activities (no zero-length pieces)."""
    if seg.break_start is None:
        return [Activity(seg.agent_id, seg.queue, WORK, seg.start, seg.end)]
    bs, be = max(seg.break_start, seg.start), min(seg.break_end, seg.end)
    parts = [(WORK, seg.start, bs), (BREAK, bs, be), (WORK, be, seg.end)]
    return [Activity(seg.agent_id, seg.queue, k, a, b) for k, a, b in parts if b > a]


def local_stamp(t: datetime, tz: str) -> str:
    """'YYYY-MM-DD HH:MM' in the client's wall-clock time."""
    return weeks.to_local(t, tz).strftime("%Y-%m-%d %H:%M")


def iso_utc(t: datetime) -> str:
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def iso_local(t: datetime, tz: str) -> str:
    loc = weeks.to_local(t, tz)
    return loc.strftime("%Y-%m-%dT%H:%M:%S") + weeks.offset(loc)


def to_csv(header: list[str], rows: list[list]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue()
