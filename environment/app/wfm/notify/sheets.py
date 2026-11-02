"""Daily sheets for team leads: each local day's shifts in start order, and headcount per queue at
each local hour of the operating day. One text file per day under
out/<client>/notify/<week>/days/<YYYY-MM-DD>.txt.

Headcount is agents on shift on the queue at the hour (gross of breaks); the breaks column counts
breaks that start within the hour.
"""
from __future__ import annotations

from datetime import date, timedelta

from wfm import weeks
from wfm.export.base import Segment, Shift, shifts
from wfm.notify import templates
from wfm.report import markdown as md


def _times(sh: Shift, tz: str) -> str:
    return ", ".join(f"{weeks.hhmm(weeks.to_local(s.start, tz))}-{weeks.hhmm(weeks.to_local(s.end, tz), sh.day)}"
                     for s in sh.segments)


def _breaks(sh: Shift, tz: str) -> str:
    return ", ".join(weeks.hhmm(weeks.to_local(s.break_start, tz)) for s in sh.breaks)


def headcount(day_shifts: list[Shift], day: date, cfg: dict, queues: list[str]) -> list[list]:
    rows = []
    segs = [s for sh in day_shifts for s in sh.segments]
    for h, t in weeks.hour_starts(day, cfg["tz"], cfg["operating_hours"]):
        on = [sum(1 for s in segs if s.queue == q and s.start <= t < s.end) for q in queues]
        brk = sum(1 for s in segs if s.break_start is not None and t <= s.break_start < t + timedelta(hours=1))
        rows.append([f"{h:02d}:00", *on, brk])
    return rows


def sheet(day: date, day_shifts: list[Shift], cfg: dict, queues: list[str]) -> str:
    tz = cfg["tz"]
    ordered = sorted(day_shifts, key=lambda sh: (sh.start, sh.agent_id))
    if ordered:
        starts = md.text_table(["times", "agent", "queue", "template", "break"],
                               [[_times(sh, tz), sh.agent_id, sh.queue, sh.template_id, _breaks(sh, tz)]
                                for sh in ordered], align="lllll")
    else:
        starts = "  " + templates.NO_SHIFTS_DAY
    count = md.text_table(["hour", *queues, "breaks"], headcount(ordered, day, cfg, queues))
    return templates.DAY_SHEET.substitute(
        name=cfg.get("name", cfg["client"]), day_label=f"{weeks.DAY_NAMES[day.weekday()]} {day:%d %b %Y}", tz=tz,
        shifts=len(ordered), hours=md.num(sum(sh.hours for sh in ordered)), starts=starts, headcount=count)


def sheets(segments: list[Segment], cfg: dict, week: str) -> dict[date, str]:
    """{local date: sheet text} for the seven days of the week. Queues are the configured ones plus
    any the schedule uses."""
    all_shifts = shifts(segments, cfg["tz"])
    queues = sorted(set(cfg.get("sla", {})) | {s.queue for s in segments})
    return {d: sheet(d, [sh for sh in all_shifts if sh.day == d], cfg, queues) for d in weeks.days(week)}
