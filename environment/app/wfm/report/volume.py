"""Weekly volume report from a client's canonical files (data/<client>/week_<ISO>.csv).

Run on a data drop before the week is run, and to look back over a client's history. Per week:
contacts and volume-weighted handle time per queue, the busiest interval in local time, the interval
count against the client's local week, file checks, and runs of zero-volume intervals inside
operating hours on a day that otherwise has contacts (an ACD or carrier outage, or a gap in the
client's feed). Queues are reported as the file delivers them.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from wfm import config, weeks
from wfm.report import markdown as md

CANONICAL = re.compile(r"^week_(\d{4}-W\d{2})\.csv$")
COLUMNS = ("client", "queue", "interval_start_utc", "interval_minutes", "volume", "aht_sec")


@dataclass(frozen=True)
class ZeroRun:
    """Consecutive zero-volume intervals inside operating hours (all queues together)."""
    start_local: datetime
    end_local: datetime
    intervals: int

    @property
    def minutes(self) -> int:
        return int((self.end_local - self.start_local).total_seconds() // 60)


@dataclass
class WeekVolume:
    week: str
    grain: int
    intervals: int
    expected: int
    contacts: dict[str, float]
    aht: dict[str, float]
    peak_local: datetime | None
    peak_volume: float
    daily: list[float] = field(default_factory=list)      # contacts per local day, Monday first
    hourly: list[float] = field(default_factory=list)     # contacts per local hour of day (0-23), whole week
    zero_runs: list[ZeroRun] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    prev_week: str | None = None
    change: float | None = None

    @property
    def total(self) -> float:
        return float(sum(self.contacts.values()))


def week_files(client: str, data_dir: Path | None = None) -> dict[str, Path]:
    """{week: path} for the client's canonical files, in week order. Other files are left alone."""
    d = (data_dir or config.DATA_DIR) / client
    if not d.is_dir():
        return {}
    found = {}
    for p in d.iterdir():
        m = CANONICAL.match(p.name)
        if m:
            weeks.parse(m.group(1))
            found[m.group(1)] = p
    return {w: found[w] for w in sorted(found, key=weeks.key)}


