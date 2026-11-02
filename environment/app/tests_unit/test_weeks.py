from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from wfm import weeks


def test_parse_and_format_round_trip():
    assert weeks.parse("2025-W03") == (2025, 3)
    assert weeks.fmt(2025, 3) == "2025-W03"
    assert weeks.weeks_in_year(2026) == 53 and weeks.weeks_in_year(2025) == 52


def test_parse_rejects_malformed_or_missing_weeks():
    for bad in ("2025-W53", "2025-W00", "2025W10", "2025-W1", ""):
        with pytest.raises(ValueError):
            weeks.parse(bad)


def test_week_arithmetic_across_year_end():
    assert weeks.week_of(date(2025, 12, 29)) == "2026-W01"
    assert weeks.add_weeks("2025-W52", 1) == "2026-W01"
    assert weeks.add_weeks("2026-W01", -1) == "2025-W52"
    assert weeks.week_range("2025-W51", "2026-W02") == ["2025-W51", "2025-W52", "2026-W01", "2026-W02"]
    assert weeks.week_range("2025-W10", "2025-W09") == []


def test_local_week_bounds_follow_dst():
    # Europe/Dublin springs forward on Sun 2025-03-30: the local week is 167 hours long
    start, end = weeks.bounds_utc("2025-W13", "Europe/Dublin")
    assert start == datetime(2025, 3, 24, 0, 0, tzinfo=timezone.utc)
    assert end == datetime(2025, 3, 30, 23, 0, tzinfo=timezone.utc)
    assert weeks.expected_intervals("2025-W13", "Europe/Dublin", 30) == 334
    assert weeks.expected_intervals("2025-W44", "America/Denver", 60) == 169   # fall-back, Sun 2025-11-02
    assert weeks.expected_intervals("2025-W26", "UTC", 15) == 672


def test_operating_hours_are_local_wall_clock():
    t = datetime(2025, 6, 24, 13, 0, tzinfo=timezone.utc)          # 07:00 in Denver (MDT)
    assert weeks.local_hour(t, "America/Denver") == 7.0
    assert weeks.in_operating_hours(t, "America/Denver", [6, 24])
    assert not weeks.in_operating_hours(t, "America/Los_Angeles", [7, 21])   # 06:00 there


def test_hour_starts_skip_the_missing_spring_forward_hour():
    hours = [h for h, _ in weeks.hour_starts(date(2025, 3, 30), "Europe/Dublin")]
    assert 1 not in hours and len(hours) == 23
    assert [h for h, _ in weeks.hour_starts(date(2025, 3, 30), "Europe/Dublin", (7, 10))] == [7, 8, 9]


def test_offset_and_midnight_formatting():
    loc = datetime(2025, 11, 2, 0, 0, tzinfo=ZoneInfo("America/Denver"))
    assert weeks.offset(loc) == "-06:00"
    assert weeks.hhmm(loc, date(2025, 11, 1)) == "24:00"
    assert weeks.hhmm(loc) == "00:00"
    assert weeks.label("2025-W26") == "2025-W26 (Mon 23 Jun - Sun 29 Jun 2025)"
