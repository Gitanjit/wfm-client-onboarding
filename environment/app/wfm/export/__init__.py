"""Schedule exporters: a run's out/<client>/schedule.csv in the layouts clients load into their ACDs.

Off the `wfm run` path (docs/adr/0006-schedule-export-layouts.md): an exporter reads schedule.csv
only, never re-runs staffing or scheduling, and writes out/<client>/export/<layout>_<week>.<ext>.
Each client's layout is recorded in clients/registry.yaml (`export_layout`).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from wfm.export import activity_csv, roster_grid, segments_json
from wfm.export.base import check_week, read_schedule


@dataclass(frozen=True)
class Layout:
    name: str
    extension: str
    render: Callable      # (segments, cfg, week, agents) -> text
    summary: str


LAYOUTS: dict[str, Layout] = {
    "activity_csv": Layout("activity_csv", "csv", activity_csv.render, "one row per work/break activity, local time"),
    "roster_grid_csv": Layout("roster_grid_csv", "csv", roster_grid.render, "one row per agent, one column per local day"),
    "segments_json": Layout("segments_json", "json", segments_json.render, "segments with breaks, UTC and local ISO times"),
}


def layout(name: str) -> Layout:
    try:
        return LAYOUTS[name]
    except KeyError:
        raise SystemExit(f"unknown export layout {name!r}; known: {', '.join(sorted(LAYOUTS))}") from None


def export_path(out_dir: Path, client: str, week: str, name: str) -> Path:
    return out_dir / client / "export" / f"{name}_{week}.{layout(name).extension}"


def control_totals(segments, path: Path, name: str, week: str, client: str) -> dict:
    """What the client's ACD import is checked against: agents, segments, breaks, scheduled hours
    and the export file's sha256."""
    return {"client": client, "week": week, "layout": name, "file": path.name,
            "agents": len({s.agent_id for s in segments}), "segments": len(segments),
            "breaks": sum(1 for s in segments if s.break_start is not None),
            "scheduled_hours": round(sum(s.hours for s in segments), 2),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def export_schedule(sched_csv: Path, cfg: dict, week: str, name: str, out_dir: Path, agents=None) -> Path:
    """Write the week's schedule in layout `name` and its control totals next to it
    (<layout>_<week>.manifest.json); returns the export file. With a roster, every scheduled agent
    must be on it."""
    lay = layout(name)
    segments = read_schedule(sched_csv)
    check_week(segments, week, cfg["tz"])
    if agents is not None:
        unknown = sorted({s.agent_id for s in segments} - {a.agent_id for a in agents})
        if unknown:
            raise SystemExit(f"schedule.csv has agents not on the {cfg['client']} roster: {', '.join(unknown)}")
    path = export_path(out_dir, cfg["client"], week, name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(lay.render(segments, cfg, week, agents))
    manifest = path.with_name(f"{name}_{week}.manifest.json")
    manifest.write_text(json.dumps(control_totals(segments, path, name, week, cfg["client"]), indent=2) + "\n")
    return path
