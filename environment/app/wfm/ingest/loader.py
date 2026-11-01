"""Ingest: a client's weekly demand file -> canonical intervals (UTC, client grain).

Two input layouts are supported in data/<client>/:
  week_<ISO>.csv    canonical (client, queue, interval_start_utc, interval_minutes, volume, aht_sec)
  export_<ISO>.csv  a client's own local-time export (interval_start_local, ..., queue, volume, aht_sec),
                    kept from Fabrikam's first onboarding; assumed to be at the client's configured grain.

The result has one row per queue per interval of the ISO week in the client's timezone, at the
client's configured grain, sorted by interval then queue.
"""
from __future__ import annotations

from datetime import date, timedelta

import pandas as pd

from wfm.config import DATA_DIR

QUEUES = ("priority", "standard")


def iso_week_monday(week: str) -> date:
    """'2026-W44' -> Monday 2026-10-26."""
    year, wk = week.split("-W")
    return date.fromisocalendar(int(year), int(wk), 1)


def local_days(week: str, tz: str) -> list[date]:
    mon = iso_week_monday(week)
    return [mon + timedelta(days=i) for i in range(7)]


def _read_canonical(path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["interval_start_utc"] = pd.to_datetime(df["interval_start_utc"], utc=True)
    return df[["queue", "interval_start_utc", "volume", "aht_sec"]]


# Fabrikam's re-sent 2025 exports have no offset column. US Eastern offset in effect from each DST
# change date (local) on; good enough for Fabrikam's weeks (WFM-204).
FABRIKAM_OFFSETS = {"2025-03-09": "-04:00", "2025-11-02": "-05:00", "2026-03-08": "-04:00", "2026-11-01": "-05:00"}


def _fixed_offsets(local: pd.Series, table: dict[str, str]) -> pd.Series:
    """UTC from local wall-clock labels and a {change date: offset} table."""
    keys = sorted(table)
    off = [table[max([k for k in keys if k <= d] or keys[:1])] for d in local.dt.strftime("%Y-%m-%d")]
    return pd.to_datetime(local.dt.strftime("%Y-%m-%d %H:%M") + pd.Series(off, index=local.index),
                          format="%Y-%m-%d %H:%M%z", utc=True)


def _read_export(path, cfg: dict) -> pd.DataFrame:
    df = pd.read_csv(path)
    local = pd.to_datetime(df["interval_start_local"]) if "interval_start_local" in df else None
    if "interval_end_local" in df:
        # Some exports stamp each row with the interval's END (data/<client>/README.txt); the offset is the
        # one in effect at that moment. The start is one export interval earlier, in elapsed time.
        stamp = df["interval_end_local"].str.strip() + df["utc_offset"].str.strip()
        end = pd.to_datetime(stamp, format="%Y-%m-%d %H:%M%z", utc=True)
        df["interval_start_utc"] = end - pd.Timedelta(minutes=cfg.get("export_interval_minutes", cfg["interval_minutes"]))
    elif "utc_offset" in df:
        # The export's utc_offset is authoritative (data/<client>/README.txt): build UTC from it rather
        # than localising the wall-clock label, which repeats during a DST fall-back.
        stamp = df["interval_start_local"].str.strip() + df["utc_offset"].str.strip()
        df["interval_start_utc"] = pd.to_datetime(stamp, format="%Y-%m-%d %H:%M%z", utc=True)
    elif cfg["client"] == "fabrikam":   # WFM-204
        df["interval_start_utc"] = _fixed_offsets(local, FABRIKAM_OFFSETS)
    else:
        df["interval_start_utc"] = local.dt.tz_localize(cfg["tz"]).dt.tz_convert("UTC")
    return df[["queue", "interval_start_utc", "volume", "aht_sec"]]


def _resample(df: pd.DataFrame, grain_min: int) -> pd.DataFrame:
    """Aggregate to the configured grain: volume summed, AHT volume-weighted."""
    df = df.copy()
    df["interval_start_utc"] = df["interval_start_utc"].dt.floor(f"{grain_min}min")
    df["_w"] = df["volume"] * df["aht_sec"]
    g = df.groupby(["queue", "interval_start_utc"], sort=True).agg(
        volume=("volume", "sum"), _w=("_w", "sum"), aht_mean=("aht_sec", "mean")).reset_index()
    g["aht_sec"] = (g["_w"] / g["volume"]).where(g["volume"] > 0, g["aht_mean"])
    return g[["queue", "interval_start_utc", "volume", "aht_sec"]]


def load_week(cfg: dict, week: str) -> pd.DataFrame:
    client = cfg["client"]
    grain = cfg["interval_minutes"]
    canon = DATA_DIR / client / f"week_{week}.csv"
    export = DATA_DIR / client / f"export_{week}.csv"
    if canon.exists():
        df = _read_canonical(canon)
    elif export.exists():
        df = _read_export(export, cfg)
    else:
        raise SystemExit(f"no data for {client} {week}: expected {canon} or {export}")

    df = _resample(df, grain)
    grid = pd.DatetimeIndex(sorted(df["interval_start_utc"].unique()))   # the week as the data delivers it
    frames = []
    for q in cfg.get("queues", QUEUES):
        part = df[df["queue"] == q].set_index("interval_start_utc").reindex(grid)
        part["queue"] = q
        part["volume"] = part["volume"].fillna(0.0)
        part["aht_sec"] = part["aht_sec"].fillna(part["aht_sec"].mean())
        frames.append(part.rename_axis("interval_start_utc").reset_index())
    out = pd.concat(frames, ignore_index=True)
    out["client"] = client
    out["interval_minutes"] = grain
    out = out.sort_values(["interval_start_utc", "queue"], kind="stable").reset_index(drop=True)
    return out[["client", "queue", "interval_start_utc", "interval_minutes", "volume", "aht_sec"]]
