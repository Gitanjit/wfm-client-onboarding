"""Weekly ops board: where each client served in an ISO week stands in the weekly cycle.

    data file -> file checks -> run -> archive -> export -> digest

One row per client whose served period covers the week (and any onboarding client whose go-live
week is on or before it), from what is on disk: data/<client>/, out/<client>/eval.json,
out/<client>/history/<week>/, out/<client>/export/ and out/<client>/notify/<week>/. Nothing is
run or changed; `next` names the first step still open. Over a range of weeks, `grid()` shows the
open step per client per week.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from wfm import config, weeks
from wfm.export import LAYOUTS, export_path
from wfm.notify import notify_dir
from wfm.registry import ClientRecord
from wfm.report import history, volume
from wfm.report import markdown as md

DONE = "done"


@dataclass
class BoardRow:
    client: str
    status: str
    config: bool
    data: str | None                  # file name of the week's data, None if missing
    intervals: str = md.DASH          # 'found/expected' for canonical files
    zero_runs: int | None = None
    checks: int | None = None         # file-check issues in the week's canonical file
    run: str = "no"                   # 'yes', 'no' or the week the last run was for
    weakest: str = md.DASH            # lowest queue attainment in the week's evaluation (run or archive)
    archived: bool = False
    exports: list[str] = field(default_factory=list)
    digest: bool = False
    expects_export: bool = True

    @property
    def next(self) -> str:
        steps = [("config", self.config), ("data", self.data is not None), ("fix data", not self.checks),
                 ("run", self.run == "yes"), ("archive", self.archived),
                 ("export", bool(self.exports) or not self.expects_export), ("notify", self.digest)]
        return next((step for step, ok in steps if not ok), DONE)


def covers(r: ClientRecord, week: str) -> bool:
    """True if the client is served in `week`, or is onboarding with go-live on or before it."""
    k = weeks.key(week)
    if r.status == "onboarding":
        return weeks.key(r.golive_week) <= k
    if k < weeks.key(weeks.week_of(r.onboarded)):
        return False
    return r.last_day is None or k <= weeks.key(weeks.week_of(r.last_day))


def _data_file(client: str, week: str) -> Path | None:
    for name in (f"week_{week}.csv", f"export_{week}.csv"):
        p = config.DATA_DIR / client / name
        if p.exists():
            return p
    return None


def _last_run(client: str, week: str, out_dir: Path) -> str:
    path = out_dir / client / "eval.json"
    if not path.exists():
        return "no"
    ev = history.read_eval(path)
    return "yes" if ev.get("week") == week and ev.get("client") == client else str(ev.get("week"))


def _weakest(ev: dict | None) -> str:
    if not ev or not ev.get("sla"):
        return md.DASH
    q, v = min(ev["sla"].items(), key=lambda kv: (kv[1], kv[0]))
    return f"{q} {md.ratio(v)}" + ("" if ev.get("meets_target") else " (below target)")


def row(r: ClientRecord, week: str, out_dir: Path) -> BoardRow:
    has_config = (config.CONFIG_DIR / f"{r.key}.yaml").exists()
    data = _data_file(r.key, week)
    b = BoardRow(r.key, r.status, has_config, data.name if data else None, expects_export=r.export_layout is not None)
    if data is not None and has_config and data.name.startswith("week_"):
        w = volume.week_volume(data, config.load_config(r.key), week)
        b.intervals, b.zero_runs, b.checks = f"{w.intervals}/{w.expected}", len(w.zero_runs), len(w.issues)
    b.run = _last_run(r.key, week, out_dir)
    archived = history.history_dir(r.key, out_dir) / week / "eval.json"
    b.archived = archived.exists()
    if b.run == "yes" or b.archived:
        b.weakest = _weakest(history.read_eval(out_dir / r.key / "eval.json" if b.run == "yes" else archived))
    b.exports = [name for name in sorted(LAYOUTS) if export_path(out_dir, r.key, week, name).exists()]
    b.digest = (notify_dir(out_dir, r.key, week) / "digest.txt").exists()
    return b


def board(records: list[ClientRecord], week: str, out_dir: Path) -> list[BoardRow]:
    return [row(r, week, out_dir) for r in records if covers(r, week)]


def _flag(ok: bool) -> str:
    return "yes" if ok else "no"


def render(rows: list[BoardRow], week: str) -> str:
    body = [[b.client, b.status, b.data or "missing", b.intervals,
             md.DASH if b.zero_runs is None else b.zero_runs, md.DASH if b.checks is None else b.checks,
             b.run if b.run in ("yes", "no") else f"last: {b.run}", b.weakest, _flag(b.archived),
             ", ".join(b.exports) or ("no" if b.expects_export else md.DASH), _flag(b.digest), b.next]
            for b in rows]
    done = sum(1 for b in rows if b.next == DONE)
    intro = (f"{len(rows)} client(s) served in the week; {done} done. Zero runs: zero-volume runs inside "
             "operating hours (see `wfm report volume`); checks: file-check issues in the week's file.")
    return md.document(md.heading(f"Ops board - {weeks.label(week)}", 1), intro,
                       md.table(["client", "status", "data", "intervals", "zero runs", "checks", "run", "weakest queue",
                                 "archived", "export", "digest", "next"], body, align="lllrrrllllll") if rows
                       else "No client is served in this week.")


def grid(records: list[ClientRecord], first: str, last: str, out_dir: Path) -> str:
    """The open step per client per week over [first, last]; blank where the client was not served."""
    span = weeks.week_range(first, last)
    if not span:
        raise SystemExit(f"empty range: {first} to {last}")
    served = [r for r in records if any(covers(r, w) for w in span)]
    body = [[w, *[row(r, w, out_dir).next if covers(r, w) else "" for r in served]] for w in span]
    done = sum(1 for line in body for cell in line[1:] if cell == DONE)
    still_open = sum(1 for line in body for cell in line[1:] if cell not in ("", DONE))
    return md.document(md.heading(f"Ops board - {first} to {last}", 1),
                       f"Next open step per client-week: {done} done, {still_open} open.",
                       md.table(["week", *[r.key for r in served]], body, align="l" * (len(served) + 1))
                       if served else "No client is served in the range.")
