import math

import pytest

from vendor.qlib import erlang_b, erlang_c, required_agents, service_level
from vendor.qlib.models import DEFAULT_PATIENCE_SEC, abandon_probability, asa, carried_traffic


def test_erlang_b_table_value():
    # 10 Erlangs on 15 servers: 3.65 % blocking (standard Erlang B table)
    assert erlang_b(10, 15) == pytest.approx(0.0365, abs=5e-4)


def test_erlang_c_reference_figure():
    # 1,000 calls/h, AHT 180 s, 80/20 -> 56 agents with no abandonment
    assert required_agents(1000, 3600, 180, 0.80, 20, patience_sec=0) == 56


def test_no_abandonment_reduces_to_erlang_c():
    a, n = 8.0, 11
    expected = 1 - erlang_c(a, n) * math.exp(-(n - a) * 20 / 300)
    assert service_level(a, n, 300, 20, patience_sec=0) == pytest.approx(expected)
    assert carried_traffic(a, n, 300, 0) == a


def test_abandonment_raises_service_level():
    a, n = 8.0, 10
    assert service_level(a, n, 300, 20, patience_sec=90) > service_level(a, n, 300, 20, patience_sec=0)


def test_overloaded_queue_is_stable_with_abandonment():
    sl = service_level(12.0, 10, 300, 20, patience_sec=60)
    assert 0.0 < sl < 1.0
    assert 0.0 < abandon_probability(12.0, 10, 300, 60) < 1.0


def test_default_patience():
    assert DEFAULT_PATIENCE_SEC == 90.0
    assert required_agents(300, 1800, 420, 0.90, 30) <= required_agents(300, 1800, 420, 0.90, 30, patience_sec=0)


def test_asa_finite_with_patience():
    assert math.isinf(asa(10.0, 10, 300, patience_sec=0))
    assert asa(10.0, 10, 300, patience_sec=120) < 120
