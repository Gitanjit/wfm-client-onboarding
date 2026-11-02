"""Deterministic seed-data generator for the wfm-client-onboarding task.

Writes every data file the task uses (seen weeks into environment/app/data, held-out weeks into
tests/heldout) and a sha256 manifest. Running it twice yields byte-identical files.

    python tools/seedgen.py --app environment/app/data --heldout tests/heldout --manifest tools/data_manifest.txt

Demand model (03_TASK_DESIGN §7; identical draw order to tools/sizing_sim.py so the prototype numbers carry over):
  volume = base_daily[q] * scale * weekday[dow] * hour_profile(h) / norm * LogNormal(0, 0.12)
  aht    = aht_base[q] * (1 + 0.35 * max(0, 1 - dist_to_nearest_peak_h)) * LogNormal(0, 0.05)
Rows outside operating hours carry volume 0 and the base AHT; they are still present.
"""
from __future__ import annotations

import argparse
import hashlib
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

CLIENTS = {
    "contoso": dict(prefix="CO", grain=15, tz="UTC", scale=0.10, n_agents=40, n_pt=8, hours=(6, 24),
                    roster_seed=1, weeks={41: 41, 42: 42, 43: 43, 44: 44}, heldout=[44], fmt="canonical"),
    "fabrikam": dict(prefix="FA", grain=60, tz="America/New_York", scale=0.07, n_agents=28, n_pt=6, hours=(6, 24),
                     roster_seed=2, weeks={41: 141, 42: 142, 43: 143, 44: 144}, heldout=[44], fmt="canonical"),
    "northwind": dict(prefix="NW", grain=30, tz="America/Chicago", scale=0.10, n_agents=40, n_pt=8, hours=(6, 24),
                      roster_seed=7, weeks={42: 242, 43: 243, 44: 244, 45: 245, (2027, 10): 246},
                      heldout=[45, (2027, 10)], fmt="export"),
}
YEAR = 2026   # a week key is an ISO week number in YEAR, or (year, week); 2027-W10 holds the US spring-forward
WEEKDAY = [1.10, 1.05, 1.00, 1.00, 0.95, 0.55, 0.45]
BASE_DAILY = {"priority": 1400.0, "standard": 3200.0}
AHT_BASE = {"priority": 420.0, "standard": 300.0}
PEAK_INFLATION = 0.35
QUEUES = ("priority", "standard")
# Two rows of Northwind's W44 export whose local label was mis-typed by one minute at the client's end.
# utc_offset and row order are correct; the row still belongs to the 10:00 interval. Deterministic.
LABEL_TYPOS = {("northwind", 44, "2026-10-27 10:00", "priority"): "2026-10-27 10:01",
               ("northwind", 44, "2026-10-29 10:00", "standard"): "2026-10-29 10:01"}


def iso_week_monday(year: int, week: int) -> datetime:
    jan4 = datetime(year, 1, 4)
    return jan4 - timedelta(days=jan4.isoweekday() - 1) + timedelta(weeks=week - 1)


def week_intervals_utc(year: int, week: int, tz: ZoneInfo, grain_min: int) -> list[datetime]:
    """UTC interval starts covering local Monday 00:00 -> next local Monday 00:00 (DST-aware)."""
    mon = iso_week_monday(year, week)
    start_local = datetime(mon.year, mon.month, mon.day, tzinfo=tz)
    end_local = start_local + timedelta(days=7)
    start_utc = start_local.astimezone(timezone.utc)
    end_utc = end_local.astimezone(timezone.utc)
    n = int((end_utc - start_utc) / timedelta(minutes=grain_min))
    return [start_utc + timedelta(minutes=grain_min * i) for i in range(n)]


def hour_profile(h: float) -> float:
    g = lambda mu: math.exp(-0.5 * ((h - mu) / 1.5) ** 2)  # noqa: E731
    return 0.15 + g(10.0) + g(15.0)


