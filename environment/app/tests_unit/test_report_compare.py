import json

import pytest

from wfm.report import compare, history

WEEK = "2025-W38"
HEADER = "agent_id,queue,segment_start_utc,segment_end_utc,template_id,segment_idx,break_start_utc,break_minutes"
BASE = ["B-001,priority,2025-09-15T09:00:00Z,2025-09-15T17:00:00Z,D8,0,2025-09-15T12:50:00Z,20",
        "B-002,standard,2025-09-16T06:00:00Z,2025-09-16T14:00:00Z,E8,0,2025-09-16T10:00:00Z,20"]


def _eval(week, pri=0.95, hours=16.0):
    return {"client": "test", "week": week, "intervals": 168, "sla": {"priority": pri, "standard": 0.93},
            "meets_target": True, "scheduled_hours": hours, "understaffed_interval_hours": 2.0,
            "overstaffed_interval_hours": 3.0, "agents_scheduled": 2, "violations": {"weekly_hours": 0}}


def _run(out, ev, rows):
    d = out / "test"
    d.mkdir(parents=True, exist_ok=True)
    (d / "eval.json").write_text(json.dumps(ev))
    (d / "schedule.csv").write_text("\n".join([HEADER, *rows]) + "\n")


def test_an_unchanged_rerun_is_reported_identical(tmp_path):
    _run(tmp_path, _eval(WEEK), BASE)
    history.archive("test", WEEK, tmp_path)
    c = compare.compare("test", compare.archived_side("test", WEEK, tmp_path),
                        compare.current_side("test", WEEK, tmp_path), "UTC")
    assert c.same_schedule and not c.changed and c.agents == []
    assert "Schedules are byte-identical." in compare.render(c)


def test_a_moved_shift_shows_per_agent_weekday_and_hour(tmp_path):
    _run(tmp_path, _eval(WEEK), BASE)
    history.archive("test", WEEK, tmp_path)
    moved = [BASE[0], "B-002,standard,2025-09-16T13:00:00Z,2025-09-16T21:00:00Z,L8,0,2025-09-16T17:00:00Z,20"]
    _run(tmp_path, _eval(WEEK, pri=0.94), moved)
    c = compare.compare("test", compare.archived_side("test", WEEK, tmp_path),
                        compare.current_side("test", WEEK, tmp_path), "UTC")
    assert c.changed and [(d.agent_id, d.days) for d in c.agents] == [("B-002", ("Tue",))]
    cover = dict(c.headcount_change)
    assert cover[6][1] == -1 and cover[14][1] == +1 and 13 not in cover
    assert ("E8", 1, 0) in c.templates and ("L8", 0, 1) in c.templates
    text = compare.render(c)
    assert "| attainment priority" in text and "-0.010" in text and "## Agents with changed shifts" in text


def test_week_on_week_compares_by_weekday(tmp_path):
    _run(tmp_path, _eval(WEEK), BASE)
    history.archive("test", WEEK, tmp_path)
    nxt = [r.replace("2025-09-15", "2025-09-22").replace("2025-09-16", "2025-09-23") for r in BASE]
    _run(tmp_path, _eval("2025-W39", hours=16.0), nxt)
    history.archive("test", "2025-W39", tmp_path)
    c = compare.compare("test", compare.archived_side("test", WEEK, tmp_path),
                        compare.archived_side("test", "2025-W39", tmp_path), "UTC")
    assert c.agents == [] and c.headcount_change == [] and not c.same_schedule
    with pytest.raises(SystemExit):
        compare.current_side("test", WEEK, tmp_path)   # the current run is 2025-W39
