from datetime import timedelta

from wfm import weeks
from wfm.config import load_config
from wfm.report import volume

WEEK = "2025-W26"
CFG = {"client": "test", "name": "Test", "tz": "UTC", "interval_minutes": 60, "operating_hours": [6, 24],
       "sla": {"priority": {"target": 0.8, "seconds": 20}, "standard": {"target": 0.8, "seconds": 20}}}


def _write(path, vol=lambda t, q: 10.0 if 6 <= t.hour else 0.0, aht=lambda t, q: 300.0, hours=168, extra=()):
    """A canonical hourly UTC file for the week named in `path`."""
    mon, _ = weeks.bounds_utc(path.stem.removeprefix("week_"), "UTC")
    lines = ["client,queue,interval_start_utc,interval_minutes,volume,aht_sec"]
    for i in range(hours):
        t = mon + timedelta(hours=i)
        for q in ("priority", "standard"):
            lines.append(f"test,{q},{t:%Y-%m-%dT%H:%M:%SZ},60,{vol(t, q):.3f},{aht(t, q):.3f}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines + list(extra)) + "\n")
    return path


def test_week_totals_weighted_aht_and_peak(tmp_path):
    p = _write(tmp_path / "test" / f"week_{WEEK}.csv",
               vol=lambda t, q: (30.0 if (t.day, t.hour) == (24, 10) else 10.0) if t.hour >= 6 else 0.0,
               aht=lambda t, q: 600.0 if q == "priority" and t.hour == 10 else 300.0)
    w = volume.week_volume(p, CFG, WEEK)
    assert w.intervals == w.expected == 168 and w.issues == []
    assert w.contacts["standard"] == 7 * 18 * 10 + 20
    pri = w.contacts["priority"]
    assert abs(w.aht["priority"] - (300 * pri + 300 * (6 * 10 + 30)) / pri) < 1e-9
    assert (w.peak_local.weekday(), w.peak_local.hour) == (1, 10) and w.peak_volume == 60.0
    assert sum(w.daily) == w.total and sum(w.hourly) == w.total


def test_outage_run_is_reported_on_all_queues_together(tmp_path):
    # Tue 13:00-16:00 nothing on either queue; one queue alone at zero is not an outage
    out = lambda t: t.day == 24 and 13 <= t.hour < 16   # noqa: E731
    p = _write(tmp_path / "test" / f"week_{WEEK}.csv",
               vol=lambda t, q: 0.0 if t.hour < 6 or out(t) or (q == "priority" and t.hour < 9) else 5.0)
    runs = volume.week_volume(p, CFG, WEEK).zero_runs
    assert [(r.start_local.hour, r.end_local.hour, r.intervals, r.minutes) for r in runs] == [(13, 16, 3, 180)]


def test_closed_days_and_single_zero_intervals_are_not_outages(tmp_path):
    p = _write(tmp_path / "test" / f"week_{WEEK}.csv",
               vol=lambda t, q: 0.0 if t.hour < 6 or t.day == 29 or (t.day == 25 and t.hour == 12) else 5.0)
    assert volume.week_volume(p, CFG, WEEK).zero_runs == []
    assert len(volume.week_volume(p, CFG, WEEK, min_run=1).zero_runs) == 1


def test_file_checks(tmp_path):
    p = _write(tmp_path / "test" / f"week_{WEEK}.csv", hours=167,
               extra=["test,priority,2025-06-23T10:00:00Z,60,1.000,300.000",
                      "other,priority,2025-06-23T10:30:00Z,30,-1.000,300.000"])
    issues = volume.week_volume(p, CFG, WEEK).issues
    assert "rows for another client: other" in issues
    assert "interval_minutes 30/60 in the file, 60 in the config" in issues
    assert "1 interval start(s) off the 60-minute grain" in issues
    assert "1 duplicate queue/interval row(s)" in issues and "1 negative volume(s)" in issues
    short = _write(tmp_path / "short" / f"week_{WEEK}.csv", hours=160)
    assert volume.week_volume(short, CFG, WEEK).issues == ["160 intervals, expected 168 for the local week"]


def test_change_is_against_the_previous_file_listed(tmp_path):
    _write(tmp_path / "test" / "week_2025-W24.csv")
    _write(tmp_path / "test" / f"week_{WEEK}.csv", vol=lambda t, q: 8.0 if t.hour >= 6 else 0.0)
    (tmp_path / "test" / "notes.txt").write_text("ignored")
    rows = volume.volume_report(CFG, data_dir=tmp_path)
    assert [r.week for r in rows] == ["2025-W24", WEEK]
    assert rows[1].prev_week == "2025-W24" and abs(rows[1].change + 0.2) < 1e-9
    assert [r.week for r in volume.volume_report(CFG, first=WEEK, data_dir=tmp_path)] == [WEEK]
    text = volume.render(CFG, rows, days=True, shape=True)
    assert "-20.0 %" in text and "All files pass." in text and "## Contacts per local day" in text


def test_profile_shares_add_up(tmp_path):
    _write(tmp_path / "test" / f"week_{WEEK}.csv")
    by_day, by_hour = volume.profile(volume.volume_report(CFG, data_dir=tmp_path))
    assert abs(sum(by_day) - 1) < 1e-9 and abs(sum(by_hour) - 1) < 1e-9 and by_hour[5] == 0.0


def test_june_24_carrier_outage_in_the_canonical_files():
    # 13:40-16:20 UTC on Tue 2025-06-24: whole intervals inside the window carry no contacts
    expected = {"contoso": ("13:45", "16:15", 10), "tailspin": ("15:00", "17:00", 4),
                "adatum": ("08:00", "10:00", 2), "woodgrove": ("07:00", "09:00", 4)}
    for client, (start, end, n) in expected.items():
        (w,) = volume.volume_report(load_config(client), first=WEEK, last=WEEK)
        assert [(r.start_local.strftime("%H:%M"), r.end_local.strftime("%H:%M"), r.intervals) for r in w.zero_runs] \
            == [(start, end, n)], client
        assert w.issues == [], client
