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
    "fabrikam": dict(prefix="FA", grain=60, tz="America/New_York", scale=0.07, n_agents=28, n_pt=6, hours=(7, 22),
                     roster_seed=2, weeks={41: 141, 42: 142, 43: 143, 44: 144}, heldout=[44], fmt="canonical"),
    "northwind": dict(prefix="NW", grain=30, tz="America/Chicago", scale=0.10, n_agents=40, n_pt=8, hours=(6, 24),
                      roster_seed=7, weeks={42: 242, 43: 243, 44: 244, 45: 245}, heldout=[45], fmt="export"),
}
YEAR = 2026
WEEKDAY = [1.10, 1.05, 1.00, 1.00, 0.95, 0.55, 0.45]
BASE_DAILY = {"priority": 1400.0, "standard": 3200.0}
AHT_BASE = {"priority": 420.0, "standard": 300.0}
PEAK_INFLATION = 0.35
QUEUES = ("priority", "standard")


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


def write_canonical(path: Path, client: str, grain: int, rows) -> None:
    lines = ["client,queue,interval_start_utc,interval_minutes,volume,aht_sec"]
    for t, q, vol, aht in rows:
        lines.append(f"{client},{q},{t.strftime('%Y-%m-%dT%H:%M:%SZ')},{grain},{vol:.3f},{aht:.3f}")
    path.write_text("\n".join(lines) + "\n")


def write_export(path: Path, tz: ZoneInfo, rows) -> None:
    """Northwind's own format: local wall-clock plus the explicit UTC offset in effect for the row."""
    lines = ["interval_start_local,utc_offset,queue,volume,aht_sec"]
    for t, q, vol, aht in rows:
        loc = t.astimezone(tz)
        z = loc.strftime("%z")  # e.g. -0500
        lines.append(f"{loc.strftime('%Y-%m-%d %H:%M')},{z[:3]}:{z[3:]},{q},{vol:.3f},{aht:.3f}")
    path.write_text("\n".join(lines) + "\n")


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
    args = ap.parse_args()

    written: list[Path] = []
    for client, c in CLIENTS.items():
        tz = ZoneInfo(c["tz"])
        for week, seed in c["weeks"].items():
            grid = week_intervals_utc(YEAR, week, tz, c["grain"])
            rows = generate(grid, tz, c["grain"], c["scale"], seed, c["hours"])
            root = args.heldout if week in c["heldout"] else args.app
            if c["fmt"] == "canonical":
                path = root / client / f"week_{YEAR}-W{week:02d}.csv"
                path.parent.mkdir(parents=True, exist_ok=True)
                write_canonical(path, client, c["grain"], rows)
            else:
                path = root / client / f"export_{YEAR}-W{week:02d}.csv"
                path.parent.mkdir(parents=True, exist_ok=True)
                write_export(path, tz, rows)
            written.append(path)
            print(f"{path}  intervals={len(grid)}  seed={seed}")
        rpath = args.app / "agents" / f"{client}.csv"
        rpath.parent.mkdir(parents=True, exist_ok=True)
        write_roster(rpath, make_roster(c["prefix"], c["n_agents"], c["n_pt"], c["roster_seed"]))
        written.append(rpath)

    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for p in sorted(written):
        lines.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.as_posix()}")
    args.manifest.write_text("\n".join(lines) + "\n")
    print(f"manifest: {args.manifest} ({len(lines)} files); numpy {np.__version__}")


if __name__ == "__main__":
    main()
