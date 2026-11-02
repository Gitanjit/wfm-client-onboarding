"""Schedule exporters: a run's out/<client>/schedule.csv in the layouts clients load into their ACDs.

Off the `wfm run` path (docs/adr/0006-schedule-export-layouts.md): an exporter reads schedule.csv
only, never re-runs staffing or scheduling, and writes out/<client>/export/<layout>_<week>.<ext>
(a per-agent layout writes a folder, out/<client>/export/<layout>_<week>/, one file per agent).
Each client's layout is recorded in clients/registry.yaml (`export_layout`).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from wfm.export import activity_csv, agent_ics, roster_grid, segments_json
from wfm.export.base import check_week, read_schedule


@dataclass(frozen=True)
class Layout:
    name: str
    extension: str
    render: Callable      # (segments, cfg, week, agents) -> text, or {file name: text} when per_agent
    summary: str
    per_agent: bool = False


LAYOUTS: dict[str, Layout] = {
    "activity_csv": Layout("activity_csv", "csv", activity_csv.render, "one row per work/break activity, local time"),
    "roster_grid_csv": Layout("roster_grid_csv", "csv", roster_grid.render, "one row per agent, one column per local day"),
    "segments_json": Layout("segments_json", "json", segments_json.render, "segments with breaks, UTC and local ISO times"),
    "agent_ics": Layout("agent_ics", "ics", agent_ics.render, "one iCalendar file per agent, events in UTC",
                        per_agent=True),
}


def layout(name: str) -> Layout:
    try:
        return LAYOUTS[name]
    except KeyError:
        raise SystemExit(f"unknown export layout {name!r}; known: {', '.join(sorted(LAYOUTS))}") from None


def export_path(out_dir: Path, client: str, week: str, name: str) -> Path:
    """The export file, or for a per-agent layout the folder holding one file per agent."""
    lay = layout(name)
    stem = out_dir / client / "export" / f"{name}_{week}"
    return stem if lay.per_agent else stem.with_name(f"{stem.name}.{lay.extension}")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def control_totals(segments, path: Path, name: str, week: str, client: str) -> dict:
    """What the client's import is checked against: agents, segments, breaks, scheduled hours and
    the sha256 of the export file (per-agent layouts: of each file in the folder)."""
    totals = {"client": client, "week": week, "layout": name, "file": path.name,
              "agents": len({s.agent_id for s in segments}), "segments": len(segments),
              "breaks": sum(1 for s in segments if s.break_start is not None),
              "scheduled_hours": round(sum(s.hours for s in segments), 2)}
    if path.is_dir():
        totals["files"] = {p.name: _sha256(p) for p in sorted(path.iterdir())}
    else:
        totals["sha256"] = _sha256(path)
    return totals


def _write(path: Path, text: str) -> None:
    path.write_bytes(text.encode("utf-8"))    # bytes as rendered: no newline translation (iCalendar uses CRLF)


def export_schedule(sched_csv: Path, cfg: dict, week: str, name: str, out_dir: Path, agents=None) -> Path:
    """Write the week's schedule in layout `name` and its control totals next to it
    (<layout>_<week>.manifest.json); returns the export file or folder. With a roster, every
    scheduled agent must be on it."""
    lay = layout(name)
    segments = read_schedule(sched_csv)
    check_week(segments, week, cfg["tz"])
    if agents is not None:
        unknown = sorted({s.agent_id for s in segments} - {a.agent_id for a in agents})
        if unknown:
            raise SystemExit(f"schedule.csv has agents not on the {cfg['client']} roster: {', '.join(unknown)}")
    path = export_path(out_dir, cfg["client"], week, name)
    path.parent.mkdir(parents=True, exist_ok=True)
    if lay.per_agent:
        path.mkdir(exist_ok=True)
        for old in path.glob(f"*.{lay.extension}"):
            old.unlink()                      # an agent dropped since the last export of this week
        for fname, text in lay.render(segments, cfg, week, agents).items():
            _write(path / fname, text)
    else:
        _write(path, lay.render(segments, cfg, week, agents))
    manifest = path.with_name(f"{name}_{week}.manifest.json")
    manifest.write_text(json.dumps(control_totals(segments, path, name, week, cfg["client"]), indent=2) + "\n")
    return path
