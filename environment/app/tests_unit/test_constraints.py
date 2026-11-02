from datetime import datetime, timezone

from wfm.constraints import cover, floor, uncovered

CFG = {"tz": "UTC", "operating_hours": [6, 24], "cross_skill_weight": 0.5,
       "min_cover": {"chat": {"agents": 2, "hours": [20, 24]}}}


def test_floor_applies_inside_its_hours_only():
    assert floor("chat", datetime(2025, 7, 21, 21, 0, tzinfo=timezone.utc), CFG) == 2
    assert floor("chat", datetime(2025, 7, 21, 12, 0, tzinfo=timezone.utc), CFG) == 0
    assert floor("voice", datetime(2025, 7, 21, 21, 0, tzinfo=timezone.utc), CFG) == 0


def test_cross_skilled_agents_count_half_toward_the_floor():
    # PR #31: one chat agent plus two voice agents holding the chat skill meet a floor of two
    assert cover(1, 2, CFG) == 2.0
    assert uncovered(required=1, floor_need=2, on_queue=1, cross_skilled=2, cfg=CFG) == 0.0


def test_staffing_requirement_is_never_met_by_cross_skilled_agents():
    assert uncovered(required=3, floor_need=2, on_queue=1, cross_skilled=6, cfg=CFG) == 2.0
