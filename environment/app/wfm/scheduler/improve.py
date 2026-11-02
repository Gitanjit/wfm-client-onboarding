"""Efficiency pass: shed scheduled hours that buy no attainment (Northwind SOW §1.6).

Runs after the greedy placement when a client sets `efficiency_pass: drop_shrink`. The floor is the
greedy schedule's own count of operating intervals meeting target, per queue and local day; no move
may take a (queue, day) below it. Shifts are swept in a fixed order and, for each, the first move
that keeps the floor is taken:
  1. drop the shift;
  2. give it a shorter template: first one whose span lies inside the current span (rest-safe by
     construction), then any other shorter template that keeps the rest rule with the agent's
     neighbouring shifts;
  3. move it to another template of the same length if that raises the met count (this frees
     coverage for later drops).
Breaks are re-placed by the configured rule inside every evaluation; no move may leave more intervals
below a `min_cover` floor (whole agents on the queue) than the greedy did. Sweeps repeat until one changes
nothing: drops and shrinks lower hours, relocations raise the met count, both are bounded. Same
agent, queue and day throughout, so weekly-hours, consecutive-day and skill rules cannot get worse.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta

from wfm import constraints
from wfm.roster import Agent
from wfm.scheduler import rules
from wfm.scheduler.templates import Template, eligible


def _span(t: Template) -> tuple[int, int]:
    return t.segments[0][0], t.segments[-1][1]


def drop_or_shrink(shifts: list, required: dict, live: dict, cfg: dict, agents: list[Agent],
                   templates: list[Template], day_grids: dict[date, list[datetime]], break_for) -> list:
    """Return the improved shift list. `break_for(shift, surplus_fn)` gives the break start the
    configured rule would choose (or None); `live[q]` is the set of intervals with volume."""
    from wfm.scheduler.greedy import Shift, _covered   # local import: greedy imports this module

    contract = {a.agent_id: a.contract for a in agents}
    split_policy = str(cfg.get("split_shifts", "all"))
    min_rest = timedelta(hours=float(cfg.get("min_rest_hours", 0)))
    tz = cfg["tz"]
    step = timedelta(minutes=cfg["interval_minutes"])
    brk = timedelta(minutes=cfg["break"]["minutes"])

    groups: dict[tuple[str, date], list] = defaultdict(list)
    by_agent: dict[str, dict[date, object]] = defaultdict(dict)
    for sh in shifts:
        groups[(sh.queue, sh.day)].append(sh)
        by_agent[sh.agent_id][sh.day] = sh

    floor_at = {t: {q: constraints.floor(q, t, cfg) for q in {s.queue for s in shifts}} for g in day_grids.values() for t in g}

    def met(q: str, day: date, group: list) -> tuple[int, int]:
        """(intervals meeting target, intervals below the queue's floor) for one queue and local day."""
        gross: dict[datetime, int] = defaultdict(int)
        for sh in group:
            for t in sh.intervals:
                gross[t] += 1
        off: dict[datetime, int] = defaultdict(int)
        for sh in group:
            b = break_for(sh, lambda t: gross[t] - required[q][t])
            if b is not None:
                for t in sh.intervals:
                    if b < t + step and t < b + brk:
                        off[t] += 1
        ok = sum(1 for t in day_grids[day] if t in live[q] and gross[t] - off[t] >= required[q][t])
        return ok, sum(1 for t in day_grids[day] if gross[t] < floor_at[t].get(q, 0))

    def reshape(sh, tpl: Template):
        segs = tpl.segments_utc(sh.day, tz)
        return Shift(sh.agent_id, sh.queue, tpl, sh.day, segs, _covered(segs, day_grids[sh.day]))

    def allowed(sh) -> list[Template]:
        c = contract.get(sh.agent_id, "FT")
        return [t for t in templates if t.id != sh.template.id and eligible(t, c) and rules.split_allowed(t, c, split_policy)]

    def rest_ok(new) -> bool:
        """The reshaped shift keeps the rest rule against the agent's previous and next shifts."""
        others = [s for d, s in by_agent[new.agent_id].items() if d != new.day]
        before = [s.segments[-1][1] for s in others if s.day < new.day]
        after = [s.segments[0][0] for s in others if s.day > new.day]
        return ((not before or new.segments[0][0] - max(before) >= min_rest)
                and (not after or min(after) - new.segments[-1][1] >= min_rest))

    floor = {k: met(k[0], k[1], g) for k, g in groups.items()}   # (met count, floor shortfall) of the greedy

    def keeps(trial, key, need) -> bool:
        m, short = met(key[0], key[1], trial)
        return m >= need and short <= floor[key][1]
    changed = True
    while changed:
        changed = False
        for key in sorted(groups):
            q, day = key
            group = groups[key]
            for sh in sorted(group, key=lambda s: (-s.hours, s.segments[0][0], s.agent_id)):
                rest = [s for s in group if s is not sh]
                if keeps(rest, key, floor[key][0]):                                   # 1. drop
                    group = rest
                    del by_agent[sh.agent_id][sh.day]
                    changed = True
                    continue
                lo, hi = _span(sh.template)
                shorter = [t for t in allowed(sh) if t.hours < sh.template.hours]
                inside = sorted([t for t in shorter if lo <= _span(t)[0] and _span(t)[1] <= hi], key=lambda t: t.hours)
                outside = sorted([t for t in shorter if t not in inside], key=lambda t: t.hours)
                same = [t for t in allowed(sh) if t.hours == sh.template.hours]
                current = met(q, day, group)[0]
                for tpl, need in [(t, floor[key][0]) for t in inside + outside] + [(t, current + 1) for t in same]:
                    new = reshape(sh, tpl)                                            # 2. shrink / 3. relocate
                    if not rest_ok(new):
                        continue
                    trial = rest + [new]
                    if keeps(trial, key, need):
                        group = trial
                        by_agent[sh.agent_id][sh.day] = new
                        changed = True
                        break
            groups[key] = group

    out = [sh for g in groups.values() for sh in g]
    return sorted(out, key=lambda s: (s.day, s.segments[0][0], s.agent_id))