def generate(intervals_utc, tz: ZoneInfo, grain_min: int, scale: float, seed: int, hours: tuple[int, int]):
    rng = np.random.default_rng(seed)
    open_h, close_h = hours
    norm = sum(hour_profile(h) for h in np.arange(open_h, close_h, grain_min / 60))
    rows = []
    for t in intervals_utc:
        loc = t.astimezone(tz)
        h = loc.hour + loc.minute / 60
        for q in QUEUES:
            if open_h <= h < close_h:
                vol = BASE_DAILY[q] * scale * WEEKDAY[loc.weekday()] * hour_profile(h) / norm
                vol *= rng.lognormal(0, 0.12)
                near_peak = min(abs(h - 10), abs(h - 15))
                infl = PEAK_INFLATION * max(0.0, 1 - near_peak / 1.0)
                aht = AHT_BASE[q] * (1 + infl) * rng.lognormal(0, 0.05)
            else:
                vol, aht = 0.0, AHT_BASE[q]
            rows.append((t, q, vol, aht))
    return rows


# Northwind's VIP line (multi-v3): contacts 08:00-20:00 local, its own random stream so that the
# priority and standard rows are byte-identical to the two-queue revisions.
VIP = dict(base_daily=1000.0, aht=540.0, hours=(8, 20), seed_offset=5000)
# VIP desk: agents appended after the generated roster (existing ids unchanged). FT unless noted.
VIP_ROSTER = [("NW-041", "FT", "vip"), ("NW-042", "FT", "vip"), ("NW-043", "FT", "vip"), ("NW-044", "FT", "vip"),
              ("NW-045", "FT", "priority;vip"), ("NW-046", "FT", "priority;vip"), ("NW-047", "FT", "priority;vip"),
              ("NW-048", "FT", "priority;vip"), ("NW-049", "FT", "vip"), ("NW-050", "FT", "vip"), ("NW-051", "FT", "vip"),
              ("NW-052", "FT", "vip")]


def add_vip(rows, tz: ZoneInfo, grain_min: int, seed: int, scale: float):
    """Insert a `vip` row after each interval's standard row."""
    rng = np.random.default_rng(seed + VIP["seed_offset"])
    a, b = VIP["hours"]
    norm = sum(hour_profile(h) for h in np.arange(a, b, grain_min / 60))
    out = []
    for r in rows:
        out.append(r)
        if r[1] != "standard":
            continue
        t = r[0]
        loc = t.astimezone(tz)
        h = loc.hour + loc.minute / 60
        if a <= h < b:
            vol = VIP["base_daily"] * scale * WEEKDAY[loc.weekday()] * hour_profile(h) / norm * rng.lognormal(0, 0.12)
            near_peak = min(abs(h - 10), abs(h - 15))
            aht = VIP["aht"] * (1 + PEAK_INFLATION * max(0.0, 1 - near_peak / 1.0)) * rng.lognormal(0, 0.05)
        else:
            vol, aht = 0.0, VIP["aht"]
        out.append((t, "vip", vol, aht))
    return out


def write_canonical(path: Path, client: str, grain: int, rows) -> None:
    lines = ["client,queue,interval_start_utc,interval_minutes,volume,aht_sec"]
    for t, q, vol, aht in rows:
        lines.append(f"{client},{q},{t.strftime('%Y-%m-%dT%H:%M:%SZ')},{grain},{vol:.3f},{aht:.3f}")
    path.write_text("\n".join(lines) + "\n")


def write_export(path: Path, tz: ZoneInfo, rows, client: str, week: int) -> None:
    """Northwind's own format: local wall-clock plus the explicit UTC offset in effect for the row."""
    lines = ["interval_start_local,utc_offset,queue,volume,aht_sec"]
    for t, q, vol, aht in rows:
        loc = t.astimezone(tz)
        z = loc.strftime("%z")  # e.g. -0500
        label = loc.strftime('%Y-%m-%d %H:%M')
        label = LABEL_TYPOS.get((client, week, label, q), label)
        lines.append(f"{label},{z[:3]}:{z[3:]},{q},{vol:.3f},{aht:.3f}")
    path.write_text("\n".join(lines) + "\n")


