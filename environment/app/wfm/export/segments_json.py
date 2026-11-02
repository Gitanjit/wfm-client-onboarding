"""Layout `segments_json`: the week's schedule as one JSON document, agents in id order.

    {"client": "wingtip", "week": "2026-W16", "tz": "America/Phoenix", "generated_from": "wingtip/schedule.csv",
     "agents": [{"agent_id": "WT-001", "hours": 24.0,
                 "segments": [{"queue": "standard", "template_id": "P6a",
                               "start_utc": "...Z", "end_utc": "...Z",
                               "start_local": "2026-04-13T07:00:00-07:00", "end_local": "...",
                               "breaks": [{"start_utc": ..., "end_utc": ..., "start_local": ..., "end_local": ...,
                                           "minutes": 20}]}]}]}

Local times carry their own offset (ISO 8601), computed per segment from the timezone database.
Keys and lists are in a fixed order so that the same schedule always gives the same bytes.
"""
from __future__ import annotations

import json

from wfm.export.base import Segment, iso_local, iso_utc


def _segment(seg: Segment, tz: str) -> dict:
    breaks = []
    if seg.break_start is not None:
        breaks.append({"start_utc": iso_utc(seg.break_start), "end_utc": iso_utc(seg.break_end),
                       "start_local": iso_local(seg.break_start, tz), "end_local": iso_local(seg.break_end, tz),
                       "minutes": seg.break_minutes})
    return {"queue": seg.queue, "template_id": seg.template_id,
            "start_utc": iso_utc(seg.start), "end_utc": iso_utc(seg.end),
            "start_local": iso_local(seg.start, tz), "end_local": iso_local(seg.end, tz), "breaks": breaks}


def render(segments: list[Segment], cfg: dict, week: str, agents=None) -> str:
    tz = cfg["tz"]
    by_agent: dict[str, list[Segment]] = {}
    for seg in segments:
        by_agent.setdefault(seg.agent_id, []).append(seg)
    doc = {"client": cfg["client"], "week": week, "tz": tz, "generated_from": f"{cfg['client']}/schedule.csv",
           "agents": [{"agent_id": aid, "hours": round(sum(s.hours for s in segs), 2),
                       "segments": [_segment(s, tz) for s in sorted(segs, key=lambda s: (s.start, s.segment_idx))]}
                      for aid, segs in sorted(by_agent.items())]}
    return json.dumps(doc, indent=2) + "\n"
