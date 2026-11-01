"""Erlang C staffing maths. Pure Python, no dependencies.

Used by wfm.staffing.required to turn interval volume and handle time into required agents.

Conventions
-----------
volume        contacts arriving in the interval
interval_sec  interval length in seconds
aht_sec       average handle time in seconds (talk + wrap)
target_sec    service-level answer-time target (e.g. 20 for "80/20")
sl_target     service-level fraction (e.g. 0.80)
occupancy_cap max A/N allowed (e.g. 0.85); None disables the cap

Sanity check (standard calculator figure): 1,000 calls/hour, AHT 180 s, 80% in 20 s -> 56 agents.
"""
from __future__ import annotations

import math


def traffic_intensity(volume: float, interval_sec: float, aht_sec: float) -> float:
    """Erlangs: arrival rate x handle time."""
    if interval_sec <= 0 or aht_sec <= 0:
        return 0.0
    return (volume / interval_sec) * aht_sec


def erlang_c_prob_wait(a: float, n: int) -> float:
    """Probability that an arriving contact must wait, with traffic a Erlangs and n agents.

    Returns 1.0 when n <= a (unstable queue). Terms are accumulated iteratively to avoid
    overflow in a**n / n! for large n.
    """
    if a <= 0:
        return 0.0
    if n <= a:
        return 1.0
    term = 1.0          # a^0 / 0!
    s = 1.0             # sum_{k=0}^{n-1} a^k / k!
    for k in range(1, n):
        term *= a / k
        s += term
    term *= a / n       # a^n / n!
    top = term * n / (n - a)
    return top / (s + top)


def service_level(a: float, n: int, aht_sec: float, target_sec: float) -> float:
    """Fraction of contacts answered within target_sec."""
    if a <= 0:
        return 1.0
    if n <= a:
        return 0.0
    pw = erlang_c_prob_wait(a, n)
    return 1.0 - pw * math.exp(-(n - a) * target_sec / aht_sec)


def asa(a: float, n: int, aht_sec: float) -> float:
    """Average speed of answer in seconds."""
    if a <= 0:
        return 0.0
    if n <= a:
        return float("inf")
    return erlang_c_prob_wait(a, n) * aht_sec / (n - a)


def occupancy(a: float, n: int) -> float:
    return 0.0 if n <= 0 else a / n


def required_agents(
    volume: float,
    interval_sec: float,
    aht_sec: float,
    sl_target: float,
    target_sec: float,
    occupancy_cap: float | None = None,
    max_agents: int = 2000,
) -> int:
    """Smallest n meeting the service-level target and (if given) the occupancy cap."""
    a = traffic_intensity(volume, interval_sec, aht_sec)
    if a <= 0:
        return 0
    n = max(1, math.ceil(a))
    while n < max_agents:
        ok_sl = service_level(a, n, aht_sec, target_sec) >= sl_target
        ok_occ = occupancy_cap is None or occupancy(a, n) <= occupancy_cap
        if ok_sl and ok_occ:
            return n
        n += 1
    return n


if __name__ == "__main__":
    # Standard check: 1000 calls/hour, AHT 180 s, 80/20 -> 56 agents
    n = required_agents(volume=1000, interval_sec=3600, aht_sec=180, sl_target=0.80, target_sec=20)
    a = traffic_intensity(1000, 3600, 180)
    print(f"A={a:.2f} Erlangs, required={n}, SL={service_level(a, n, 180, 20):.3f}, "
          f"ASA={asa(a, n, 180):.1f}s, occ={occupancy(a, n):.3f}")
    assert n == 56, n
    # With an occupancy cap the answer can only go up
    n2 = required_agents(1000, 3600, 180, 0.80, 20, occupancy_cap=0.85)
    assert n2 >= n
    print("ok")
