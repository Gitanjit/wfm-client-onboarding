"""Sizing simulation for the WFM task design. Run before building the system.

Answers four questions with numbers:
  Q1  Does ISO 2026-W44 in America/Chicago contain the fall-back, and how many 30-min UTC intervals?
  Q2  Does the planted defect (weekly-mean AHT instead of per-interval AHT) produce SLA misses
      concentrated at peaks, under the SOW targets?
  Q3  Can Northwind's roster (32 FT x 40h + 8 PT x 24h = 1472 h) cover the required curve?
  Q4  If an agent fixes the defect for Contoso too, how much do Contoso's required hours rise?
      (sizes the +15% regression cost tolerance)

Pure numpy + stdlib. Deterministic.
"""
from __future__ import annotations

import math
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "wfm"))
from erlang import required_agents, service_level, traffic_intensity  # noqa: E402

# ---------------------------------------------------------------- Q1: calendar / DST
CHI = ZoneInfo("America/Chicago")

def iso_week_monday(year: int, week: int) -> datetime:
    jan4 = datetime(year, 1, 4)
    return (jan4 - timedelta(days=jan4.isoweekday() - 1) + timedelta(weeks=week - 1))

def week_intervals_utc(year, week, tz, grain_min):
    """UTC interval starts covering local Monday 00:00 -> next Monday 00:00 in tz."""
    mon = iso_week_monday(year, week)
    start_local = datetime(mon.year, mon.month, mon.day, tzinfo=tz)
    end_local = start_local + timedelta(days=7)
    start_utc = start_local.astimezone(timezone.utc)
    end_utc = end_local.astimezone(timezone.utc)
    n = int((end_utc - start_utc) / timedelta(minutes=grain_min))
    return [start_utc + timedelta(minutes=grain_min * i) for i in range(n)]

w44 = week_intervals_utc(2026, 44, CHI, 30)
w45 = week_intervals_utc(2026, 45, CHI, 30)
print(f"Q1  W44 Monday = {iso_week_monday(2026, 44).date()}  intervals(30m, Chicago) = {len(w44)}")
print(f"    W45 Monday = {iso_week_monday(2026, 45).date()}  intervals(30m, Chicago) = {len(w45)}")
dup = {}
for t in w44:
    loc = t.astimezone(CHI)
    key = loc.strftime("%Y-%m-%d %H:%M")
    dup.setdefault(key, []).append(loc.strftime("%z"))
ambiguous = {k: v for k, v in dup.items() if len(v) > 1}
print(f"    ambiguous local labels in W44: {ambiguous}")
assert len(w44) == 338 and len(w45) == 336, "calendar assumption wrong"

# ---------------------------------------------------------------- demand generator (spec 03 §7)
def hour_profile(h: float) -> float:
    g = lambda mu: math.exp(-0.5 * ((h - mu) / 1.5) ** 2)
    return 0.15 + g(10.0) + g(15.0)

WEEKDAY = [1.10, 1.05, 1.00, 1.00, 0.95, 0.55, 0.45]
BASE_DAILY = {"priority": 1400.0, "standard": 3200.0}
AHT_BASE = {"priority": 420.0, "standard": 300.0}
OPEN, CLOSE = 6, 24  # local operating hours

def generate(intervals_utc, tz, grain_min, scale, seed, peak_inflation=0.35):
    rng = np.random.default_rng(seed)
    rows = []
    # normalise hour profile over operating hours per day
    norm = sum(hour_profile(h) for h in np.arange(OPEN, CLOSE, grain_min / 60))
    for t in intervals_utc:
        loc = t.astimezone(tz)
        h = loc.hour + loc.minute / 60
        for q in ("priority", "standard"):
            if OPEN <= h < CLOSE:
                vol = BASE_DAILY[q] * scale * WEEKDAY[loc.weekday()] * hour_profile(h) / norm
                vol *= rng.lognormal(0, 0.12)
                near_peak = min(abs(h - 10), abs(h - 15))
                infl = peak_inflation * max(0.0, 1 - near_peak / 1.0)
                aht = AHT_BASE[q] * (1 + infl) * rng.lognormal(0, 0.05)
            else:
                vol, aht = 0.0, AHT_BASE[q]
            rows.append((t, q, vol, aht))
    return rows

