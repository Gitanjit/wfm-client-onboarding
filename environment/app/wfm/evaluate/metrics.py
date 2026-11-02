"""Evaluate a schedule.csv against the required curve: attainment, hours, constraint audit.

A convenience for engineers. Contractual evaluation is performed independently against each
client's SOW.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
from zoneinfo import ZoneInfo

import pandas as pd

from wfm import constraints
from wfm.roster import Agent


def _parse(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for c in ("segment_start_utc", "segment_end_utc", "break_start_utc"):
        df[c] = pd.to_datetime(df[c], utc=True)
    df["break_minutes"] = df["break_minutes"].fillna(0).astype(int)
    return df


def coverage(sched: pd.DataFrame, grid, grain_min: int, skills: dict | None = None) -> tuple[dict, dict, dict]:
    """Per queue per interval: gross agents on queue, agents on break (overlapping the slot), and
    agents on shift on another queue who hold this queue's skill (`skills`: agent_id -> skills)."""
    gross = defaultdict(lambda: defaultdict(int))
    on_break = defaultdict(lambda: defaultdict(int))
    cross = defaultdict(lambda: defaultdict(int))
    step = timedelta(minutes=grain_min)
    skills = skills or {}
    for r in sched.itertuples(index=False):
        for t in grid:
            if r.segment_start_utc <= t < r.segment_end_utc:
                gross[r.queue][t] += 1
                for q in skills.get(r.agent_id, ()):
                    if q != r.queue:
                        cross[q][t] += 1
                if r.break_minutes and r.break_start_utc < t + step and t < r.break_start_utc + timedelta(minutes=int(r.break_minutes)):
                    on_break[r.queue][t] += 1
    return gross, on_break, cross


def evaluate(req: pd.DataFrame, sched: pd.DataFrame, cfg: dict, agents: list[Agent], week: str) -> dict:
    sched = _parse(sched)
    grain = cfg["interval_minutes"]
    grid = sorted(set(req["interval_start_utc"]))
    gross, on_break, cross = coverage(sched, grid, grain, {a.agent_id: a.skills for a in agents})
    h = grain / 60.0
    basis = cfg.get("attainment_basis", "service_level")

    sla, under, over = {}, 0.0, 0.0
    for q, g in req.groupby("queue"):
        met = tot = 0
        for r in g.itertuples(index=False):
            if r.volume <= 0:
                continue
            tot += 1
            scheduled = gross[q][r.interval_start_utc] - on_break[q][r.interval_start_utc]
            if basis == "coverage":   # PR #47: scheduled coverage of the requirement, capped at 1
                met += min(1.0, scheduled / r.required) if r.required else 1.0
            elif scheduled >= r.required:
                met += 1
            under += max(0, r.required - scheduled) * h
            over += max(0, scheduled - r.required) * h
        sla[q] = round(met / tot, 3) if tot else 1.0

    hours = float(((sched["segment_end_utc"] - sched["segment_start_utc"]).dt.total_seconds() / 3600).sum())
    return {
        "client": cfg["client"], "week": week, "intervals": len(grid),
        "sla": sla, "meets_target": all(v >= cfg["sla_target"] for v in sla.values()),
        "scheduled_hours": round(hours, 1),
        "understaffed_interval_hours": round(under, 1), "overstaffed_interval_hours": round(over, 1),
        "agents_scheduled": int(sched["agent_id"].nunique()),
        "violations": {**audit(sched, cfg, agents), "min_cover": floor_gaps(gross, cross, grid, cfg)},
    }


def floor_gaps(gross: dict, cross: dict, grid, cfg: dict) -> int:
    """Intervals where a `min_cover` queue has less cover than its floor (see wfm/constraints.py)."""
    return sum(1 for q in (cfg.get("min_cover") or {}) for t in grid
               if constraints.cover(gross[q][t], cross[q][t], cfg) < constraints.floor(q, t, cfg))


def audit(sched: pd.DataFrame, cfg: dict, agents: list[Agent]) -> dict[str, int]:
    """Count violations of the service's standard rules per agent."""
    by_id = {a.agent_id: a for a in agents}
    z = ZoneInfo(cfg["tz"])
    v = {"weekly_hours": 0, "consecutive_days": 0, "skill_match": 0, "no_overlap": 0}
    for aid, g in sched.groupby("agent_id"):
        a = by_id.get(aid)
        g = g.sort_values("segment_start_utc")
        hours = ((g["segment_end_utc"] - g["segment_start_utc"]).dt.total_seconds() / 3600).sum()
        if a is None or hours > cfg["weekly_hours"][a.contract] + 1e-9:
            v["weekly_hours"] += 1
        if a is not None and any(q not in a.skills for q in g["queue"]):
            v["skill_match"] += 1
        ends = g["segment_end_utc"].shift(1)
        if (g["segment_start_utc"] < ends).any():
            v["no_overlap"] += 1
        days = sorted({t.astimezone(z).date() for t in g["segment_start_utc"]})
        run = 1
        for d1, d2 in zip(days, days[1:]):
            run = run + 1 if (d2 - d1).days == 1 else 1
            if run > cfg["max_consecutive_days"]:
                v["consecutive_days"] += 1
                break
    return v
