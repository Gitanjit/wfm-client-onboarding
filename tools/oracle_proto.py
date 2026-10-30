"""Prototype of the week-aware greedy scheduler (the ORACLE's algorithm) against simulated demand.

Purpose: before building the real system, prove that a greedy reference can
  (a) reach >= 0.95 SLA attainment on both Northwind queues with the 40-agent roster,
  (b) satisfy R1 (11h rest across days), R2 (split PT-only), R3 (break at max gross surplus),
      weekly-hour caps, <=5 consecutive days, skill match, no overlap,
  (c) do so deterministically.
Also reports what the BASELINE (per-day, midpoint breaks, split-for-all, buggy staffing) attains,
so the gap the agent must close is known in advance.

Run from scaffolds/:  python tools/oracle_proto.py
"""
from __future__ import annotations

import io
import contextlib
import math
import sys
import types
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "wfm"))
from erlang import service_level, traffic_intensity  # noqa: E402

# ---- reuse the demand model from sizing_sim.py (everything before its Q2 section)
src = (HERE / "sizing_sim.py").read_text()
sim = types.ModuleType("sim"); sim.__dict__["__file__"] = str(HERE / "sizing_sim.py")
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(src.split("# ---------------------------------------------------------------- Q2")[0], "sim", "exec"), sim.__dict__)

CHI = ZoneInfo("America/Chicago")
GRAIN = 30
H = GRAIN / 60.0
SOW = {"priority": (0.90, 30), "standard": (0.80, 20)}
CAP = 0.85
OPEN, CLOSE = 6, 24

# Templates: local wall-clock, (start_h, end_h) segments; none crosses midnight
TEMPLATES = {
    "E8": [(6, 14)], "D8": [(9, 17)], "L8": [(13, 21)], "N8": [(16, 24)],
    "P6a": [(7, 13)], "P6b": [(15, 21)], "P4": [(10, 14)],
    "S44": [(8, 12), (16, 20)],
}
SPLIT = {"S44"}


def make_roster(n_ft=32, n_pt=8, seed=7):
    import random
    rnd = random.Random(seed)
    agents = []
    for i in range(n_ft + n_pt):
        contract = "PT" if i < n_pt else "FT"
        r = rnd.random()
        skills = {"priority", "standard"} if r < 0.30 else ({"priority"} if r < 0.58 else {"standard"})
        agents.append({"id": f"NW-{i+1:03d}", "contract": contract, "skills": skills,
                       "cap_h": 24 if contract == "PT" else 40})
    return agents


def build_required(intervals_utc, seed, buggy: bool):
    rows = sim.generate(intervals_utc, CHI, GRAIN, scale=0.10, seed=seed, peak_inflation=0.35)
    curve = sim.required_curve(rows, SOW, GRAIN, None if buggy else CAP, use_mean_aht=buggy)
    # req[q][utc] = (vol, aht, n_required)
    req = {q: {t: (vol, aht, n) for (t, vol, aht, n) in lst} for q, lst in curve.items()}
    return req


def local_day(t_utc):
    return t_utc.astimezone(CHI).date()


def shift_segments_utc(day, template):
    """Local wall-clock -> UTC datetimes for a given local date."""
    segs = []
    for s_h, e_h in TEMPLATES[template]:
        s = datetime(day.year, day.month, day.day, s_h, 0, tzinfo=CHI)
        e = datetime(day.year, day.month, day.day, 0, 0, tzinfo=CHI) + timedelta(hours=e_h)
        segs.append((s.astimezone(timezone.utc), e.astimezone(timezone.utc)))
    return segs


def intervals_in(seg, grid):
    s, e = seg
    return [t for t in grid if s <= t < e]


def schedule_week(req, grid, agents, *, week_aware: bool, split_pt_only: bool, break_rule: str):
    """Greedy. Returns list of shifts: dict(agent, template, day, segs=[(s,e)], queue, break=(start,20)|None)."""
    cover = {q: defaultdict(int) for q in req}           # gross coverage per queue per interval
    shifts = []
    hours = defaultdict(float)
    last_end = {}                                        # agent -> last shift end (UTC)
    days_worked = defaultdict(list)
    days = sorted({local_day(t) for t in grid})
    grid_set = set(grid)

    def deficit(q, t):
        return req[q][t][2] - cover[q][t]

    for day in days:
        day_grid = [t for t in grid if local_day(t) == day]
        dead = set()                                      # (tpl, q) with no eligible agent today
        while True:
            # choose (template, queue) with max positive deficit covered
            best, best_val = None, 0.0
            for tpl in TEMPLATES:
                segs = shift_segments_utc(day, tpl)
                ivs = [t for seg in segs for t in intervals_in(seg, day_grid)]
                for q in req:
                    if (tpl, q) in dead:
                        continue
                    val = sum(max(0, min(1, deficit(q, t))) for t in ivs)
                    if val > best_val + 1e-9:
                        best, best_val = (tpl, q, segs, ivs), val
            if best is None or best_val < 1.0:           # nothing left worth a shift
                break
            tpl, q, segs, ivs = best
            length = sum((e - s).total_seconds() / 3600 for s, e in segs)
            # candidate agents
            cands = []
            for a in agents:
                if q not in a["skills"]:
                    continue
                if split_pt_only and tpl in SPLIT and a["contract"] != "PT":
                    continue
                if hours[a["id"]] + length > a["cap_h"] + 1e-9:
                    continue
                if any(sh["agent"] == a["id"] and sh["day"] == day for sh in shifts):
                    continue                              # one shift per agent per day
                if week_aware:
                    le = last_end.get(a["id"])
                    if le is not None and (segs[0][0] - le) < timedelta(hours=11):
                        continue
                    dw = days_worked[a["id"]]
                    if len(dw) >= 5 and all((day - dw[-k]).days == k for k in range(1, 6)):
                        continue                          # would be 6th consecutive day
                cands.append(a)
            if not cands:
                dead.add((tpl, q))
                continue
            a = min(cands, key=lambda x: (hours[x["id"]], x["id"]))
            shifts.append({"agent": a["id"], "template": tpl, "day": day, "segs": segs, "queue": q,
                           "contract": a["contract"], "break": None, "ivs": ivs})
            hours[a["id"]] += length
            last_end[a["id"]] = segs[-1][1]
            days_worked[a["id"]].append(day)
            for t in ivs:
                cover[q][t] += 1

    # breaks
    for sh in shifts:
        length = sum((e - s).total_seconds() / 3600 for s, e in sh["segs"])
        if length < 6:
            continue
        start = sh["segs"][0][0]
        window = [t for t in sh["ivs"] if timedelta(hours=2) <= (t - start) <= timedelta(hours=5)]
        if not window:
            continue
        if break_rule == "midpoint":
            mid = start + timedelta(hours=length / 2)
            t_b = min(sh["ivs"], key=lambda t: abs((t - mid).total_seconds()))
        else:  # max gross surplus on the agent's queue; ties -> earliest
            q = sh["queue"]
            t_b = max(window, key=lambda t: (cover[q][t] - req[q][t][2], -t.timestamp()))
        sh["break"] = (t_b, 20)
    return shifts, cover, hours


