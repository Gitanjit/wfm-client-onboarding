from wfm import board, cli, registry


def _rows(week, out):
    return {b.client: b for b in board.board(list(registry.load_registry().values()), week, out)}


def test_board_lists_the_clients_served_that_week(tmp_path):
    rows = _rows("2025-W30", tmp_path)
    assert list(rows) == ["contoso", "tailspin", "adatum", "woodgrove"]
    assert rows["contoso"].data == "week_2025-W30.csv" and rows["contoso"].intervals == "672/672"
    assert (rows["contoso"].zero_runs, rows["contoso"].checks, rows["contoso"].next) == (0, 0, "run")
    assert rows["tailspin"].data is None and rows["tailspin"].next == "data"
    assert list(_rows("2026-W39", tmp_path)) == ["contoso", "fabrikam", "wingtip"]
    text = board.render(list(rows.values()), "2025-W30")
    assert text.startswith("# Ops board - 2025-W30 (Mon 21 Jul - Sun 27 Jul 2025)") and "0 done" in text


def test_board_follows_the_weekly_cycle(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "OUT_DIR", tmp_path)
    week = "2026-W39"
    cli.main(["run", "--client", "fabrikam", "--week", week])
    assert _rows(week, tmp_path)["fabrikam"].next == "archive"
    cli.main(["report", "archive", "--client", "fabrikam", "--week", week])
    cli.main(["export", "--client", "fabrikam", "--week", week])
    assert _rows(week, tmp_path)["fabrikam"].next == "notify"
    cli.main(["notify", "--client", "fabrikam", "--week", week])
    fab = _rows(week, tmp_path)["fabrikam"]
    assert (fab.run, fab.archived, fab.exports, fab.digest, fab.next) == ("yes", True, ["activity_csv"], True, "done")
    assert _rows(week, tmp_path)["wingtip"].run == "no"
    assert fab.weakest.startswith("priority 0.") or fab.weakest.startswith("standard 0.")
    cli.main(["clients", "--board", "--week", week])
    assert "| fabrikam | live   | week_2026-W39.csv |" in (tmp_path / "reports" / f"board_{week}.md").read_text()


def test_board_over_a_range_shows_the_open_step_per_week(tmp_path):
    text = board.grid(list(registry.load_registry().values()), "2025-W03", "2025-W05", tmp_path)
    rows = [line.split("|")[1:-1] for line in text.splitlines() if line.startswith("| 2025-W")]
    assert text.splitlines()[4].split("|")[1:-1][1].strip() == "contoso" and len(rows) == 3
    assert [[c.strip() for c in r] for r in rows] == [["2025-W03", "data", "run"], ["2025-W04", "data", "run"],
                                                      ["2025-W05", "run", "run"]]
    assert "0 done, 6 open." in text
