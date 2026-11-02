import json

import pytest

from wfm import cli


@pytest.fixture
def out(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "OUT_DIR", tmp_path)
    return tmp_path


def test_clients_lists_the_registry(capsys):
    cli.main(["clients", "--status", "retired"])
    lines = capsys.readouterr().out.splitlines()
    assert [line.split()[0] for line in lines[2:]] == ["tailspin", "adatum", "woodgrove"]
    cli.main(["clients", "--markdown"])
    assert "| wingtip   | Wingtip Toys" in capsys.readouterr().out
    cli.main(["clients", "--active-on", "2025-06-24"])
    assert [line.split()[0] for line in capsys.readouterr().out.splitlines()[2:]] == \
        ["contoso", "tailspin", "adatum", "woodgrove"]


def test_clients_check_passes(capsys):
    # Northwind's config and roster are in (go-live 2026-W44): nothing pending
    cli.main(["clients", "--check"])
    text = capsys.readouterr().out
    assert "8 client(s) checked: 0 error(s), 0 warning(s), 0 pending" in text


def test_week_arguments_are_validated():
    with pytest.raises(SystemExit) as e:
        cli.main(["report", "archive", "--client", "fabrikam", "--week", "2026-44"])
    assert e.value.code == 2


def test_weekly_cycle_run_archive_export_notify_summary(out, capsys):
    cli.main(["run", "--client", "fabrikam", "--week", "2026-W39"])
    cli.main(["report", "archive", "--client", "fabrikam", "--week", "2026-W39"])
    cli.main(["export", "--client", "fabrikam", "--week", "2026-W39"])               # registry layout
    cli.main(["export", "--client", "fabrikam", "--week", "2026-W39", "--layout", "all"])
    cli.main(["notify", "--client", "fabrikam", "--week", "2026-W39"])
    cli.main(["report", "summary", "--client", "fabrikam", "--csv"])
    capsys.readouterr()
    assert (out / "fabrikam" / "history" / "2026-W39" / "schedule.csv").exists()
    assert (out / "fabrikam" / "export" / "activity_csv_2026-W39.csv").exists()
    assert json.loads((out / "fabrikam" / "export" / "segments_json_2026-W39.json").read_text())["tz"] == "America/New_York"
    assert len(list((out / "fabrikam" / "export").glob("*_2026-W39.manifest.json"))) == 4
    digest = (out / "fabrikam" / "notify" / "2026-W39" / "digest.txt").read_text()
    assert digest.startswith("To: Ruth Abara (account manager); WFM team")
    assert len(list((out / "fabrikam" / "notify" / "2026-W39" / "agents").glob("FA-*.txt"))) == 28
    assert (out / "fabrikam" / "reports" / "summary_2026-W39_2026-W39.md").exists()
    assert (out / "fabrikam" / "reports" / "summary_2026-W39_2026-W39.csv").exists()


def test_compare_fails_on_change_only_when_the_schedule_moved(out, capsys):
    cli.main(["run", "--client", "fabrikam", "--week", "2026-W39"])
    cli.main(["report", "archive", "--client", "fabrikam", "--week", "2026-W39"])
    cli.main(["report", "compare", "--client", "fabrikam", "--week", "2026-W39", "--fail-on-change"])
    assert "Schedules are byte-identical." in capsys.readouterr().out
    sched = out / "fabrikam" / "schedule.csv"
    sched.write_text("".join(sched.read_text().splitlines(keepends=True)[:-1]))
    with pytest.raises(SystemExit) as e:
        cli.main(["report", "compare", "--client", "fabrikam", "--week", "2026-W39", "--fail-on-change"])
    assert e.value.code == 1


def test_export_and_notify_refuse_another_weeks_run(out):
    cli.main(["run", "--client", "fabrikam", "--week", "2026-W37"])
    for cmd in (["export", "--client", "fabrikam", "--week", "2026-W39"],
                ["notify", "--client", "fabrikam", "--week", "2026-W39"]):
        with pytest.raises(SystemExit, match="is for 2026-W37, not 2026-W39"):
            cli.main(cmd)


def test_report_volume_prints_the_weeks(capsys):
    cli.main(["report", "volume", "--client", "contoso", "--from", "2025-W26", "--to", "2025-W26"])
    text = capsys.readouterr().out
    assert text.startswith("# Volume - Contoso") and "| 2025-W26 | Tue 2025-06-24 | 13:45 | 16:15 |" in text
