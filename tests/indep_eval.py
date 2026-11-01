"""Independent evaluator used by the grader. Never imports from /app and never reads /app/configs.

Own Erlang C (tests/erlang_c.py, a byte-identical copy of the reference maths), own canonical
loader (Northwind exports converted with the explicit utc_offset), own week grids from the ISO week
in the client's timezone, SOW targets hard-coded. Coverage is computed from schedule.csv alone.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from erlang_c import required_agents

QUEUES = ("priority", "standard")

# The contracts. Targets are the SOW's, not the config files'.
SOW = {
    "northwind": {"tz": "America/Chicago", "grain": 30, "hours": (6, 24), "cap": 0.85,
                  "sla": {"priority": (0.90, 30), "standard": (0.80, 20)},
                  "rules": ["rest11h", "split_pt_only", "break_window_max_surplus", "weekly_hours",
                            "consecutive_days", "skill_match", "no_overlap", "coverage_sane"]},
    "contoso": {"tz": "UTC", "grain": 15, "hours": (6, 24), "cap": 0.85,
                "sla": {"priority": (0.80, 20), "standard": (0.80, 20)},
                "rules": ["weekly_hours", "consecutive_days", "skill_match", "no_overlap", "coverage_sane"]},
    "fabrikam": {"tz": "America/New_York", "grain": 60, "hours": (6, 24), "cap": 0.85,
                 "sla": {"priority": (0.80, 20), "standard": (0.80, 20)},
                 "rules": ["weekly_hours", "consecutive_days", "skill_match", "no_overlap", "coverage_sane"]},
}
WEEKLY_HOURS = {"FT": 40.0, "PT": 24.0}
MAX_CONSECUTIVE_DAYS = 5
REST_HOURS = 11.0
BREAK_MIN_SHIFT_H, BREAK_MINUTES, BREAK_WINDOW_H = 6.0, 20, (2.0, 5.0)
UTC = timezone.utc


# ----------------------------------------------------------------------------- calendar / demand
def iso_week_monday(week: str) -> date:
    y, w = week.split("-W")
    return date.fromisocalendar(int(y), int(w), 1)


def week_grid(week: str, tz: str, grain: int) -> list[datetime]:
    """UTC slot starts from local Monday 00:00 to the next local Monday 00:00; DST changes the count."""
    z = ZoneInfo(tz)
    mon = iso_week_monday(week)
    start = datetime(mon.year, mon.month, mon.day, tzinfo=z).astimezone(UTC)
    end = (datetime(mon.year, mon.month, mon.day, tzinfo=z) + timedelta(days=7)).astimezone(UTC)
    n = int((end - start) / timedelta(minutes=grain))
    return [start + timedelta(minutes=grain * i) for i in range(n)]


def _parse_utc(s: str) -> datetime:
    return datetime.strptime(s.strip(), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)


def load_demand(client: str, data_path: Path, grid: list[datetime]) -> dict[str, dict[datetime, tuple[float, float]]]:
    """{queue: {slot: (volume, aht)}} on the grader's grid. Slots absent from the file carry zero volume."""
    demand = {q: {t: (0.0, 0.0) for t in grid} for q in QUEUES}
    step = grid[1] - grid[0]
    with data_path.open() as f:
        for r in csv.DictReader(f):
            if "interval_start_utc" in r:
                t = _parse_utc(r["interval_start_utc"])
            else:  # Northwind export: local wall-clock + explicit offset (authoritative)
                t = datetime.fromisoformat(f"{r['interval_start_local'].strip()}{r['utc_offset'].strip()}").astimezone(UTC)
            t = grid[0] + ((t - grid[0]) // step) * step   # a row belongs to the planning interval that contains it
            q = r["queue"].strip()
            if q in demand and t in demand[q]:
                demand[q][t] = (float(r["volume"]), float(r["aht_sec"]))
    return demand


def required_curve(demand, sow) -> dict[str, dict[datetime, int]]:
    sec = sow["grain"] * 60
    return {q: {t: required_agents(v, sec, a, sow["sla"][q][0], sow["sla"][q][1], sow["cap"])
                for t, (v, a) in demand[q].items()} for q in QUEUES}


# ----------------------------------------------------------------------------- schedule
class Segment:
    __slots__ = ("agent", "queue", "start", "end", "template", "idx", "break_start", "break_minutes", "row")

    def __init__(self, r: dict, row: int):
        self.agent = r["agent_id"].strip()
        self.queue = r["queue"].strip()
        self.start = _parse_utc(r["segment_start_utc"])
        self.end = _parse_utc(r["segment_end_utc"])
        self.template = r.get("template_id", "")
        self.idx = int(r.get("segment_idx") or 0)
        bs = (r.get("break_start_utc") or "").strip()
        self.break_start = _parse_utc(bs) if bs else None
        self.break_minutes = int(float(r.get("break_minutes") or 0))
        self.row = row

    @property
    def hours(self) -> float:
        return (self.end - self.start).total_seconds() / 3600.0


def load_schedule(path: Path) -> list[Segment]:
    with path.open() as f:
        rows = list(csv.DictReader(f))
    need = {"agent_id", "queue", "segment_start_utc", "segment_end_utc", "break_start_utc", "break_minutes"}
    if rows and not need <= set(rows[0].keys()):
        raise ValueError(f"schedule.csv missing columns: {sorted(need - set(rows[0].keys()))}")
    return [Segment(r, i + 2) for i, r in enumerate(rows)]


def load_agents(path: Path) -> dict[str, tuple[str, frozenset[str]]]:
    with path.open() as f:
        return {r["agent_id"].strip(): (r["contract"].strip(), frozenset(r["skills"].strip().split(";")))
                for r in csv.DictReader(f)}


def coverage(segments: list[Segment], grid: list[datetime], grain: int):
    """gross[q][t] = agents on queue whose segment covers t (ignoring breaks); on_break[q][t] likewise."""
    gross = {q: defaultdict(int) for q in QUEUES}
    on_break = {q: defaultdict(int) for q in QUEUES}
    step = timedelta(minutes=grain)
    index = {t: i for i, t in enumerate(grid)}
    for s in segments:
        if s.queue not in gross:
            continue
        # slots within [start, end) that lie on the grid
        t = s.start
        while t < s.end:
            if t in index:
                gross[s.queue][t] += 1
                if s.break_start is not None and s.break_minutes > 0:
                    if s.break_start < t + step and t < s.break_start + timedelta(minutes=s.break_minutes):
                        on_break[s.queue][t] += 1
            t += step
    return gross, on_break


def _shifts(segments: list[Segment], tz: str) -> dict[tuple[str, date], list[Segment]]:
    """A shift = all of an agent's segments on one local day."""
    z = ZoneInfo(tz)
    out: dict[tuple[str, date], list[Segment]] = defaultdict(list)
    for s in segments:
        out[(s.agent, s.start.astimezone(z).date())].append(s)
    for k in out:
        out[k].sort(key=lambda s: s.start)
    return out


# ----------------------------------------------------------------------------- evaluation
def evaluate(client: str, week: str, schedule_path: Path, data_path: Path, agents_path: Path) -> dict:
    sow = SOW[client]
    grid = week_grid(week, sow["tz"], sow["grain"])
    demand = load_demand(client, data_path, grid)
    required = required_curve(demand, sow)
    segments = load_schedule(schedule_path)
    agents = load_agents(agents_path)
    gross, on_break = coverage(segments, grid, sow["grain"])
    h = sow["grain"] / 60.0

    sla, under, over = {}, 0.0, 0.0
    for q in QUEUES:
        met = tot = 0
        for t in grid:
            if demand[q][t][0] <= 0:
                continue
            tot += 1
            sched = gross[q][t] - on_break[q][t]
            if sched >= required[q][t]:
                met += 1
            under += max(0, required[q][t] - sched) * h
            over += max(0, sched - required[q][t]) * h
        sla[q] = met / tot if tot else 1.0

    violations = audit(client, week, segments, agents, required, gross, grid)
    return {
        "client": client, "week": week, "intervals": len(grid),
        "sla": sla,
        "scheduled_hours": sum(s.hours for s in segments),
        "understaffed_interval_hours": under, "overstaffed_interval_hours": over,
        "agents_scheduled": len({s.agent for s in segments}),
        "segments": len(segments),
        "violations": {rule: violations.get(rule, []) for rule in sow["rules"]},
    }


def audit(client, week, segments, agents, required, gross, grid) -> dict[str, list[str]]:
    """{rule: [human-readable violations]} for every rule in the client's SOW."""
    sow = SOW[client]
    z = ZoneInfo(sow["tz"])
    grain = sow["grain"]
    step = timedelta(minutes=grain)
    slots = set(grid)
    week_start, week_end = grid[0], grid[-1] + step
    v: dict[str, list[str]] = defaultdict(list)
    by_agent: dict[str, list[Segment]] = defaultdict(list)
    for s in segments:
        by_agent[s.agent].append(s)

    # coverage_sane: on-grid, inside the week, inside operating hours, valid agent/queue, break inside segment
    open_h, close_h = sow["hours"]
    for s in segments:
        if s.agent not in agents:
            v["coverage_sane"].append(f"row {s.row}: unknown agent {s.agent}")
        if s.queue not in QUEUES:
            v["coverage_sane"].append(f"row {s.row}: unknown queue {s.queue}")
        if s.end <= s.start:
            v["coverage_sane"].append(f"row {s.row}: empty or reversed segment")
        if s.start not in slots or not (week_start <= s.start and s.end <= week_end) or (s.end - s.start) % step:
            v["coverage_sane"].append(f"row {s.row}: segment {s.start:%Y-%m-%dT%H:%MZ}-{s.end:%Y-%m-%dT%H:%MZ} off the week grid")
        ls, le = s.start.astimezone(z), (s.end - timedelta(minutes=1)).astimezone(z)
        if ls.hour + ls.minute / 60 < open_h or le.hour + (le.minute + 1) / 60 > close_h or ls.date() != le.date():
            v["coverage_sane"].append(f"row {s.row}: segment outside operating hours {open_h:02d}:00-{close_h:02d}:00 local")
        if s.break_start is not None or s.break_minutes:
            if s.break_start is None or s.break_minutes != BREAK_MINUTES:
                v["coverage_sane"].append(f"row {s.row}: break must be {BREAK_MINUTES} min with a start time")
            elif not (s.start <= s.break_start and s.break_start + timedelta(minutes=s.break_minutes) <= s.end) or s.break_start not in slots:
                v["coverage_sane"].append(f"row {s.row}: break {s.break_start:%Y-%m-%dT%H:%MZ} not on the grid inside its segment")

    for aid, segs in by_agent.items():
        segs.sort(key=lambda s: (s.start, s.end))
        contract, skills = agents.get(aid, ("FT", frozenset()))
        hours = sum(s.hours for s in segs)
        if hours > WEEKLY_HOURS[contract] + 1e-9:
            v["weekly_hours"].append(f"{aid} ({contract}): {hours:.1f} h > {WEEKLY_HOURS[contract]:.0f} h")
        for q in sorted({s.queue for s in segs}):
            if q not in skills:
                v["skill_match"].append(f"{aid}: scheduled on {q} without the skill")
        for a, b in zip(segs, segs[1:]):
            if b.start < a.end:
                v["no_overlap"].append(f"{aid}: rows {a.row} and {b.row} overlap")
        days = sorted({s.start.astimezone(z).date() for s in segs})
        run = 1
        for d1, d2 in zip(days, days[1:]):
            run = run + 1 if (d2 - d1).days == 1 else 1
            if run > MAX_CONSECUTIVE_DAYS:
                v["consecutive_days"].append(f"{aid}: {run} consecutive days ending {d2}")
                break

    shifts = _shifts(segments, sow["tz"])
    per_agent_shifts: dict[str, list[list[Segment]]] = defaultdict(list)
    for (aid, day), segs in sorted(shifts.items(), key=lambda kv: (kv[0][0], kv[1][0].start)):
        per_agent_shifts[aid].append(segs)
        contract = agents.get(aid, ("FT", frozenset()))[0]
        # split_pt_only
        if len(segs) > 1 and contract != "PT":
            v["split_pt_only"].append(f"{aid} ({contract}): {len(segs)} segments on {day}")
        # break_window_max_surplus
        length = sum(s.hours for s in segs)
        if length >= BREAK_MIN_SHIFT_H:
            breaks = [s for s in segs if s.break_start is not None and s.break_minutes]
            start = segs[0].start
            if len(breaks) != 1:
                v["break_window_max_surplus"].append(f"{aid} {day}: {len(breaks)} breaks on a {length:.0f} h shift")
                continue
            b = breaks[0]
            lo, hi = start + timedelta(hours=BREAK_WINDOW_H[0]), start + timedelta(hours=BREAK_WINDOW_H[1])
            if not (lo <= b.break_start <= hi):
                v["break_window_max_surplus"].append(f"{aid} {day}: break at {b.break_start:%H:%MZ} outside [{lo:%H:%MZ}, {hi:%H:%MZ}]")
                continue
            q = b.queue
            window = [t for s in segs for t in grid if s.start <= t < s.end and lo <= t <= hi]
            if not window or b.break_start not in window:
                v["break_window_max_surplus"].append(f"{aid} {day}: break slot not inside the shift's window")
                continue
            surplus = {t: gross[q][t] - required[q][t] for t in window}
            best = max(surplus.values())
            if surplus[b.break_start] != best:
                v["break_window_max_surplus"].append(
                    f"{aid} {day}: break at {b.break_start:%H:%MZ} surplus {surplus[b.break_start]} < max {best}")

    # rest11h: consecutive shifts (by local day) of one agent, elapsed gap between last end and next start
    for aid, lst in per_agent_shifts.items():
        lst.sort(key=lambda segs: segs[0].start)
        for a, b in zip(lst, lst[1:]):
            gap = (b[0].start - a[-1].end).total_seconds() / 3600.0
            if gap < REST_HOURS - 1e-9:
                v["rest11h"].append(f"{aid}: {a[-1].end:%a %H:%MZ} -> {b[0].start:%a %H:%MZ} = {gap:.1f} h")
    return dict(v)


if __name__ == "__main__":  # ad-hoc use: python indep_eval.py <client> <week> <schedule.csv> <demand.csv> <agents.csv>
    import json
    import sys
    c, w, s, d, a = sys.argv[1:6]
    print(json.dumps(evaluate(c, w, Path(s), Path(d), Path(a)), indent=2, default=str))