SOW = {"northwind": {"priority": (0.90, 30), "standard": (0.80, 20)},
       "contoso":   {"priority": (0.80, 20), "standard": (0.80, 20)}}

def required_curve(rows, targets, grain_min, cap, use_mean_aht: bool):
    by_q = {}
    for t, q, vol, aht in rows:
        by_q.setdefault(q, []).append((t, vol, aht))
    out = {}
    for q, lst in by_q.items():
        sl, tsec = targets[q]
        mean_aht = float(np.mean([a for _, v, a in lst if v > 0]))
        out[q] = [(t, vol, aht,
                   required_agents(vol, grain_min * 60, mean_aht if use_mean_aht else aht, sl, tsec, cap))
                  for t, vol, aht in lst]
    return out

def sla_if_staffed_with(curve_buggy, curve_fixed, grain_min, targets):
    """Staff with the buggy headcount; evaluate true SL with the real per-interval AHT."""
    res = {}
    for q in curve_fixed:
        sl_t, tsec = targets[q]
        misses, total, peak_misses = 0, 0, 0
        for (t, vol, aht, n_fix), (_, _, _, n_bug) in zip(curve_fixed[q], curve_buggy[q]):
            if vol <= 0:
                continue
            total += 1
            a = traffic_intensity(vol, grain_min * 60, aht)
            if service_level(a, n_bug, aht, tsec) < sl_t:
                misses += 1
                h = t.astimezone(CHI).hour + t.astimezone(CHI).minute / 60
                if min(abs(h - 10), abs(h - 15)) <= 1.0:
                    peak_misses += 1
        res[q] = (misses, total, peak_misses)
    return res

# ---------------------------------------------------------------- Q2: defect bites?
rows = generate(w44, CHI, 30, scale=0.10, seed=244)
fixed = required_curve(rows, SOW["northwind"], 30, 0.85, use_mean_aht=False)
buggy = required_curve(rows, SOW["northwind"], 30, None, use_mean_aht=True)  # D1 + D2 both present
r = sla_if_staffed_with(buggy, fixed, 30, SOW["northwind"])
print("\nQ2  Northwind W44, staffed with buggy headcount, evaluated with true AHT:")
for q, (m, tot, pk) in r.items():
    print(f"    {q:9s} misses {m:3d}/{tot} operating intervals ({m/tot:.1%}); {pk} of them within 1h of a peak")
hrs_fix = {q: sum(n for *_, n in v) * 0.5 for q, v in fixed.items()}
hrs_bug = {q: sum(n for *_, n in v) * 0.5 for q, v in buggy.items()}
print(f"    required agent-hours fixed={sum(hrs_fix.values()):.0f}  buggy={sum(hrs_bug.values()):.0f}  "
      f"delta={sum(hrs_fix.values())/sum(hrs_bug.values())-1:+.1%}")

# ---------------------------------------------------------------- Q3: roster feasibility
roster_hours = 32 * 40 + 8 * 24
peak_req = max(sum(curve[i][3] for curve in fixed.values()) for i in range(len(w44)))
print(f"\nQ3  roster hours available = {roster_hours}; required agent-hours (fixed) = {sum(hrs_fix.values()):.0f} "
      f"-> utilisation {sum(hrs_fix.values())/roster_hours:.0%}; peak concurrent required = {peak_req} of 40 agents")
print("    rule of thumb: shift granularity wastes ~20-30%, so target required <= 70% of roster hours")

# ---------------------------------------------------------------- Q4: regression tolerance
UTC = timezone.utc
w44c = week_intervals_utc(2026, 44, UTC, 15)
rows_c = generate(w44c, UTC, 15, scale=0.10, seed=44)
fix_c = required_curve(rows_c, SOW["contoso"], 15, 0.85, use_mean_aht=False)
bug_c = required_curve(rows_c, SOW["contoso"], 15, None, use_mean_aht=True)
hf = sum(sum(n for *_, n in v) for v in fix_c.values()) * 0.25
hb = sum(sum(n for *_, n in v) for v in bug_c.values()) * 0.25
print(f"\nQ4  Contoso W44 required hours: buggy={hb:.0f} fixed={hf:.0f} -> fixing raises required hours by {hf/hb-1:+.1%}")
print("    (scheduled hours move less than required hours because shifts already overcover troughs)")
