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


# --------------------------------------------------------------------------------------------------
# environment/history/plan.py: when each generated file enters the service's history
# --------------------------------------------------------------------------------------------------

DANA, TOMAS, MEI = "Dana Vexley", "Tomas Okafor", "Mei Lindqvist"
STARTS = {DANA: date(2024, 11, 4), TOMAS: date(2025, 2, 17), MEI: date(2025, 6, 2)}
NAMES = {"contoso": "Contoso", "tailspin": "Tailspin", "adatum": "Adatum", "woodgrove": "Woodgrove",
         "fabrikam": "Fabrikam", "proseware": "Proseware", "wingtip": "Wingtip"}
DST_WEEKS = {("tailspin", W(2025, 13)): 334, ("tailspin", W(2025, 43)): 338, ("adatum", W(2025, 44)): 169,
             ("adatum", W(2026, 10)): 167, ("woodgrove", W(2025, 44)): 338, ("fabrikam", W(2025, 44)): 169,
             ("fabrikam", W(2026, 10)): 167, ("proseware", W(2026, 13)): 334}
DATA_SPECIAL = {
    ("woodgrove", W(2025, 44)): ("2025-11-05T11:20:00+00:00", TOMAS,
                                 "Woodgrove 2025-W44 data, re-cut after the fall-back conversion fix (WFM-114)\n\n"
                                 "Each row's offset now comes from the timezone database; 338 intervals.\n"
                                 "See docs/incidents/2025-11-05-woodgrove-dst-fall-back-ingest.md."),
    ("adatum", W(2026, 4)): ("2026-01-29T16:52:00+00:00", MEI,
                             "Adatum 2026-W04 data (late drop, received Thu 29 Jan; WFM-142)"),
}
LAST_NOTE = {("tailspin", W(2025, 43)): "last drop before the contract ends",
             ("adatum", W(2026, 13)): "final week", ("woodgrove", W(2026, 3)): "final week",
             ("proseware", W(2026, 33)): "last week before the pause"}
OUTAGE_NOTE = {W(2025, 26): "telephony outage Tue 24 Jun, committed as delivered",
               W(2026, 16): "tenant outage Tue 14 Apr, committed as delivered"}
OUTAGE_CLIENTS = {W(2025, 26): OUTAGES[0][2], W(2026, 16): OUTAGES[1][2]}
CHAT_WEEKS = {W(2025, w) for w in range(30, 36)}

