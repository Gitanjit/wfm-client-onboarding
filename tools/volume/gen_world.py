#!/usr/bin/env python3
"""Deterministic generator for the seed repository's volume: client registry, configs, rosters,
historical data weeks and the service docs (ADRs, incidents, client notes, PR notes, runbook).

    python tools/volume/gen_world.py                 # writes into environment/app
    python tools/volume/gen_world.py --app <dir>     # elsewhere (e.g. to diff)

Everything agrees with tools/volume/WORLD.md. Re-running writes byte-identical files. The demand
model is tools/seedgen.py's (imported, unchanged); holidays, outages, the Contoso chat queue and the
per-client trend are applied on top of its rows. Files that seedgen owns (contoso/fabrikam 2026-W41..W43,
data/northwind, the three existing rosters) are never written here.
"""
from __future__ import annotations

import argparse
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from seedgen import generate, hour_profile, make_roster, week_intervals_utc, write_canonical, write_roster  # noqa: E402

import world_docs  # noqa: E402

# --------------------------------------------------------------------------------------------------
# Clients (WORLD.md "Clients and lifecycles")
# --------------------------------------------------------------------------------------------------

def W(year: int, week: int) -> tuple[int, int]:
    return (year, week)


def wk(key: tuple[int, int]) -> str:
    return f"{key[0]}-W{key[1]:02d}"


def week_add(key: tuple[int, int], n: int) -> tuple[int, int]:
    d = date.fromisocalendar(key[0], key[1], 1) + timedelta(weeks=n)
    iso = d.isocalendar()
    return (iso[0], iso[1])


def week_span(first: tuple[int, int], last: tuple[int, int]) -> list[tuple[int, int]]:
    out, k = [], first
    while k <= last:
        out.append(k)
        k = week_add(k, 1)
    return out


# scale: (first, last) linear trend over the client's span of weeks (BASE_DAILY x scale contacts/day).
# aht: multiplier on seedgen's AHT_BASE. Contoso and Fabrikam keep 1.0 and end on the scales of their
# existing 2026-W41..W43 files (0.10 and 0.07).
CLIENTS = {
    "contoso": dict(grain=15, tz="UTC", hours=(6, 24), scale=(0.085, 0.10), aht=1.0, seed_base=31,
                    first=W(2024, 49), last=W(2026, 40), trend_last=W(2026, 41), stride=4,
                    must=[W(2024, 49), W(2024, 52), W(2025, 1), W(2025, 26), W(2025, 30), W(2025, 32),
                          W(2025, 34), W(2025, 52), W(2026, 1)]),
    "tailspin": dict(grain=30, tz="Europe/Dublin", hours=(7, 21), scale=(0.052, 0.056), aht=0.9, seed_base=32,
                     first=W(2025, 3), last=W(2025, 43), drop_every=4, prefix="TS", n_agents=30, n_pt=6, roster_seed=21,
                     must=[W(2025, 3), W(2025, 6), W(2025, 12), W(2025, 13), W(2025, 17), W(2025, 26), W(2025, 32),
                           W(2025, 43)]),
    "adatum": dict(grain=60, tz="America/Denver", hours=(6, 24), scale=(0.045, 0.050), aht=1.2, seed_base=33,
                   first=W(2025, 11), last=W(2026, 13), stride=2, prefix="AD", n_agents=30, n_pt=6, roster_seed=22,
                   must=[W(2025, 11), W(2025, 22), W(2025, 26), W(2025, 36), W(2025, 44), W(2025, 48), W(2026, 4),
                         W(2026, 10), W(2026, 13)]),
    "woodgrove": dict(grain=30, tz="America/Los_Angeles", hours=(6, 21), scale=(0.080, 0.076), aht=1.05,
                      seed_base=34, first=W(2025, 20), last=W(2026, 3), drop_every=4, prefix="WG", n_agents=40, n_pt=8,
                      roster_seed=23,
                      must=[W(2025, 20), W(2025, 22), W(2025, 26), W(2025, 27), W(2025, 36), W(2025, 44), W(2025, 48),
                            W(2025, 52), W(2026, 3)]),
    "fabrikam": dict(grain=60, tz="America/New_York", hours=(6, 24), scale=(0.064, 0.07), aht=1.0, seed_base=35,
                     first=W(2025, 33), last=W(2026, 40), trend_last=W(2026, 41), stride=2,
                     must=[W(2025, 33), W(2025, 34), W(2025, 35), W(2025, 36), W(2025, 37), W(2025, 44), W(2025, 48),
                           W(2025, 52), W(2026, 10), W(2026, 16)]),
    "proseware": dict(grain=30, tz="Europe/Berlin", hours=(7, 21), scale=(0.058, 0.062), aht=0.95, seed_base=36,
                      first=W(2025, 47), last=W(2026, 33), drop_every=4, prefix="PW", n_agents=34, n_pt=7, roster_seed=24,
                      must=[W(2025, 47), W(2025, 52), W(2026, 1), W(2026, 13), W(2026, 14), W(2026, 15), W(2026, 16),
                            W(2026, 22), W(2026, 33)]),
    "wingtip": dict(grain=30, tz="America/Phoenix", hours=(6, 24), scale=(0.070, 0.082), aht=1.1, seed_base=37,
                    first=W(2026, 7), last=W(2026, 42), drop_every=4, prefix="WT", n_agents=36, n_pt=8, roster_seed=25,
                    must=[W(2026, 7), W(2026, 8), W(2026, 16), W(2026, 22), W(2026, 27), W(2026, 37), W(2026, 42)]),
}

