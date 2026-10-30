"""Staffing: required agents per queue per interval (Erlang C at the client's SLA targets)."""
from __future__ import annotations

import pandas as pd

from wfm.staffing.erlang import required_agents


def _handle_time(g: pd.DataFrame, mode: str) -> pd.Series:
    """Handle time per interval under the configured smoothing (`aht_smoothing`):
    `queue_mean` (default) — the queue's mean AHT over intervals with volume; `interval` — each row's own AHT."""
    if mode == "interval":
        return g["aht_sec"]
    return pd.Series(g.loc[g["volume"] > 0, "aht_sec"].mean(), index=g.index)


def add_required(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Append a `required` column to the canonical intervals frame."""
    interval_sec = cfg["interval_minutes"] * 60
    cap = cfg.get("occupancy_cap")  # WFM-212: applied per interval
    mode = cfg.get("aht_smoothing", "queue_mean")
    out = df.copy()
    out["required"] = 0
    for q, g in out.groupby("queue", sort=False):
        sla = cfg["sla"][q]
        # the handle-time series is used per interval (WFM-198 collapsed it to one value, so `interval` had no effect)
        aht = _handle_time(g, mode)
        out.loc[g.index, "required"] = [
            required_agents(v, interval_sec, a, sla["target"], sla["seconds"], cap)
            for v, a in zip(g["volume"], aht)
        ]
    out.attrs["occupancy_cap"] = cap
    return out
