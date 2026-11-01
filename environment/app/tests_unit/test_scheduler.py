from datetime import date, datetime, timedelta, timezone

import pandas as pd

from wfm.roster import Agent
from wfm.scheduler.greedy import schedule_week
from wfm.scheduler.templates import TEMPLATES, templates_for

CFG = {"client": "test", "interval_minutes": 60, "tz": "UTC", "operating_hours": [6, 24],
       "weekly_hours": {"FT": 40, "PT": 24}, "max_consecutive_days": 5,
       "break": {"min_shift_hours": 6, "minutes": 20, "window_hours": [2, 5]}}
WEEK = "2026-W41"
DAYS = [date(2026, 10, 5) + timedelta(days=i) for i in range(7)]


def _req(need_by_day: dict) -> pd.DataFrame:
    """{date: [(start_h, end_h, agents_required)]} -> hourly requirement frame for WEEK (UTC client)."""
    rows = []
    for d in DAYS:
        for h in range(24):
            need = next((n for s, e, n in need_by_day.get(d, []) if s <= h < e), 0)
            rows.append({"queue": "priority", "interval_start_utc": datetime(d.year, d.month, d.day, h, tzinfo=timezone.utc),
                         "volume": float(need), "aht_sec": 300.0, "required": need})
    return pd.DataFrame(rows)


def test_templates_never_cross_midnight():
    assert all(0 <= s < e <= 24 for t in TEMPLATES for s, e in t.segments)


def test_templates_filtered_to_operating_hours():
    ids = {t.id for t in templates_for({"operating_hours": [7, 22]})}
    assert "E8" not in ids and "N8" not in ids and {"D8", "L8", "P6a"} <= ids


def test_scheduler_is_per_day():
    # a shift placed on Monday does not change what Tuesday gets: each local day is scheduled on its own
    mon, tue = DAYS[0], DAYS[1]
    agents = [Agent("A-001", "FT", frozenset({"priority"}))]
    with_mon = schedule_week(_req({mon: [(16, 24, 1)], tue: [(6, 14, 1)]}), CFG, agents, WEEK)
    only_tue = schedule_week(_req({tue: [(6, 14, 1)]}), CFG, agents, WEEK)
    tuesday = lambda shifts: sorted((s.template.id, s.day) for s in shifts if s.day == tue)  # noqa: E731
    assert tuesday(with_mon) == tuesday(only_tue) == [("E8", tue)]


def test_weekly_hours_cap_holds():
    agents = [Agent("A-001", "FT", frozenset({"priority"}))]
    shifts = schedule_week(_req({d: [(9, 17, 1)] for d in DAYS}), CFG, agents, WEEK)
    assert 0 < sum(s.hours for s in shifts) <= 40


def test_rest_rule_spans_days_when_configured():
    # with min_rest_hours set, Monday's late shift pushes Tuesday's start out: E8 (6 h after) is refused, L8 is taken
    mon, tue = DAYS[0], DAYS[1]
    agents = [Agent("A-001", "FT", frozenset({"priority"}))]
    shifts = schedule_week(_req({mon: [(16, 24, 1)], tue: [(6, 14, 1)]}), {**CFG, "min_rest_hours": 11}, agents, WEEK)
    assert sorted((s.template.id, s.day) for s in shifts) == [("L8", tue), ("N8", mon)]


def test_efficiency_pass_sheds_unneeded_hours():
    # one agent needed 10:00-14:00: the greedy takes the first 8 h template that covers it; the pass shortens it to P4
    agents = [Agent("A-001", "FT", frozenset({"priority"}))]
    req = _req({DAYS[0]: [(10, 14, 1)]})
    assert [s.template.id for s in schedule_week(req, CFG, agents, WEEK)] == ["E8"]
    assert [s.template.id for s in schedule_week(req, {**CFG, "efficiency_pass": "drop_shrink"}, agents, WEEK)] == ["P4"]
