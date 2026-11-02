"""Evaluation history: out/<client>/eval.json archived per week.

`wfm run` overwrites out/<client>/eval.json and schedule.csv on every run. After a week is run and
checked, `wfm report archive` copies both into out/<client>/history/<week>/, which is what the
multi-week summary reads. Re-archiving a week (after a re-run on corrected data) replaces it.
"""
from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from wfm import weeks

HISTORY = "history"
FILES = ("eval.json", "schedule.csv")


@dataclass(frozen=True)
class Archived:
    week: str
    path: Path          # out/<client>/history/<week>/
    replaced: bool      # an earlier archive of the same week was overwritten


def read_eval(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        raise SystemExit(f"no {path}: run the week first (python -m wfm run ...)") from None
    except json.JSONDecodeError as e:
        raise SystemExit(f"{path}: not valid JSON ({e})") from None


def check_eval(ev: dict, client: str, week: str, path: Path) -> None:
    """The eval must be the one for this client-week; `run` leaves the last week run in place."""
    if ev.get("client") != client:
        raise SystemExit(f"{path} is for client {ev.get('client')!r}, not {client!r}")
    if ev.get("week") != week:
        raise SystemExit(f"{path} is for {ev.get('week')}, not {week}: run {week} first")


def history_dir(client: str, out_dir: Path) -> Path:
    return out_dir / client / HISTORY


def archive(client: str, week: str, out_dir: Path) -> Archived:
    weeks.parse(week)
    src = out_dir / client
    ev = read_eval(src / "eval.json")
    check_eval(ev, client, week, src / "eval.json")
    dest = history_dir(client, out_dir) / week
    replaced = dest.exists()
    dest.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        if (src / name).exists():
            shutil.copyfile(src / name, dest / name)
        elif (dest / name).exists():
            (dest / name).unlink()          # do not leave an older week's file next to the new eval
    return Archived(week, dest, replaced)


def archived_weeks(client: str, out_dir: Path) -> list[str]:
    root = history_dir(client, out_dir)
    if not root.is_dir():
        return []
    found = []
    for p in root.iterdir():
        if not (p / "eval.json").exists():
            continue
        try:
            weeks.parse(p.name)
        except ValueError:
            continue
        found.append(p.name)
    return sorted(found, key=weeks.key)


def load(client: str, out_dir: Path, first: str | None = None, last: str | None = None) -> list[dict]:
    """Archived evals in week order, limited to [first, last] when given."""
    out = []
    for w in archived_weeks(client, out_dir):
        if (first and weeks.key(w) < weeks.key(first)) or (last and weeks.key(w) > weeks.key(last)):
            continue
        path = history_dir(client, out_dir) / w / "eval.json"
        ev = read_eval(path)
        check_eval(ev, client, w, path)
        out.append(ev)
    return out