# (date, author, pr, message, paths). Paths are relative to environment/app, in their final form.
DOC_EVENTS = [
    ("2024-11-08T15:20:00+00:00", DANA, None, "ADR 0001: canonical interval format",
     ["docs/adr/0001-canonical-interval-format.md"]),
    ("2024-11-15T11:05:00+00:00", DANA, None, "ADR 0002: store UTC, plan in local wall-clock time",
     ["docs/adr/0002-utc-storage-local-templates.md"]),
    ("2024-11-21T16:40:00+00:00", DANA, None, "ADR 0003: deterministic scheduling",
     ["docs/adr/0003-deterministic-scheduling.md"]),
    ("2024-11-29T14:10:00+00:00", DANA, 4, "Contoso onboarding (WFM-006)\n\nPR note for the Contoso go-live in 2024-W49.",
     ["docs/prs/004-contoso-onboarding.md"]),
    ("2025-01-09T10:30:00+00:00", DANA, 9, "Tailspin onboarding: roster and PR note (WFM-019)",
     ["data/agents/tailspin.csv", "docs/prs/009-tailspin-onboarding.md"]),
    ("2025-03-05T09:45:00+00:00", TOMAS, None, "ADR 0004: per-client configuration overlay",
     ["docs/adr/0004-per-client-config-overlay.md"]),
    ("2025-03-06T15:30:00+00:00", TOMAS, None, "Tailspin settings as a client overlay (configs/tailspin.yaml)",
     ["configs/tailspin.yaml"]),
    ("2025-03-07T13:15:00+00:00", TOMAS, 14, "Adatum onboarding: config, roster (WFM-034)",
     ["configs/adatum.yaml", "data/agents/adatum.csv", "docs/prs/014-adatum-onboarding.md"]),
    ("2025-05-08T14:00:00+00:00", TOMAS, 19, "Woodgrove onboarding: config, roster (WFM-052)",
     ["configs/woodgrove.yaml", "data/agents/woodgrove.csv", "docs/prs/019-woodgrove-onboarding.md"]),
    ("2025-07-01T15:10:00+00:00", MEI, None, "Incident note: hosted telephony outage of 2025-06-24 (WFM-068)",
     ["docs/incidents/2025-07-01-telephony-platform-outage.md"]),
    ("2025-07-03T16:25:00+00:00", MEI, 24, "Volume report: weekly totals, interval counts, zero-volume runs (WFM-071)",
     ["wfm/weeks.py", "wfm/report/__init__.py", "wfm/report/markdown.py", "wfm/report/volume.py",
      "tests_unit/test_weeks.py", "tests_unit/test_report_volume.py", "docs/prs/024-volume-report.md"]),
    ("2025-07-11T11:50:00+00:00", MEI, 28, "Archive weekly evaluations; multi-week summary (WFM-077)",
     ["wfm/report/history.py", "wfm/report/summary.py", "tests_unit/test_report_summary.py",
      "docs/prs/028-eval-history.md"]),
    ("2025-08-08T10:20:00+00:00", MEI, None, "ADR 0005: vendoring third-party code",
     ["docs/adr/0005-vendoring-policy.md"]),
    ("2025-08-18T09:35:00+00:00", MEI, None, "ADR 0006: schedule export layouts",
     ["docs/adr/0006-schedule-export-layouts.md"]),
    ("2025-08-20T15:55:00+00:00", MEI, 39, "Schedule exports in the clients' layouts (WFM-093)",
     ["wfm/export/__init__.py", "wfm/export/base.py", "wfm/export/activity_csv.py", "wfm/export/roster_grid.py",
      "wfm/export/segments_json.py", "tests_unit/test_export.py", "docs/prs/039-schedule-export.md"]),
    ("2025-09-03T14:30:00+00:00", TOMAS, None, "Client notes for Contoso", ["docs/clients/contoso.md"]),
    ("2025-10-08T10:05:00+00:00", MEI, None, "Client notes for Fabrikam (renewed 2025-10-06)",
     ["docs/clients/fabrikam.md"]),
    ("2025-11-04T11:40:00+00:00", TOMAS, None, "Client notes for Tailspin, retired 2025-10-31",
     ["docs/clients/tailspin.md"]),
    ("2025-11-05T16:15:00+00:00", TOMAS, None, "Incident note: Woodgrove 2025-W44 fall-back ingest (WFM-114)",
     ["docs/incidents/2025-11-05-woodgrove-dst-fall-back-ingest.md"]),
    ("2025-11-10T10:00:00+00:00", TOMAS, None, "ADR 0007: client config schema 2",
     ["docs/adr/0007-config-schema-v2.md"]),
    ("2025-11-13T15:45:00+00:00", TOMAS, 50, "Client config schema 2 (WFM-121)", ["docs/prs/050-config-schema-v2.md"]),
    ("2025-11-14T12:20:00+00:00", TOMAS, 51, "Proseware onboarding: schema-2 config, roster (WFM-123)",
     ["configs/proseware.yaml", "data/agents/proseware.csv", "docs/prs/051-proseware-onboarding.md"]),
    ("2026-01-20T13:10:00+00:00", TOMAS, None, "Client notes for Woodgrove, retired 2026-01-16",
     ["docs/clients/woodgrove.md"]),
    ("2026-01-30T10:30:00+00:00", MEI, None, "Incident note: Adatum 2026-W04 late drop (WFM-142)",
     ["docs/incidents/2026-01-30-adatum-late-data-drop.md"]),
    ("2026-02-05T16:00:00+00:00", MEI, 53, "Wingtip onboarding: schema-2 config, roster; v2 loader tests (WFM-146)",
     ["configs/wingtip.yaml", "data/agents/wingtip.csv", "tests_unit/test_config_v2.py",
      "docs/prs/053-wingtip-onboarding.md"]),
    ("2026-02-10T09:50:00+00:00", MEI, None, "Client notes for Wingtip", ["docs/clients/wingtip.md"]),
    ("2026-04-01T14:20:00+00:00", TOMAS, None, "Client notes for Adatum, retired 2026-03-27", ["docs/clients/adatum.md"]),
    ("2026-04-21T15:35:00+00:00", TOMAS, None, "Incident note: contact-centre tenant outage of 2026-04-14 (WFM-158)",
     ["docs/incidents/2026-04-21-contact-centre-tenant-outage.md"]),
    ("2026-06-12T14:45:00+00:00", MEI, 55, "Weekly digests and agent shift lists (WFM-171)",
     ["wfm/notify/__init__.py", "wfm/notify/templates.py", "wfm/notify/digest.py", "wfm/notify/agents.py",
      "tests_unit/test_notify.py", "docs/prs/055-notify-digests.md"]),
    ("2026-08-21T11:15:00+00:00", TOMAS, None, "Client notes for Proseware, paused from 2026-08-14",
     ["docs/clients/proseware.md"]),
    ("2026-10-14T16:30:00+00:00", TOMAS, 60, "Client registry and `wfm clients` (WFM-219)",
     ["wfm/registry.py", "clients/registry.yaml", "clients/README.md", "docs/adr/0008-client-lifecycle.md",
      "docs/OPERATIONS.md", "tests_unit/test_registry.py", "tests_unit/test_cli_subcommands.py",
      "docs/prs/060-client-registry.md"]),
    ("2026-10-15T10:40:00+00:00", DANA, None, "Unit tests pinning notable data weeks: DST interval counts, outage runs",
     ["tests_unit/test_data_weeks.py"]),
]

