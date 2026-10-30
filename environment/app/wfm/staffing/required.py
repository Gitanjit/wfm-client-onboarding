"""Staffing: required agents per queue per interval (Erlang C at the client's SLA targets)."""
from __future__ import annotations

import pandas as pd

from wfm.staffing.erlang import required_agents


def add_required(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Append a `required` column to the canonical intervals frame."""
    interval_sec = cfg["interval_minutes"] * 60
    cap = cfg.get("occupancy_cap")  # WFM-212: read here, not yet applied in the call below
    out = df.copy()
    out["required"] = 0
    for q, g in out.groupby("queue", sort=False):
        sla = cfg["sla"][q]
        aht = g.loc[g["volume"] > 0, "aht_sec"].mean()  # smoothed handle time for the queue
        out.loc[g.index, "required"] = [
            required_agents(v, interval_sec, aht, sla["target"], sla["seconds"]) for v in g["volume"]
        ]
    out.attrs["occupancy_cap"] = cap
    return out
