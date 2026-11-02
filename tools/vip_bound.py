"""Upper bound on Northwind vip attainment for a VIP desk of N full-time agents (multi-v3 sizing).

For each local day, every multiset of FT templates (E8 D8 L8 N8 P6a P6b P4; S44 is PT-only) that keeps the
§2.6 floor (one agent on vip 06:00-24:00) is scored by the vip intervals with volume whose GROSS coverage
reaches the Erlang C requirement (tests/erlang_c.py, 90/20, cap 0.85, the interval's own AHT). A knapsack
over the seven days then spends the desk's weekly hours (40 x N) where they buy the most met intervals.

Every relaxation loosens the bound, so the result is a true ceiling: breaks are ignored (gross >= net),
rest, consecutive days and one-template-per-agent-per-day are dropped except "at most N shifts a day",
and hours are pooled across agents. If the ceiling is below 0.95, no schedule meets the SOW floor on vip.

    python tools/vip_bound.py <export.csv> <N> [<N> ...]
"""
from __future__ import annotations

import csv
import sys
from datetime import datetime
from itertools import combinations_with_replacement
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
from erlang_c import required_agents  # noqa: E402

TEMPLATES = {"E8": (6, 14), "D8": (9, 17), "L8": (13, 21), "N8": (16, 24), "P6a": (7, 13), "P6b": (15, 21), "P4": (10, 14)}
FLOOR_HOURS, VIP_HOURS = (6, 24), (8, 20)


def day_requirements(path: Path) -> dict:
    """{local date: {half-hour slot index from 00:00: required agents}} for vip rows with volume."""
    out: dict = {}
    for r in csv.DictReader(path.open()):
        if r["queue"] != "vip":
            continue
        loc = datetime.fromisoformat(r["interval_start_local"].strip())
        day = out.setdefault(loc.date(), {})
        v, a = float(r["volume"]), float(r["aht_sec"])
        if v > 0:
            day[loc.hour * 2 + loc.minute // 30] = required_agents(v, 1800, a, 0.90, 20, 0.85)
    return out


def best_by_hours(req: dict, n: int) -> dict[int, int]:
    """{hours used: max met intervals} over floor-feasible template multisets of at most n shifts."""
    slots = {k: [s for s in range(2 * a, 2 * b)] for k, (a, b) in TEMPLATES.items()}
    floor_slots = range(2 * FLOOR_HOURS[0], 2 * FLOOR_HOURS[1])
    best: dict[int, int] = {}
    for size in range(1, n + 1):
        for combo in combinations_with_replacement(TEMPLATES, size):
            cov = [0] * 48
            for k in combo:
                for s in slots[k]:
                    cov[s] += 1
            if any(cov[s] < 1 for s in floor_slots):
                continue
            hours = sum(TEMPLATES[k][1] - TEMPLATES[k][0] for k in combo)
            met = sum(1 for s, r in req.items() if cov[s] >= r)
            if met > best.get(hours, -1):
                best[hours] = met
    return best


def ceiling(path: Path, n: int) -> tuple[float, int, int]:
    days = day_requirements(path)
    budget = 40 * n
    dp = {0: 0}                                  # hours spent -> met intervals so far
    for d in sorted(days):
        opts = best_by_hours(days[d], n)
        nxt: dict[int, int] = {}
        for h0, m0 in dp.items():
            for h, m in opts.items():
                if h0 + h <= budget and m0 + m > nxt.get(h0 + h, -1):
                    nxt[h0 + h] = m0 + m
        dp = nxt
    total = sum(len(r) for r in days.values())
    met = max(dp.values()) if dp else 0
    return met / total, met, total


if __name__ == "__main__":
    f = Path(sys.argv[1])
    for n in map(int, sys.argv[2:]):
        c, met, total = ceiling(f, n)
        print(f"{f.name}  desk {n:2d}: ceiling {c:.3f}  ({met}/{total} vip intervals)")
