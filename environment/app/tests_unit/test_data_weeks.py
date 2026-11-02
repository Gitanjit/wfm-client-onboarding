"""The canonical week files against the facts recorded for each client: DST weeks, the outage on
Tue 2026-04-14 and file checks for every week on file."""

from wfm import weeks
from wfm.config import load_config
from wfm.report import volume

CLIENTS = ["contoso", "tailspin", "adatum", "woodgrove", "fabrikam", "proseware", "wingtip"]


def test_every_week_file_passes_the_file_checks():
    for client in CLIENTS:
        rows = volume.volume_report(load_config(client))
        assert rows and {r.week: r.issues for r in rows if r.issues} == {}, client


def test_dst_weeks_have_the_local_week_length():
    for client, week, intervals in [("tailspin", "2025-W13", 334), ("tailspin", "2025-W43", 338),
                                    ("adatum", "2025-W44", 169), ("woodgrove", "2025-W44", 338),
                                    ("fabrikam", "2026-W10", 167), ("proseware", "2026-W13", 334)]:
        (w,) = volume.volume_report(load_config(client), first=week, last=week)
        assert w.intervals == w.expected == intervals, (client, week)


def test_arizona_weeks_never_change_length():
    cfg = load_config("wingtip")
    assert {r.intervals for r in volume.volume_report(cfg)} == {336}
    assert weeks.expected_intervals("2026-W11", cfg["tz"], 30) == 336    # US spring-forward week


def test_april_14_outage_in_the_canonical_files():
    # 13:00-15:30 UTC on Tue 2026-04-14
    expected = {"fabrikam": ("09:00", "11:00", 2), "proseware": ("15:00", "17:30", 5), "wingtip": ("06:00", "08:30", 5)}
    for client, (start, end, n) in expected.items():
        (w,) = volume.volume_report(load_config(client), first="2026-W16", last="2026-W16")
        assert [(r.start_local.strftime("%H:%M"), r.end_local.strftime("%H:%M"), r.intervals) for r in w.zero_runs] \
            == [(start, end, n)], client


def test_outages_are_the_only_zero_runs_on_file():
    found = {(c, r.week) for c in CLIENTS for r in volume.volume_report(load_config(c)) if r.zero_runs}
    assert found == {("contoso", "2025-W26"), ("tailspin", "2025-W26"), ("adatum", "2025-W26"),
                     ("woodgrove", "2025-W26"), ("fabrikam", "2026-W16"), ("proseware", "2026-W16"),
                     ("wingtip", "2026-W16")}
