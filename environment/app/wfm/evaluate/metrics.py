"""Evaluate a schedule.csv against the required curve: attainment, hours, constraint audit.

A convenience for engineers. Contractual evaluation is performed independently against each
client's SOW.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
from zoneinfo import ZoneInfo

import pandas as pd

from wfm.roster import Agent


def _parse(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for c in ("segment_start_utc", "segment_end_utc", "break_start_utc"):
        df[c] = pd.to_datetime(df[c], utc=True)
    df["break_minutes"] = df["break_minutes"].fillna(0).astype(int)
    return df


def coverage(sched: pd.DataFrame, grid, grain_min: int) -> tuple[dict, dict]:
    """Per queue per interval: gross agents on queue, and agents on break (overlapping the slot)."""
    gross = defaultdict(lambda: defaultdict(int))
    on_break = defaultdict(lambda: defaultdict(int))
    step = timedelta(minutes=grain_min)
    for r in sched.itertuples(index=False):
        for t in grid:
            if r.segment_start_utc <= t < r.segment_end_utc:
                gross[r.queue][t] += 1
                if r.break_minutes and r.break_start_utc < t + step and t < r.break_start_utc + timedelta(minutes=int(r.break_minutes)):
                    on_break[r.queue][t] += 1
    return gross, on_break


def evaluate(req: pd.DataFrame, sched: pd.DataFrame, cfg: dict, agents: list[Agent], week: str) -> dict:
    sched = _parse(sched)
    grain = cfg["interval_minutes"]
    grid = sorted(set(req["interval_start_utc"]))
    gross, on_break = coverage(sched, grid, grain)
    h = grain / 60.0

    sla, under, over = {}, 0.0, 0.0
    for q, g in req.groupby("queue"):
        met = tot = 0
        for r in g.itertuples(index=False):
            if r.volume <= 0:
                continue
            tot += 1
            scheduled = gross[q][r.interval_start_utc] - on_break[q][r.interval_start_utc]
            if scheduled >= r.required:
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
        "violations": audit(sched, cfg, agents),
    }


def audit(sched: pd.DataFrame, cfg: dict, agents: list[Agent]) -> dict[str, int]:
    """Count violations of the service's standard rules per agent."""
    by_id = {a.agent_id: a for a in agents}
    z = ZoneInfo(cfg["tz"])
    v = {"weekly_hours": 0, "consecutive_days": 0, "skill_match": 0, "no_overlap": 0}
    min_rest = float(cfg.get("min_rest_hours", 0))
    split_policy = str(cfg.get("split_shifts", "all"))
    if min_rest:
        v["rest11h"] = 0
    if split_policy != "all":
        v["split_pt_only"] = 0
    for aid, g in sched.groupby("agent_id"):
        if min_rest or split_policy != "all":
            # a shift = an agent's segments on one local day
            by_day = g.assign(_day=[t.astimezone(z).date() for t in g["segment_start_utc"]]).groupby("_day")
            shifts = [(d, s["segment_start_utc"].min(), s["segment_end_utc"].max(), len(s)) for d, s in by_day]
            shifts.sort(key=lambda x: x[1])
            if min_rest:
                v["rest11h"] += sum(1 for p, n in zip(shifts, shifts[1:])
                                    if (n[1] - p[2]).total_seconds() / 3600 < min_rest - 1e-9)
            if split_policy != "all":
                a = by_id.get(aid)
                v["split_pt_only"] += sum(1 for s in shifts if s[3] > 1 and (a is None or a.contract != split_policy))
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