# Edits to files that already exist on the branch (placed by the core history, not added here).
CORE_EDITS = [
    {"date": "2025-07-03", "pr": 24, "file": "wfm/cli.py", "what": "add `report volume`"},
    {"date": "2025-07-11", "pr": 28, "file": "wfm/cli.py", "what": "add `report archive` and `report summary`"},
    {"date": "2025-08-20", "pr": 39, "file": "wfm/cli.py", "what": "add `export` (--layout required until PR #60)"},
    {"date": "2025-11-13", "pr": 50, "file": "wfm/config.py",
     "what": "add V2_SECTIONS and _flatten_v2 (only keys that existed then; later keys join their section when added)"},
    {"date": "2026-06-12", "pr": 55, "file": "wfm/cli.py", "what": "add `notify`"},
    {"date": "2026-10-14", "pr": 60, "file": "wfm/cli.py",
     "what": "add `clients`; export layout and notify account manager default from clients/registry.yaml"},
]


def _h(*parts) -> int:
    """Small deterministic hash (no PYTHONHASHSEED dependence)."""
    s = "|".join(map(str, parts))
    return sum((i + 1) * ord(ch) for i, ch in enumerate(s))


def _rota(d: date) -> str:
    if d < STARTS[TOMAS]:
        return DANA
    iso = d.isocalendar()[1]
    if d < STARTS[MEI]:
        return (DANA, TOMAS)[iso % 2]
    return (DANA, TOMAS, MEI)[iso % 3]


def data_events() -> list[dict]:
    events = []
    for client in CLIENTS:
        weeks = weeks_for(client)
        for key in weeks:
            path = f"data/{client}/week_{wk(key)}.csv"
            if (client, key) in DATA_SPECIAL:
                when, author, msg = DATA_SPECIAL[(client, key)]
            else:
                sunday = date.fromisocalendar(key[0], key[1], 7)
                h = _h(client, wk(key))
                d = sunday + timedelta(days=(1, 1, 1, 2, 2, 3)[h % 6])
                minute = 8 * 60 + (h * 37) % 540
                when = f"{d.isoformat()}T{minute // 60:02d}:{minute % 60:02d}:00+00:00"
                author = _rota(d)
                verb = ("{n} {w} data", "{n} {w} interval data", "Add {n} {w} drop", "{n} {w} drop")[h % 4]
                msg = verb.format(n=NAMES[client], w=wk(key))
                notes = []
                if key == weeks[0]:
                    notes.append("first live week")
                if key in OUTAGE_NOTE and client in OUTAGE_CLIENTS[key]:
                    notes.append(OUTAGE_NOTE[key])
                if (client, key) in DST_WEEKS:
                    notes.append(f"DST week, {DST_WEEKS[(client, key)]} intervals")
                if client == "contoso" and key in CHAT_WEEKS:
                    notes.append("with chat rows")
                if (client, key) in LAST_NOTE:
                    notes.append(LAST_NOTE[(client, key)])
                if notes:
                    msg += " (" + "; ".join(notes) + ")"
            events.append({"date": when, "author": author, "message": msg, "add": [path], "pr": None})
    return events


def plan_events() -> list[dict]:
    events = data_events()
    for when, author, pr, msg, paths in DOC_EVENTS:
        events.append({"date": when, "author": author, "message": msg, "add": list(paths), "pr": pr})
    events.sort(key=lambda e: (e["date"], e["add"][0]))
    for e in events:
        d = date.fromisoformat(e["date"][:10])
        assert d >= STARTS[e["author"]], e
        assert date(2024, 11, 4) <= d <= date(2026, 10, 23), e
    return events


def write_plan(path: Path) -> None:
    events = plan_events()
    lines = ['"""History plan for the generated volume (written by tools/volume/gen_world.py; do not edit).',
             "",
             "EVENTS: one dict per commit, ordered by date. `add` lists paths relative to environment/app in",
             "their final form; each generated path appears in exactly one event. `pr` set means a --no-ff",
             "merge of a feature branch for that pull request.",
             "CORE_EDITS: when files that already exist on the branch gained the pieces this volume relies on.",
             '"""', "", "EVENTS = ["]
    for e in events:
        lines.append(f"    {e!r},")
    lines += ["]", "", "CORE_EDITS = ["]
    lines += [f"    {e!r}," for e in CORE_EDITS]
    lines += ["]", ""]
    path.write_text("\n".join(lines))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", type=Path, default=ROOT / "environment" / "app")
    ap.add_argument("--only", choices=["data", "text", "plan"], default=None)
    ap.add_argument("--plan", type=Path, default=ROOT / "environment" / "history" / "plan.py")
    args = ap.parse_args()
    written = []
    if args.only in (None, "data"):
        written += write_data(args.app)
        written += write_rosters(args.app)
    if args.only in (None, "text"):
        written += write_text(args.app, world_docs.files(CLIENTS, weeks_for))
    if args.only in (None, "plan"):
        write_plan(args.plan)
        written.append(args.plan)
    total = sum(p.stat().st_size for p in written)
    print(f"{len(written)} files, {total / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