# Public holidays (local dates): volume on the day x HOLIDAY_DAY, the rest of the week x HOLIDAY_WEEK,
# giving a week 15-30 % below its neighbours. Fabrikam's Labor Day week is set to about 22 % below.
HOLIDAY_DAY = 0.30
HOLIDAY_WEEK = 0.93
US = ["2025-05-26", "2025-07-04", "2025-09-01", "2025-11-27", "2025-12-25", "2026-01-01", "2026-01-19",
      "2026-02-16", "2026-05-25", "2026-07-03", "2026-09-07"]
HOLIDAYS = {
    "contoso": ["2024-12-25", "2024-12-26", "2025-01-01", "2025-12-25", "2025-12-26", "2026-01-01"],
    "tailspin": ["2025-02-03", "2025-03-17", "2025-04-21", "2025-05-05", "2025-06-02", "2025-08-04"],
    "adatum": US, "woodgrove": US, "fabrikam": US, "wingtip": US,
    "proseware": ["2025-12-25", "2025-12-26", "2026-01-01", "2026-04-03", "2026-04-06", "2026-05-01", "2026-05-14",
                  "2026-05-25"],
}
DAY_AFTER = {"2025-11-28": 0.70}   # the Friday after Thanksgiving (US clients)
SPECIAL_WEEK = {("fabrikam", W(2025, 36)): 0.90}

# Outages (UTC windows): a run of zero-volume intervals inside operating hours; partial intervals keep
# the share of the interval outside the window. Documented in docs/incidents/.
OUTAGES = [
    (datetime(2025, 6, 24, 13, 40, tzinfo=timezone.utc), datetime(2025, 6, 24, 16, 20, tzinfo=timezone.utc),
     ("contoso", "tailspin", "adatum", "woodgrove")),
    (datetime(2026, 4, 14, 13, 0, tzinfo=timezone.utc), datetime(2026, 4, 14, 15, 30, tzinfo=timezone.utc),
     ("fabrikam", "proseware", "wingtip")),
]

# Contoso's evening chat queue, 2025-07-21 to 2025-09-01 (WORLD.md). Its own random stream, so the
# priority and standard rows do not depend on whether a week carries chat.
CHAT = dict(first=date(2025, 7, 21), end=date(2025, 9, 1), hours=(16, 24), base_daily=500.0, aht=540.0,
            seed_offset=7000)


def week_seed(client: str, key: tuple[int, int]) -> int:
    return CLIENTS[client]["seed_base"] * 10000 + (key[0] % 100) * 100 + key[1]


def weeks_for(client: str) -> list[tuple[int, int]]:
    c = CLIENTS[client]
    span = week_span(c["first"], c["last"])
    if c.get("drop_every"):   # every week except each n-th
        keep = {k for i, k in enumerate(span) if i % c["drop_every"] != c["drop_every"] - 1}
    else:                     # every n-th week
        keep = {k for i, k in enumerate(span) if i % c["stride"] == 0}
    keep |= set(c["must"])
    return sorted(keep)


def scale_for(client: str, key: tuple[int, int]) -> float:
    c = CLIENTS[client]
    span = week_span(c["first"], c.get("trend_last", c["last"]))
    lo, hi = c["scale"]
    i = span.index(key)
    return lo + (hi - lo) * i / max(1, len(span) - 1)