def read_week(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        raise SystemExit(f"{path}: missing column(s) {', '.join(missing)}")
    df["interval_start_utc"] = pd.to_datetime(df["interval_start_utc"], utc=True)
    return df


def file_issues(df: pd.DataFrame, cfg: dict, week: str) -> list[str]:
    """Problems with a canonical week file that would change what `wfm run` makes of it."""
    issues = []
    tz, grain = cfg["tz"], cfg["interval_minutes"]
    clients = sorted(set(df["client"].astype(str)) - {cfg["client"]})
    if clients:
        issues.append(f"rows for another client: {', '.join(clients)}")
    grains = sorted(set(int(g) for g in df["interval_minutes"]))
    if grains != [grain]:
        issues.append(f"interval_minutes {'/'.join(map(str, grains))} in the file, {grain} in the config")
    starts = df["interval_start_utc"].drop_duplicates()
    lo, hi = weeks.bounds_utc(week, tz)
    outside = int(((starts < lo) | (starts >= hi)).sum())
    if outside:
        issues.append(f"{outside} interval(s) outside the local week")
    off_grain = int(((starts - lo).dt.total_seconds() % (grain * 60) != 0).sum())
    if off_grain:
        issues.append(f"{off_grain} interval start(s) off the {grain}-minute grain")
    expected = weeks.expected_intervals(week, tz, grain)
    if len(starts) != expected:
        issues.append(f"{len(starts)} intervals, expected {expected} for the local week")
    dupes = int(df.duplicated(["queue", "interval_start_utc"]).sum())
    if dupes:
        issues.append(f"{dupes} duplicate queue/interval row(s)")
    neg = int((df["volume"] < 0).sum())
    if neg:
        issues.append(f"{neg} negative volume(s)")
    bad_aht = int(((df["volume"] > 0) & ~(df["aht_sec"] > 0)).sum())
    if bad_aht:
        issues.append(f"{bad_aht} row(s) with volume but no handle time")
    for q in sorted(set(cfg.get("sla", {})) - set(df["queue"])):
        issues.append(f"no rows for queue {q}")
    return issues


def zero_runs(df: pd.DataFrame, cfg: dict, min_run: int = 2) -> list[ZeroRun]:
    """Runs of at least `min_run` consecutive intervals with no contacts on any queue, inside the
    local operating hours, on local days that have contacts in other intervals."""
    tz, hours = cfg["tz"], cfg["operating_hours"]
    step = timedelta(minutes=cfg["interval_minutes"])
    totals = df.groupby("interval_start_utc", sort=True)["volume"].sum()
    by_day: dict = {}
    for t, v in totals.items():
        t = t.to_pydatetime()
        if weeks.in_operating_hours(t, tz, hours):
            by_day.setdefault(weeks.to_local(t, tz).date(), []).append((t, float(v)))
    runs = []
    for _day, slots in sorted(by_day.items()):
        if sum(v for _, v in slots) <= 0:
            continue                          # closed or no data that day: not an outage
        run: list[datetime] = []
        for t, v in slots + [(None, 1.0)]:    # sentinel closes a trailing run
            contiguous = run and t is not None and t - run[-1] == step
            if t is not None and v <= 0 and (not run or contiguous):
                run.append(t)
                continue
            if len(run) >= min_run:
                runs.append(ZeroRun(weeks.to_local(run[0], tz), weeks.to_local(run[-1] + step, tz), len(run)))
            run = [t] if t is not None and v <= 0 else []
    return runs


def daily_totals(df: pd.DataFrame, tz: str, week: str) -> list[float]:
    """Contacts per local day of the week (all queues), Monday first."""
    local_dates = df["interval_start_utc"].dt.tz_convert(tz).dt.date
    by_day = df.groupby(local_dates)["volume"].sum()
    return [float(by_day.get(d, 0.0)) for d in weeks.days(week)]


def hourly_totals(df: pd.DataFrame, tz: str) -> list[float]:
    """Contacts per local hour of day over the whole week (all queues), 00 to 23."""
    by_hour = df.groupby(df["interval_start_utc"].dt.tz_convert(tz).dt.hour)["volume"].sum()
    return [float(by_hour.get(h, 0.0)) for h in range(24)]


def week_volume(path: Path, cfg: dict, week: str, min_run: int = 2) -> WeekVolume:
    df = read_week(path)
    contacts, aht = {}, {}
    for q, g in df.groupby("queue", sort=True):
        vol = float(g["volume"].sum())
        contacts[q] = vol
        aht[q] = float((g["volume"] * g["aht_sec"]).sum() / vol) if vol > 0 else None
    totals = df.groupby("interval_start_utc", sort=True)["volume"].sum()
    peak_t = totals.idxmax() if len(totals) and totals.max() > 0 else None
    return WeekVolume(
        week=week, grain=cfg["interval_minutes"],
        intervals=int(df["interval_start_utc"].nunique()),
        expected=weeks.expected_intervals(week, cfg["tz"], cfg["interval_minutes"]),
        contacts=contacts, aht=aht,
        peak_local=weeks.to_local(peak_t.to_pydatetime(), cfg["tz"]) if peak_t is not None else None,
        peak_volume=float(totals.max()) if len(totals) else 0.0, daily=daily_totals(df, cfg["tz"], week),
        hourly=hourly_totals(df, cfg["tz"]),
        zero_runs=zero_runs(df, cfg, min_run), issues=file_issues(df, cfg, week))


def volume_report(cfg: dict, first: str | None = None, last: str | None = None,
                  data_dir: Path | None = None, min_run: int = 2) -> list[WeekVolume]:
    """One WeekVolume per canonical file in [first, last]; `change` is against the previous file
    in the list (sampled histories skip weeks, so `prev_week` names it)."""
    files = week_files(cfg["client"], data_dir)
    rows, prev = [], None
    for week, path in files.items():
        if (first and weeks.key(week) < weeks.key(first)) or (last and weeks.key(week) > weeks.key(last)):
            continue
        row = week_volume(path, cfg, week, min_run)
        if prev is not None and prev.total > 0:
            row.prev_week, row.change = prev.week, row.total / prev.total - 1
        rows.append(row)
        prev = row
    return rows


def profile(rows: list[WeekVolume]) -> tuple[list[float], list[float]]:
    """Share of contacts per weekday and per local hour of day over all the weeks given. Sampled
    weeks count once each; a holiday or outage week pulls its days down like any other."""
    total = sum(r.total for r in rows)
    if total <= 0:
        return [0.0] * 7, [0.0] * 24
    return ([sum(r.daily[i] for r in rows) / total for i in range(7)],
            [sum(r.hourly[h] for r in rows) / total for h in range(24)])


def _peak(r: WeekVolume) -> str:
    if r.peak_local is None:
        return md.DASH
    return f"{weeks.DAY_NAMES[r.peak_local.weekday()]} {r.peak_local:%H:%M}"


def render(cfg: dict, rows: list[WeekVolume], days: bool = False, shape: bool = False) -> str:
    """Markdown report; `days` adds contacts per local day, `shape` the weekday and intraday profile."""
    name = cfg.get("name", cfg["client"])
    if not rows:
        return md.document(md.heading(f"Volume - {name}", 1), "No canonical week files in the range.")
    queues = sorted({q for r in rows for q in r.contacts})
    span = rows[0].week if len(rows) == 1 else f"{rows[0].week} to {rows[-1].week}"
    intro = (f"Client `{cfg['client']}`, {len(rows)} week file(s), {span}. Times are local ({cfg['tz']}), "
             f"operating hours {cfg['operating_hours'][0]:02d}:00-{cfg['operating_hours'][1]:02d}:00. "
             "Contacts per queue; handle time is volume-weighted, in seconds. Change is against the "
             "previous file listed.")
    headers = ["week", "intervals", "expected", *queues, "total", "change", "vs",
               *[f"aht {q}" for q in queues], "peak"]
    body = [[r.week, r.intervals, r.expected, *[md.num(r.contacts.get(q)) for q in queues], md.num(r.total),
             md.change(r.change), r.prev_week or md.DASH, *[md.num(r.aht.get(q), 0) for q in queues], _peak(r)]
            for r in rows]
    blocks = [md.heading(f"Volume - {name}", 1), intro, md.table(headers, body)]

    if days:
        blocks += [md.heading("Contacts per local day"),
                   md.table(["week", *weeks.DAY_NAMES, "total"],
                            [[r.week, *[md.num(v) for v in r.daily], md.num(r.total)] for r in rows])]

    if shape:
        by_day, by_hour = profile(rows)
        open_h, close_h = cfg["operating_hours"]
        blocks += [md.heading("Profile over the range"),
                   md.table(["weekday", *weeks.DAY_NAMES], [["share", *[md.pct(v) for v in by_day]]]),
                   md.table(["local hour", "share of contacts"],
                            [[f"{h:02d}:00", md.pct(by_hour[h])] for h in range(int(open_h), int(close_h))])]

    runs = [(r.week, z) for r in rows for z in r.zero_runs]
    blocks.append(md.heading("Zero-volume runs inside operating hours"))
    if runs:
        blocks.append(md.table(["week", "day", "from", "to", "intervals", "minutes"],
                               [[w, f"{weeks.DAY_NAMES[z.start_local.weekday()]} {z.start_local:%Y-%m-%d}",
                                 f"{z.start_local:%H:%M}", weeks.hhmm(z.end_local, z.start_local.date()),
                                 z.intervals, z.minutes] for w, z in runs]))
    else:
        blocks.append("None.")

    blocks.append(md.heading("File checks"))
    flagged = [f"{r.week}: {'; '.join(r.issues)}" for r in rows if r.issues]
    blocks.append(md.bullets(flagged) if flagged else "All files pass.")
    return md.document(*blocks)