# Litware (step 2): 20-minute grain, Europe/London, three queues, an export stamped with the interval END.
LITWARE = dict(prefix="LW", grain=20, tz="Europe/London", scale=0.035, n_agents=24, n_pt=6, hours=(7, 21),
               queue_hours={"priority": (7, 21), "standard": (7, 21), "email": (7, 19)}, roster_seed=11,
               weeks={(2027, 10): 341, (2027, 11): 342, (2027, 12): 343}, heldout=[(2027, 12)])
BASE_DAILY_L = {"priority": 1400.0, "standard": 3200.0, "email": 900.0}
AHT_BASE_L = {"priority": 420.0, "standard": 300.0, "email": 360.0}
STEP2_NORTHWIND = {(2027, 10): 246, (2027, 11): 247}   # W10 is seen in step 2; W11 is step 2's held-out week


def generate_multi(intervals_utc, tz: ZoneInfo, grain_min: int, scale: float, seed: int, queue_hours: dict):
    """As generate(), with per-queue operating hours (rows outside a queue's hours carry volume 0)."""
    rng = np.random.default_rng(seed)
    rows = []
    norms = {q: sum(hour_profile(h) for h in np.arange(a, b, grain_min / 60)) for q, (a, b) in queue_hours.items()}
    for t in intervals_utc:
        loc = t.astimezone(tz)
        h = loc.hour + loc.minute / 60
        for q, (a, b) in queue_hours.items():
            if a <= h < b:
                vol = BASE_DAILY_L[q] * scale * WEEKDAY[loc.weekday()] * hour_profile(h) / norms[q] * rng.lognormal(0, 0.12)
                near_peak = min(abs(h - 10), abs(h - 15))
                aht = AHT_BASE_L[q] * (1 + PEAK_INFLATION * max(0.0, 1 - near_peak / 1.0)) * rng.lognormal(0, 0.05)
            else:
                vol, aht = 0.0, AHT_BASE_L[q]
            rows.append((t, q, vol, aht))
    return rows


def write_export_end(path: Path, tz: ZoneInfo, rows, grain: int) -> None:
    """Litware's format: the local wall-clock time at which the interval ENDS, with the offset in effect then."""
    lines = ["interval_end_local,utc_offset,queue,volume,aht_sec"]
    for t, q, vol, aht in rows:
        loc = (t + timedelta(minutes=grain)).astimezone(tz)
        z = loc.strftime("%z")
        lines.append(f"{loc.strftime('%Y-%m-%d %H:%M')},{z[:3]}:{z[3:]},{q},{vol:.3f},{aht:.3f}")
    path.write_text("\n".join(lines) + "\n")


def make_roster_litware(n_agents: int, n_pt: int, seed: int) -> list[tuple[str, str, str]]:
    rnd = random.Random(seed)
    mix = [(0.35, "priority;standard"), (0.55, "priority"), (0.70, "standard"), (0.85, "standard;email"), (1.0, "email")]
    out = []
    for i in range(n_agents):
        r = rnd.random()
        out.append((f"LW-{i + 1:03d}", "PT" if i < n_pt else "FT", next(s for c, s in mix if r < c)))
    return out


def make_roster(prefix: str, n_agents: int, n_pt: int, seed: int) -> list[tuple[str, str, str]]:
    """agent_id, contract, skills. 30% dual-skill, 28% priority-only, 42% standard-only; PT = first n_pt ids."""
    rnd = random.Random(seed)
    out = []
    for i in range(n_agents):
        contract = "PT" if i < n_pt else "FT"
        r = rnd.random()
        skills = "priority;standard" if r < 0.30 else ("priority" if r < 0.58 else "standard")
        out.append((f"{prefix}-{i + 1:03d}", contract, skills))
    return out


