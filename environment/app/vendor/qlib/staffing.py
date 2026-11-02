"""Staffing helpers built on qlib.models."""
from __future__ import annotations

from .models import DEFAULT_PATIENCE_SEC, carried_traffic, service_level


def traffic(volume: float, interval_sec: float, aht_sec: float) -> float:
    if interval_sec <= 0 or aht_sec <= 0:
        return 0.0
    return volume * aht_sec / interval_sec


def achieved(volume: float, interval_sec: float, aht_sec: float, agents: int, target_sec: float,
             patience_sec: float | None = None) -> float:
    """Service level `agents` achieve on an interval's volume."""
    p = DEFAULT_PATIENCE_SEC if patience_sec is None else patience_sec
    return service_level(traffic(volume, interval_sec, aht_sec), agents, aht_sec, target_sec, p)


def required_agents(volume: float, interval_sec: float, aht_sec: float, sl_target: float, target_sec: float,
                    occupancy_cap: float | None = None, patience_sec: float | None = None,
                    max_agents: int = 2000) -> int:
    """Smallest n whose service level meets sl_target and whose occupancy (carried traffic / n)
    is within occupancy_cap. patience_sec=None uses the library default."""
    p = DEFAULT_PATIENCE_SEC if patience_sec is None else patience_sec
    a = traffic(volume, interval_sec, aht_sec)
    if a <= 0:
        return 0
    n = 1
    while n < max_agents:
        if service_level(a, n, aht_sec, target_sec, p) >= sl_target:
            if occupancy_cap is None or carried_traffic(a, n, aht_sec, p) / n <= occupancy_cap:
                return n
        n += 1
    return n
