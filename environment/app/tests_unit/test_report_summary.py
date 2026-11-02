import json

import pytest

from wfm.report import history, summary


def _eval(week, pri, std, hours=500.0, client="test", **viol):
    return {"client": client, "week": week, "intervals": 168, "sla": {"priority": pri, "standard": std},
            "meets_target": min(pri, std) >= 0.9, "scheduled_hours": hours, "understaffed_interval_hours": 4.0,
            "overstaffed_interval_hours": 10.0, "agents_scheduled": 20,
            "violations": {"weekly_hours": 0, "no_overlap": 0, **viol}}


def _run_output(out, ev, schedule="agent_id\n"):
    d = out / ev["client"]
    d.mkdir(parents=True, exist_ok=True)
    (d / "eval.json").write_text(json.dumps(ev))
    (d / "schedule.csv").write_text(schedule)


def test_archive_copies_the_run_and_replaces_an_earlier_archive(tmp_path):
    _run_output(tmp_path, _eval("2025-W27", 0.95, 0.93), "first\n")
    a = history.archive("test", "2025-W27", tmp_path)
    assert not a.replaced and (a.path / "schedule.csv").read_text() == "first\n"
    _run_output(tmp_path, _eval("2025-W27", 0.96, 0.93), "second\n")
    a = history.archive("test", "2025-W27", tmp_path)
    assert a.replaced and (a.path / "schedule.csv").read_text() == "second\n"
    assert history.load("test", tmp_path)[0]["sla"]["priority"] == 0.96


def test_archive_refuses_an_eval_for_another_week_or_client(tmp_path):
    _run_output(tmp_path, _eval("2025-W26", 0.95, 0.93))
    with pytest.raises(SystemExit, match="not 2025-W27"):
        history.archive("test", "2025-W27", tmp_path)
    (tmp_path / "other").mkdir()
    (tmp_path / "other" / "eval.json").write_text(json.dumps(_eval("2025-W26", 0.9, 0.9)))
    with pytest.raises(SystemExit, match="client 'test'"):
        history.archive("other", "2025-W26", tmp_path)
    with pytest.raises(SystemExit, match="run the week first"):
        history.archive("nobody", "2025-W26", tmp_path)


def test_archived_weeks_are_in_week_order_and_ignore_other_folders(tmp_path):
    for w in ("2026-W02", "2025-W52", "2026-W01"):
        _run_output(tmp_path, _eval(w, 0.9, 0.9))
        history.archive("test", w, tmp_path)
    (history.history_dir("test", tmp_path) / "scratch").mkdir()
    assert history.archived_weeks("test", tmp_path) == ["2025-W52", "2026-W01", "2026-W02"]
    assert [e["week"] for e in history.load("test", tmp_path, first="2026-W01")] == ["2026-W01", "2026-W02"]


def test_summary_per_queue_and_totals():
    evals = [_eval("2025-W27", 0.95, 0.88, 500.0), _eval("2025-W28", 0.91, 0.93, 520.0, weekly_hours=2),
             _eval("2025-W30", 0.91, 0.96, 480.0, weekly_hours=1)]
    s = summary.summarise(evals, sla_target=0.9, last="2025-W31")
    pri = next(q for q in s.queues if q.queue == "priority")
    assert (pri.min, pri.min_week, pri.max_week, pri.below_target) == (0.91, "2025-W28", "2025-W27", 0)
    std = next(q for q in s.queues if q.queue == "standard")
    assert std.below_target == 1 and abs(std.mean - (0.88 + 0.93 + 0.96) / 3) < 1e-12
    assert s.missing == ["2025-W29", "2025-W31"] and s.weeks_meeting == 2
    assert (s.hours.min, s.hours.max) == (480.0, 520.0) and s.understaffed == 12.0
    assert s.violations == {"no_overlap": 0, "weekly_hours": 3} and s.violation_weeks["weekly_hours"] == 2


def test_summary_render_and_csv():
    s = summary.summarise([_eval("2025-W27", 0.95, 0.88), _eval("2025-W28", 0.91, 0.93)], sla_target=0.9)
    text = summary.render(s, "Test Client")
    assert text.startswith("# Weekly summary - Test Client, 2025-W27 to 2025-W28")
    assert "| 2025-W27 |" in text and "1 of 2 met the evaluator target (0.90 per queue)" in text
    lines = summary.to_csv(s).splitlines()
    assert lines[0].startswith("week,intervals,sla_priority,sla_standard,meets_target")
    assert lines[1].startswith("2025-W27,168,0.95,0.88,False")


def test_summary_needs_weeks_in_order():
    with pytest.raises(SystemExit):
        summary.summarise([])
    with pytest.raises(ValueError):
        summary.summarise([_eval("2025-W28", 0.9, 0.9), _eval("2025-W27", 0.9, 0.9)])
