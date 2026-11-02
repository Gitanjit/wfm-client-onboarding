from datetime import datetime, timedelta, timezone

import pandas as pd

from wfm.evaluate.metrics import evaluate
from wfm.roster import Agent

T0 = datetime(2025, 9, 1, 12, tzinfo=timezone.utc)
CFG = {"client": "test", "interval_minutes": 60, "tz": "UTC", "sla_target": 0.9,
       "weekly_hours": {"FT": 40, "PT": 24}, "max_consecutive_days": 5}
AGENTS = [Agent(f"A-{i}", "FT", frozenset({"priority"})) for i in range(3)]


def _req(required):
    return pd.DataFrame({"queue": "priority", "volume": 10.0, "aht_sec": 300.0, "required": required,
                         "interval_start_utc": [T0 + timedelta(hours=i) for i in range(len(required))]})


def _sched(n_agents, hours):
    return pd.DataFrame([{"agent_id": f"A-{i}", "queue": "priority",
                          "segment_start_utc": T0.strftime("%Y-%m-%dT%H:%M:%SZ"),
                          "segment_end_utc": (T0 + timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                          "template_id": "X", "segment_idx": 0, "break_start_utc": "", "break_minutes": 0}
                         for i in range(n_agents)])


def test_service_level_basis_counts_met_intervals():
    res = evaluate(_req([3, 4]), _sched(3, 2), CFG, AGENTS, "2025-W36")
    assert res["sla"]["priority"] == 0.5


def test_coverage_basis_scores_scheduled_over_required():
    # PR #47: three agents against a requirement of four scores 0.75 for that hour
    res = evaluate(_req([3, 4]), _sched(3, 2), {**CFG, "attainment_basis": "coverage"}, AGENTS, "2025-W36")
    assert res["sla"]["priority"] == round((1 + 0.75) / 2, 3)