def day_factor(client: str, key: tuple[int, int], d: date) -> float:
    hols = {date.fromisoformat(s) for s in HOLIDAYS[client]}
    mon = date.fromisocalendar(key[0], key[1], 1)
    days = {mon + timedelta(days=i) for i in range(7)}
    if not hols & days:
        return 1.0
    if d in hols:
        return HOLIDAY_DAY
    if d.isoformat() in DAY_AFTER and client in ("adatum", "woodgrove", "fabrikam", "wingtip"):
        return DAY_AFTER[d.isoformat()]
    return SPECIAL_WEEK.get((client, key), HOLIDAY_WEEK)


def outage_keep(client: str, t: datetime, grain: int) -> float:
    """Share of the interval starting at t that lies outside every outage window of the client."""
    end = t + timedelta(minutes=grain)
    lost = 0.0
    for a, b, who in OUTAGES:
        if client in who:
            lost += max(0.0, (min(end, b) - max(t, a)).total_seconds())
    return max(0.0, 1.0 - lost / (grain * 60))


def add_chat(rows, tz: ZoneInfo, grain: int, seed: int, scale: float):
    """Insert a `chat` row after each interval's standard row while the chat queue ran."""
    rng = np.random.default_rng(seed + CHAT["seed_offset"])
    a, b = CHAT["hours"]
    norm = sum(hour_profile(h) for h in np.arange(a, b, grain / 60))
    out = []
    for r in rows:
        out.append(r)
        if r[1] != "standard":
            continue
        t = r[0]
        loc = t.astimezone(tz)
        h = loc.hour + loc.minute / 60
        if a <= h < b and CHAT["first"] <= loc.date() < CHAT["end"]:
            vol = CHAT["base_daily"] * scale * hour_profile(h) / norm * rng.lognormal(0, 0.15)
            aht = CHAT["aht"] * rng.lognormal(0, 0.06)
        else:
            vol, aht = 0.0, CHAT["aht"]
        out.append((t, "chat", vol, aht))
    return out


def week_rows(client: str, key: tuple[int, int]):
    c = CLIENTS[client]
    tz = ZoneInfo(c["tz"])
    grid = week_intervals_utc(key[0], key[1], tz, c["grain"])
    seed = week_seed(client, key)
    scale = scale_for(client, key)
    rows = generate(grid, tz, c["grain"], scale, seed, c["hours"])
    mon = date.fromisocalendar(key[0], key[1], 1)
    if client == "contoso" and mon < CHAT["end"] and mon + timedelta(days=7) > CHAT["first"]:
        rows = add_chat(rows, tz, c["grain"], seed, scale)
    out = []
    for t, q, vol, aht in rows:
        if vol > 0:
            vol *= day_factor(client, key, t.astimezone(tz).date()) * outage_keep(client, t, c["grain"])
        out.append((t, q, vol, aht * c["aht"]))
    return out


def write_data(app: Path) -> list[Path]:
    written = []
    for client in CLIENTS:
        for key in weeks_for(client):
            path = app / "data" / client / f"week_{wk(key)}.csv"
            path.parent.mkdir(parents=True, exist_ok=True)
            write_canonical(path, client, CLIENTS[client]["grain"], week_rows(client, key))
            written.append(path)
    return written


def write_rosters(app: Path) -> list[Path]:
    written = []
    for client, c in CLIENTS.items():
        if "prefix" not in c:
            continue
        path = app / "data" / "agents" / f"{client}.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        write_roster(path, make_roster(c["prefix"], c["n_agents"], c["n_pt"], c["roster_seed"]))
        written.append(path)
    return written


def write_text(app: Path, files: dict[str, str]) -> list[Path]:
    written = []
    for rel, text in files.items():
        path = app / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        written.append(path)
    return written


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", type=Path, default=ROOT / "environment" / "app")
    ap.add_argument("--only", choices=["data", "text"], default=None)
    args = ap.parse_args()
    written = []
    if args.only in (None, "data"):
        written += write_data(args.app)
        written += write_rosters(args.app)
    if args.only in (None, "text"):
        written += write_text(args.app, world_docs.files(CLIENTS, weeks_for))
    total = sum(p.stat().st_size for p in written)
    print(f"{len(written)} files, {total / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
