"""WIP — week-aware rewrite of the greedy scheduler. Do not wire in yet (WFM-231).

Same template-placement loop as `greedy.py`, but with week state so that the rules in the newer
contracts (minimum rest between shifts, split shifts only for part-time) are enforced while placing
instead of being audited afterwards.

Status
  [x] week state per agent: hours, days worked, previous shift end
  [x] rest between shifts (MIN_REST_HOURS; move to config before wiring in)
  [x] split templates only for PT contracts
  [ ] break placement per contract (still the midpoint rule, copied from greedy.py)
  [ ] compare output with greedy.py on Contoso W41–W43; unit tests
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd

from wfm.ingest.loader import local_days
from wfm.roster import Agent
from wfm.scheduler.greedy import Shift, _covered, _would_exceed_run
from wfm.scheduler.templates import templates_for

MIN_REST_HOURS = 11.0   # TODO(WFM-231): read from config; 11 h is the figure in the newer contracts


def _rested(last_end: datetime | None, start: datetime, min_rest_hours: float) -> bool:
    """At least `min_rest_hours` between the previous shift's end and this start. No previous shift: ok."""
    return last_end is None or start - last_end < timedelta(hours=min_rest_hours)


def schedule_week(req: pd.DataFrame, cfg: dict, agents: list[Agent], week: str) -> list[Shift]:
    tz = cfg["tz"]
    grain_h = cfg["interval_minutes"] / 60.0
    caps = cfg["weekly_hours"]
    max_run = cfg["max_consecutive_days"]
    templates = templates_for(cfg)
    queues = list(dict.fromkeys(req["queue"]))

    required = {q: dict(zip(g["interval_start_utc"], g["required"])) for q, g in req.groupby("queue")}
    cover = {q: defaultdict(int) for q in queues}
    grid = sorted(set(req["interval_start_utc"]))
    z = ZoneInfo(tz)

    # week state
    hours_used: dict[str, float] = defaultdict(float)
    days_worked: dict[str, list[date]] = defaultdict(list)
    last_end: dict[str, datetime] = {}
    shifts: list[Shift] = []

    for day in local_days(week, tz):
        day_grid = [t for t in grid if t.astimezone(z).date() == day]
        worked_today: set[str] = set()
        dead: set[tuple[str, str]] = set()
        while True:
            best, best_val = None, 0.0
            for tpl in templates:
                segs = tpl.segments_utc(day, tz)
                ivs = _covered(segs, day_grid)
                for q in queues:
                    if (tpl.id, q) in dead:
                        continue
                    val = sum(max(0, min(1, required[q][t] - cover[q][t])) for t in ivs)
                    if val > best_val + 1e-9:
                        best, best_val = (tpl, q, segs, ivs), val
            if best is None or best_val * grain_h < 0.5:
                break
            tpl, q, segs, ivs = best
            cands = [a for a in agents
                     if q in a.skills and a.agent_id not in worked_today
                     and (not tpl.is_split or a.contract == "PT")
                     and hours_used[a.agent_id] + tpl.hours <= caps[a.contract] + 1e-9
                     and not _would_exceed_run(days_worked[a.agent_id], day, max_run)
                     and _rested(last_end.get(a.agent_id), segs[0][0], MIN_REST_HOURS)]
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

    _place_breaks_midpoint(shifts, cfg)
    return shifts


def _place_breaks_midpoint(shifts: list[Shift], cfg: dict) -> None:
    """Copied from greedy.place_breaks. TODO(WFM-231): contract-specific placement."""
    rule = cfg["break"]
    length = timedelta(minutes=rule["minutes"])
    for sh in shifts:
        if sh.hours < rule["min_shift_hours"]:
            continue
        fits = [t for t in sh.intervals if any(s <= t and t + length <= e for s, e in sh.segments)]
        if not fits:
            continue
        mid = sh.segments[0][0] + timedelta(hours=sh.hours / 2)
        sh.break_start = min(fits, key=lambda t: (abs((t - mid).total_seconds()), t))
        sh.break_minutes = rule["minutes"]
