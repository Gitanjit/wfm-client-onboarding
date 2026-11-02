import csv
import hashlib
import io
import json

import pytest

from wfm.export import LAYOUTS, export_schedule
from wfm.export import base
from wfm.roster import Agent

WEEK = "2025-W44"   # US fall-back on Sun 2025-11-02
CFG = {"client": "test", "tz": "America/New_York"}
HEADER = "agent_id,queue,segment_start_utc,segment_end_utc,template_id,segment_idx,break_start_utc,break_minutes"
ROWS = [
    "A-002,priority,2025-10-27T12:00:00Z,2025-10-27T16:00:00Z,S44,0,2025-10-27T14:00:00Z,20",
    "A-002,priority,2025-10-27T20:00:00Z,2025-10-28T00:00:00Z,S44,1,,0",
    "A-003,standard,2025-10-28T20:00:00Z,2025-10-29T04:00:00Z,N8,0,2025-10-29T00:00:00Z,20",
    "A-001,standard,2025-11-01T13:00:00Z,2025-11-01T21:00:00Z,D8,0,2025-11-01T16:50:00Z,20",
    "A-001,standard,2025-11-02T14:00:00Z,2025-11-02T22:00:00Z,D8,0,2025-11-02T18:00:00Z,20",
]
AGENTS = [Agent("A-001", "FT", frozenset({"standard"})), Agent("A-002", "PT", frozenset({"priority"})),
          Agent("A-003", "FT", frozenset({"standard"})), Agent("A-004", "PT", frozenset({"standard"}))]


@pytest.fixture
def sched(tmp_path):
    p = tmp_path / "schedule.csv"
    p.write_text("\n".join([HEADER, *ROWS]) + "\n")
    return p


def test_segments_group_into_shifts_per_local_day(sched):
    shifts = base.shifts(base.read_schedule(sched), CFG["tz"])
    assert [(s.agent_id, s.template_id, str(s.day), len(s.segments), s.hours) for s in shifts] == [
        ("A-001", "D8", "2025-11-01", 1, 8.0), ("A-001", "D8", "2025-11-02", 1, 8.0),
        ("A-002", "S44", "2025-10-27", 2, 8.0), ("A-003", "N8", "2025-10-28", 1, 8.0)]


def test_a_break_splits_its_segment_into_work_break_work(sched):
    seg = base.read_schedule(sched)[0]   # A-001 Saturday
    assert [(a.kind, a.minutes) for a in base.activities(seg)] == [("WORK", 230), ("BREAK", 20), ("WORK", 230)]


def test_activity_csv_takes_the_offset_per_row_across_the_dst_change(sched):
    rows = list(csv.DictReader(io.StringIO(LAYOUTS["activity_csv"].render(base.read_schedule(sched), CFG, WEEK))))
    sat = [r for r in rows if r["agent_id"] == "A-001" and r["date_local"] == "2025-11-01"]
    sun = [r for r in rows if r["agent_id"] == "A-001" and r["date_local"] == "2025-11-02"]
    assert {r["utc_offset"] for r in sat} == {"-04:00"} and {r["utc_offset"] for r in sun} == {"-05:00"}
    assert sat[0]["start_local"] == sun[0]["start_local"].replace("11-02", "11-01") == "2025-11-01 09:00"
    assert [r["activity"] for r in sun] == ["WORK", "BREAK", "WORK"] and sun[1]["start_local"] == "2025-11-02 13:00"


def test_roster_grid_lists_the_whole_roster(sched):
    rows = list(csv.reader(io.StringIO(LAYOUTS["roster_grid_csv"].render(base.read_schedule(sched), CFG, WEEK, AGENTS))))
    assert rows[0][2] == "Mon 2025-10-27" and rows[0][-1] == "hours"
    grid = {r[0]: r for r in rows[1:]}
    assert grid["A-002"][2] == "08:00-12:00 / 16:00-20:00" and grid["A-002"][1] == "PT"
    assert grid["A-003"][3] == "16:00-24:00"
    assert grid["A-001"][7:9] == ["09:00-17:00", "09:00-17:00"] and grid["A-001"][-1] == "16.0"
    assert grid["A-004"][2:9] == ["OFF"] * 7 and grid["A-004"][-1] == "0.0"


def test_segments_json_is_stable_and_carries_local_offsets(sched):
    segs = base.read_schedule(sched)
    text = LAYOUTS["segments_json"].render(segs, CFG, WEEK)
    assert text == LAYOUTS["segments_json"].render(list(reversed(segs)), CFG, WEEK)
    doc = json.loads(text)
    a1 = doc["agents"][0]
    assert a1["agent_id"] == "A-001" and a1["hours"] == 16.0
    assert a1["segments"][1]["start_local"] == "2025-11-02T09:00:00-05:00"
    assert a1["segments"][0]["breaks"][0]["start_local"] == "2025-11-01T12:50:00-04:00"


def test_export_writes_the_file_and_its_control_totals(sched, tmp_path):
    path = export_schedule(sched, CFG, WEEK, "activity_csv", tmp_path / "out", AGENTS)
    assert path == tmp_path / "out" / "test" / "export" / f"activity_csv_{WEEK}.csv"
    m = json.loads(path.with_name(f"activity_csv_{WEEK}.manifest.json").read_text())
    assert (m["agents"], m["segments"], m["breaks"], m["scheduled_hours"]) == (3, 5, 4, 32.0)
    assert m["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()


def test_export_refuses_another_week_unknown_agents_and_layouts(sched, tmp_path):
    with pytest.raises(SystemExit, match="outside 2025-W45"):
        export_schedule(sched, CFG, "2025-W45", "activity_csv", tmp_path)
    with pytest.raises(SystemExit, match="not on the test roster: A-003"):
        export_schedule(sched, CFG, WEEK, "activity_csv", tmp_path, [a for a in AGENTS if a.agent_id != "A-003"])
    with pytest.raises(SystemExit, match="unknown export layout"):
        export_schedule(sched, CFG, WEEK, "fixed_width", tmp_path)