def write_roster(path: Path, roster) -> None:
    path.write_text("agent_id,contract,skills\n" + "".join(f"{a},{c},{s}\n" for a, c, s in roster))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", type=Path, required=True, help="environment/app/data")
    ap.add_argument("--heldout", type=Path, required=True, help="tests/heldout")
    ap.add_argument("--manifest", type=Path, required=True, help="tools/data_manifest.txt")
    ap.add_argument("--step2", type=Path, default=None, help="steps/litware-spring/workdir/data (multi-step only)")
    args = ap.parse_args()

    written: list[Path] = []
    for client, c in CLIENTS.items():
        tz = ZoneInfo(c["tz"])
        for key, seed in c["weeks"].items():
            year, week = key if isinstance(key, tuple) else (YEAR, key)
            grid = week_intervals_utc(year, week, tz, c["grain"])
            rows = generate(grid, tz, c["grain"], c["scale"], seed, c["hours"])
            if client == "northwind":
                rows = add_vip(rows, tz, c["grain"], seed, c["scale"])
            root = args.heldout if key in c["heldout"] else args.app
            if c["fmt"] == "canonical":
                path = root / client / f"week_{year}-W{week:02d}.csv"
                path.parent.mkdir(parents=True, exist_ok=True)
                write_canonical(path, client, c["grain"], rows)
            else:
                path = root / client / f"export_{year}-W{week:02d}.csv"
                path.parent.mkdir(parents=True, exist_ok=True)
                write_export(path, tz, rows, client, week)
            written.append(path)
            print(f"{path}  intervals={len(grid)}  seed={seed}")
        rpath = args.app / "agents" / f"{client}.csv"
        rpath.parent.mkdir(parents=True, exist_ok=True)
        roster = make_roster(c["prefix"], c["n_agents"], c["n_pt"], c["roster_seed"])
        write_roster(rpath, roster + (VIP_ROSTER if client == "northwind" else []))
        written.append(rpath)

    if args.step2:   # step 2 ("litware-spring"): seen files go to the step's workdir, held-out files to tests/heldout
        c = LITWARE
        tz = ZoneInfo(c["tz"])
        for (year, week), seed in c["weeks"].items():
            grid = week_intervals_utc(year, week, tz, c["grain"])
            rows = generate_multi(grid, tz, c["grain"], c["scale"], seed, c["queue_hours"])
            root = args.heldout if (year, week) in c["heldout"] else args.step2
            path = root / "litware" / f"export_{year}-W{week:02d}.csv"
            path.parent.mkdir(parents=True, exist_ok=True)
            write_export_end(path, tz, rows, c["grain"])
            written.append(path)
            print(f"{path}  intervals={len(grid)}  seed={seed}")
        rpath = args.step2 / "agents" / "litware.csv"
        rpath.parent.mkdir(parents=True, exist_ok=True)
        write_roster(rpath, make_roster_litware(c["n_agents"], c["n_pt"], c["roster_seed"]))
        written.append(rpath)
        nw = CLIENTS["northwind"]
        tz = ZoneInfo(nw["tz"])
        for (year, week), seed in STEP2_NORTHWIND.items():
            grid = week_intervals_utc(year, week, tz, nw["grain"])
            rows = add_vip(generate(grid, tz, nw["grain"], nw["scale"], seed, nw["hours"]), tz, nw["grain"], seed, nw["scale"])
            root = args.step2 if week == 10 else args.heldout
            path = root / "northwind" / f"export_{year}-W{week:02d}.csv"
            path.parent.mkdir(parents=True, exist_ok=True)
            write_export(path, tz, rows, "northwind", week)
            written.append(path)
            print(f"{path}  intervals={len(grid)}  seed={seed}")

    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for p in sorted(written):
        lines.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.as_posix()}")
    args.manifest.write_text("\n".join(lines) + "\n")
    print(f"manifest: {args.manifest} ({len(lines)} files); numpy {np.__version__}")


if __name__ == "__main__":
    main()
