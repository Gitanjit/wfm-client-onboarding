"""Queueing models. All times in seconds; traffic `a` in Erlangs (arrival rate x mean handle time).

erlang_b(a, n)        blocking probability, n servers, no queue
erlang_c(a, n)        probability that an arrival waits (M/M/n, infinite patience)
service_level(...)    fraction answered within `target_sec`; Erlang C when patience_sec == 0,
                      otherwise the Erlang A approximation below (M/M/n+M)

Erlang A approximation
----------------------
Callers abandon after an exponential patience with mean `patience_sec`. A waiting caller leaves
the queue either by being answered (rate (n - a_c) / aht) or by abandoning (rate 1 / patience_sec),
so the carried traffic a_c is found by fixed-point iteration:

    a_c = a * (1 - P_wait(a_c, n) * P(abandon | wait))
    P(abandon | wait) = (1 / patience) / ((n - a_c) / aht + 1 / patience)

Service level counts a contact as within target if it is answered within target_sec or abandons
within target_sec (short abandons are not held against the centre):

    SL = 1 - P_wait(a_c, n) * exp(-((n - a_c) / aht + 1 / patience) * target_sec)

The approximation is within a few points of the exact M/M/n+M figures for the small queues it
was written for (n < 50, patience 30-300 s). With patience_sec == 0 every formula reduces to Erlang C.
"""
from __future__ import annotations

import math

DEFAULT_PATIENCE_SEC = 90.0     # mean caller patience used when the caller does not pass one
_ITER, _TOL = 200, 1e-10


def erlang_b(a: float, n: int) -> float:
    """Blocking probability by the stable recurrence B(a, k) = a B(a, k-1) / (k + a B(a, k-1))."""
    if a <= 0:
        return 0.0
    b = 1.0
    for k in range(1, n + 1):
        b = a * b / (k + a * b)
    return b


def erlang_c(a: float, n: int) -> float:
    """Probability of waiting in M/M/n. 1.0 when n <= a (the queue grows without bound)."""
    if a <= 0:
        return 0.0
    if n <= a:
        return 1.0
    b = erlang_b(a, n)
    return n * b / (n - a * (1 - b))


def carried_traffic(a: float, n: int, aht_sec: float, patience_sec: float) -> float:
    """Traffic actually served once abandonment is taken out (Erlang A fixed point)."""
    if a <= 0 or n <= 0:
        return 0.0
    if patience_sec <= 0:
        return a
    ac = min(a, n * 0.999)
    for _ in range(_ITER):
        pw = erlang_c(ac, n)
        p_ab = abandon_given_wait(ac, n, aht_sec, patience_sec)
        nxt = a * (1.0 - pw * p_ab)
        nxt = min(nxt, n * 0.999)
        if abs(nxt - ac) < _TOL:
            return nxt
        ac = 0.5 * ac + 0.5 * nxt
    return ac


def abandon_given_wait(ac: float, n: int, aht_sec: float, patience_sec: float) -> float:
    if patience_sec <= 0:
        return 0.0
    serve_rate = max(n - ac, 0.0) / aht_sec
    leave_rate = 1.0 / patience_sec
    return leave_rate / (serve_rate + leave_rate)


def abandon_probability(a: float, n: int, aht_sec: float, patience_sec: float = DEFAULT_PATIENCE_SEC) -> float:
    """Fraction of offered contacts that abandon."""
    if a <= 0 or patience_sec <= 0:
        return 0.0
    ac = carried_traffic(a, n, aht_sec, patience_sec)
    return erlang_c(ac, n) * abandon_given_wait(ac, n, aht_sec, patience_sec)


def service_level(a: float, n: int, aht_sec: float, target_sec: float,
                  patience_sec: float = DEFAULT_PATIENCE_SEC) -> float:
    """Fraction of contacts answered (or abandoned) within target_sec."""
    if a <= 0:
        return 1.0
    if n <= 0:
        return 0.0
    if patience_sec <= 0:
        if n <= a:
            return 0.0
        return 1.0 - erlang_c(a, n) * math.exp(-(n - a) * target_sec / aht_sec)
    ac = carried_traffic(a, n, aht_sec, patience_sec)
    rate = (n - ac) / aht_sec + 1.0 / patience_sec
    return 1.0 - erlang_c(ac, n) * math.exp(-rate * target_sec)


def asa(a: float, n: int, aht_sec: float, patience_sec: float = DEFAULT_PATIENCE_SEC) -> float:
    """Mean wait of all offered contacts, seconds."""
    if a <= 0:
        return 0.0
    if patience_sec <= 0:
        return math.inf if n <= a else erlang_c(a, n) * aht_sec / (n - a)
    ac = carried_traffic(a, n, aht_sec, patience_sec)
    rate = (n - ac) / aht_sec + 1.0 / patience_sec
    return erlang_c(ac, n) / rate
