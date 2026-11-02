from datetime import date

from wfm.export.base import read_schedule
from wfm.notify import write_notifications
from wfm.notify.agents import notices
from wfm.notify.digest import digest
from wfm.notify.sheets import sheets
from wfm.roster import Agent

WEEK = "2026-W23"   # Mon 1 Jun 2026
CFG = {"client": "test", "name": "Test Client", "tz": "Europe/Berlin", "operating_hours": [7, 21], "sla_target": 0.9,
       "sla": {"priority": {}, "standard": {}}, "weekly_hours": {"FT": 40, "PT": 24}}
HEADER = "agent_id,queue,segment_start_utc,segment_end_utc,template_id,segment_idx,break_start_utc,break_minutes"
ROWS = ["N-001,priority,2026-06-01T05:00:00Z,2026-06-01T11:00:00Z,P6a,0,2026-06-01T08:00:00Z,20",
        "N-002,standard,2026-06-01T06:00:00Z,2026-06-01T10:00:00Z,S44,0,,0",
        "N-002,standard,2026-06-01T14:00:00Z,2026-06-01T18:00:00Z,S44,1,,0",
        "N-001,priority,2026-06-03T07:00:00Z,2026-06-03T15:00:00Z,D8,0,2026-06-03T11:00:00Z,20"]
AGENTS = [Agent("N-001", "FT", frozenset({"priority"})), Agent("N-002", "PT", frozenset({"standard"})),
          Agent("N-003", "PT", frozenset({"standard"}))]
EVAL = {"client": "test", "week": WEEK, "sla": {"priority": 0.93, "standard": 0.88}, "meets_target": False,
        "scheduled_hours": 22.0, "agents_scheduled": 2, "understaffed_interval_hours": 6.5,
        "overstaffed_interval_hours": 1.0, "violations": {"weekly_hours": 0, "no_overlap": 2}}


def _segments(tmp_path):
    p = tmp_path / "schedule.csv"
    p.write_text("\n".join([HEADER, *ROWS]) + "\n")
    return read_schedule(p)


def test_digest_restates_the_run(tmp_path):
    text = digest(EVAL, _segments(tmp_path), CFG, WEEK, account_manager="Pat Doe", agents=AGENTS)
    assert text.startswith("To: Pat Doe (account manager); WFM team\nSubject: Test Client - schedule for 2026-W23")
    assert "standard       0.880    0.90  below" in text and "priority       0.930    0.90  met" in text
    assert "(FT 1, PT 1)" in text and "No earlier archived week to compare with." in text
    assert "no_overlap      2" in text and "weekly_hours" not in text
    assert "Mon 01 Jun       2   14.0  07:00-20:00" in text


def test_digest_compares_with_the_previous_archived_week(tmp_path):
    prev = dict(EVAL, week="2026-W22", sla={"priority": 0.95, "standard": 0.90}, scheduled_hours=24.0)
    text = digest(EVAL, _segments(tmp_path), CFG, WEEK, agents=AGENTS, previous=prev)
    assert text.startswith("To: WFM team\n")
    assert "Against 2026-W22" in text and "-0.020" in text and "-2.0" in text


def test_agent_notices_cover_the_whole_roster_in_local_time(tmp_path):
    out = notices(_segments(tmp_path), CFG, WEEK, AGENTS)
    assert sorted(out) == ["N-001", "N-002", "N-003"]
    n1 = out["N-001"]
    assert "Mon 01 Jun  07:00-13:00  priority  10:00 (20 min)" in n1      # CEST, UTC+2
    assert "Tue 02 Jun  off" in n1 and "Total: 14.0 h of a weekly cap of 40.0 h." in n1
    assert "08:00-12:00, 16:00-20:00  standard" in out["N-002"]
    assert "No shifts this week." in out["N-003"] and "cap of 24.0 h" in out["N-003"]


def test_day_sheets_count_agents_per_queue_by_local_hour(tmp_path):
    days = sheets(_segments(tmp_path), CFG, WEEK)
    assert list(days) == [date(2026, 6, d) for d in range(1, 8)]
    mon = days[date(2026, 6, 1)]
    assert "2 shift(s), 14.0 h." in mon
    assert "07:00         1         0       0" in mon and "08:00         1         1       0" in mon
    assert "10:00         1         1       1" in mon and "17:00         0         1       0" in mon
    assert "No shifts this day." in days[date(2026, 6, 2)]


def test_write_notifications_replaces_an_earlier_run(tmp_path):
    stale = tmp_path / "test" / "notify" / WEEK / "agents" / "N-099.txt"
    stale.parent.mkdir(parents=True)
    stale.write_text("old")
    written = write_notifications(tmp_path, CFG, WEEK, EVAL, _segments(tmp_path), AGENTS, "Pat Doe")
    root = tmp_path / "test" / "notify" / WEEK
    assert written[0] == root / "digest.txt" and len(written) == 1 + 3 + 7
    assert not stale.exists() and (root / "days" / "2026-06-07.txt").exists()
