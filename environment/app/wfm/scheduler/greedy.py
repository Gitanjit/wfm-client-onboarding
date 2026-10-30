"""Greedy template placement, one local day at a time.

For each local day of the week: while some (template, queue) pair still covers at least half an
hour of uncovered requirement, place the best-scoring pair on the available agent with the fewest
hours so far. Breaks go at the shift midpoint. Deterministic: fixed template order, agent ids as
the tie-break.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd

from wfm import constraints
from wfm.ingest.loader import local_days
from wfm.roster import Agent
from wfm.scheduler import rules
from wfm.scheduler.templates import Template, eligible, templates_for


@dataclass
class Shift:
    agent_id: str
    queue: str
    template: Template
    day: date
    segments: list[tuple[datetime, datetime]]
    intervals: list[datetime] = field(default_factory=list)   # grid slots the segments cover
    break_start: datetime | None = None
    break_minutes: int = 0

    @property
    def hours(self) -> float:
        return sum((e - s).total_seconds() for s, e in self.segments) / 3600.0


def _covered(segments, day_grid) -> list[datetime]:
    return [t for s, e in segments for t in day_grid if s <= t < e]


def schedule_week(req: pd.DataFrame, cfg: dict, agents: list[Agent], week: str) -> list[Shift]:
    tz = cfg["tz"]
    grain_h = cfg["interval_minutes"] / 60.0
    caps = cfg["weekly_hours"]
    max_run = cfg["max_consecutive_days"]
    templates = templates_for(cfg)
    queues = list(dict.fromkeys(req["queue"]))

    required = {q: dict(zip(g["interval_start_utc"], g["required"])) for q, g in req.groupby("queue")}
    cover = {q: defaultdict(int) for q in queues}
    cross = {q: defaultdict(int) for q in queues}    # agents on another queue holding this skill (min_cover)
    grid = sorted(set(req["interval_start_utc"]))
    z = ZoneInfo(tz)
    floors = {q: {t: constraints.floor(q, t, cfg) for t in grid} for q in queues}

    min_rest = float(cfg.get("min_rest_hours", 0))
    split_policy = str(cfg.get("split_shifts", "all"))

    hours_used: dict[str, float] = defaultdict(float)
    days_worked: dict[str, list[date]] = defaultdict(list)
    last_end: dict[str, datetime] = {}   # week state: when each agent's previous shift ended (UTC)
    shifts: list[Shift] = []

    for day in local_days(week, tz):
        day_grid = [t for t in grid if t.astimezone(z).date() == day]
        worked_today: set[str] = set()
        dead: set[tuple[str, str]] = set()   # (template, queue) pairs nobody can take today
        while True:
            best, best_val = None, 0.0
            for tpl in templates:
                segs = tpl.segments_utc(day, tz)
                ivs = _covered(segs, day_grid)
                for q in queues:
                    if (tpl.id, q) in dead:
                        continue
                    val = sum(min(1, constraints.uncovered(required[q][t], floors[q][t], cover[q][t], cross[q][t], cfg))
                              for t in ivs)
                    if val > best_val + 1e-9:
                        best, best_val = (tpl, q, segs, ivs), val
            if best is None or best_val * grain_h < 0.5:
                break
            tpl, q, segs, ivs = best
            cands = [a for a in agents
                     if q in a.skills and eligible(tpl, a.contract) and a.agent_id not in worked_today
                     and rules.split_allowed(tpl, a.contract, split_policy)
                     and hours_used[a.agent_id] + tpl.hours <= caps[a.contract] + 1e-9
                     and not _would_exceed_run(days_worked[a.agent_id], day, max_run)
                     and rules.rest_ok(last_end.get(a.agent_id), segs[0][0], min_rest)]
            if not cands:
                dead.add((tpl.id, q))
                continue
            a = min(cands, key=lambda x: (hours_used[x.agent_id], x.agent_id))
            shifts.append(Shift(a.agent_id, q, tpl, day, segs, ivs))
            hours_used[a.agent_id] += tpl.hours
            days_worked[a.agent_id].append(day)
            last_end[a.agent_id] = segs[-1][1]
            worked_today.add(a.agent_id)
            for t in ivs:
                cover[q][t] += 1
                for other in a.skills & set(queues) - {q}:
                    cross[other][t] += 1

    place_breaks(shifts, cfg, required, cover)
    return shifts


def _would_exceed_run(worked: list[date], day: date, max_run: int) -> bool:
    """True if working `day` would make more than max_run consecutive local days."""
    run = 0
    d = day - timedelta(days=1)
    while d in worked:
        run += 1
        d -= timedelta(days=1)
    return run >= max_run


def place_breaks(shifts: list[Shift], cfg: dict, required: dict, cover: dict) -> None:
    """One break per long shift. Placement per config: `midpoint` (service default) or
    `max_surplus` (the window slot with the largest gross coverage surplus on the shift's queue)."""
    rule = cfg["break"]
    length = timedelta(minutes=rule["minutes"])
    lo, hi = (timedelta(hours=h) for h in rule["window_hours"])
    placement = cfg.get("break_placement", "midpoint")
    for sh in shifts:
        if sh.hours < rule["min_shift_hours"]:
            continue
        fits = [t for t in sh.intervals if any(s <= t and t + length <= e for s, e in sh.segments)]
        start = sh.segments[0][0]
        if placement == "max_surplus":
            window = [t for t in fits if lo <= t - start <= hi]
            if not window:
                continue
            q = sh.queue
            sh.break_start = rules.break_slot(window, lambda t: cover[q][t] - required[q][t])
        else:
            if not fits:
                continue
            mid = start + timedelta(hours=sh.hours / 2)
            sh.break_start = min(fits, key=lambda t: (abs((t - mid).total_seconds()), t))
        sh.break_minutes = rule["minutes"]


def to_frame(shifts: list[Shift]) -> pd.DataFrame:
    """schedule.csv rows: one per segment; the break sits on the segment that contains it."""
    rows = []
    for sh in shifts:
        for i, (s, e) in enumerate(sh.segments):
            has_break = sh.break_start is not None and s <= sh.break_start < e
            rows.append({
                "agent_id": sh.agent_id, "queue": sh.queue,
                "segment_start_utc": s.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "segment_end_utc": e.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "template_id": sh.template.id, "segment_idx": i,
                "break_start_utc": sh.break_start.strftime("%Y-%m-%dT%H:%M:%SZ") if has_break else "",
                "break_minutes": sh.break_minutes if has_break else 0,
            })
    df = pd.DataFrame(rows, columns=["agent_id", "queue", "segment_start_utc", "segment_end_utc",
                                     "template_id", "segment_idx", "break_start_utc", "break_minutes"])
    return df.sort_values(["segment_start_utc", "agent_id", "segment_idx"], kind="stable").reset_index(drop=True)
