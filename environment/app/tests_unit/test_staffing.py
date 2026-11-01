import pandas as pd

from wfm.staffing.erlang import required_agents
from wfm.staffing.required import add_required

CFG = {"interval_minutes": 60, "occupancy_cap": 0.85,
       "sla": {"priority": {"target": 0.80, "seconds": 20}, "standard": {"target": 0.80, "seconds": 20}}}


def test_erlang_reference_figure():
    # 1,000 calls/h, AHT 180 s, 80/20 -> 56 agents (the standard calculator figure)
    assert required_agents(1000, 3600, 180, 0.80, 20) == 56


def test_zero_volume_needs_no_agents():
    assert required_agents(0, 3600, 300, 0.80, 20) == 0


def test_required_uses_queue_mean_aht():
    # WFM-198: two intervals with the same volume get the same requirement whatever their own AHT
    df = pd.DataFrame({
        "queue": ["priority", "priority"],
        "interval_start_utc": pd.to_datetime(["2026-10-05T10:00:00Z", "2026-10-05T11:00:00Z"]),
        "volume": [100.0, 100.0], "aht_sec": [200.0, 400.0],
    })
    req = add_required(df, CFG)
    assert req["required"].iloc[0] == req["required"].iloc[1] == required_agents(100, 3600, 300, 0.80, 20)