def evaluate(req, grid, shifts, cover):
    """Independent-evaluator semantics: on-queue = gross cover minus agents on break in that interval."""
    on_break = {q: defaultdict(int) for q in req}
    for sh in shifts:
        if sh["break"]:
            on_break[sh["queue"]][sh["break"][0]] += 1   # 20-min break inside one 30-min slot
    out = {}
    for q in req:
        meet = tot = 0
        under = 0.0
        for t, (vol, aht, n_req) in req[q].items():
            if vol <= 0:
                continue
            tot += 1
            sched = cover[q][t] - on_break[q][t]
            if sched >= n_req:
                meet += 1
            else:
                under += (n_req - sched) * H
        out[q] = {"attainment": meet / tot, "understaffed_h": under}
    hours = sum(sum((e - s).total_seconds() / 3600 for s, e in sh["segs"]) for sh in shifts)
    return out, hours


def audit(shifts, agents_by_id):
    viol = defaultdict(int)
    by_agent = defaultdict(list)
    for sh in shifts:
        by_agent[sh["agent"]].append(sh)
    for aid, lst in by_agent.items():
        lst.sort(key=lambda s: s["segs"][0][0])
        for a, b in zip(lst, lst[1:]):
            if b["segs"][0][0] - a["segs"][-1][1] < timedelta(hours=11):
                viol["R1_rest"] += 1
        if sum(sum((e - s).total_seconds() / 3600 for s, e in s_["segs"]) for s_ in lst) > agents_by_id[aid]["cap_h"] + 1e-9:
            viol["hours"] += 1
        days = sorted({s_["day"] for s_ in lst})
        run = 1
        for d1, d2 in zip(days, days[1:]):
            run = run + 1 if (d2 - d1).days == 1 else 1
            if run > 5:
                viol["consecutive"] += 1
        for s_ in lst:
            if s_["template"] in SPLIT and s_["contract"] != "PT":
                viol["R2_split"] += 1
            if s_["queue"] not in agents_by_id[aid]["skills"]:
                viol["skill"] += 1
    return dict(viol)


def run(label, req_for_sched, req_true, grid, agents, **kw):
    shifts, cover, hours = schedule_week(req_for_sched, grid, agents, **kw)
    # evaluate against the TRUE requirement (the grader's view)
    cover_true = cover
    res, sched_h = evaluate(req_true, grid, shifts, cover_true)
    v = audit(shifts, {a["id"]: a for a in agents})
    print(f"{label:34s} prio {res['priority']['attainment']:.3f}  std {res['standard']['attainment']:.3f}  "
          f"under_h {res['priority']['understaffed_h']+res['standard']['understaffed_h']:6.1f}  "
          f"sched_h {sched_h:6.0f}  shifts {len(shifts):3d}  violations {v or 'none'}")
    return res, sched_h, v


if __name__ == "__main__":
    agents = make_roster()
    for week, seed in [(44, 244), (45, 245)]:
        grid = sim.week_intervals_utc(2026, week, CHI, GRAIN)
        req_true = build_required(grid, seed, buggy=False)
        req_bug = build_required(grid, seed, buggy=True)
        print(f"\n=== Northwind 2026-W{week}: {len(grid)} intervals ===")
        run("BASELINE (buggy req, per-day, midpoint)", req_bug, req_true, grid, agents,
            week_aware=False, split_pt_only=False, break_rule="midpoint")
        run("ORACLE (true req, week-aware, R2, R3)", req_true, req_true, grid, agents,
            week_aware=True, split_pt_only=True, break_rule="max_surplus")
        run("shallow: true req but per-day (no R1)", req_true, req_true, grid, agents,
            week_aware=False, split_pt_only=True, break_rule="max_surplus")
