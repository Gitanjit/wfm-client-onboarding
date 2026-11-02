"""Layout `activity_csv`: one row per activity (work or break) in the client's local time.

    agent_id,date_local,activity,queue,start_local,end_local,utc_offset,minutes
    CO-007,2026-10-19,WORK,priority,2026-10-19 06:00,2026-10-19 09:50,+00:00,230

`utc_offset` is the offset in effect at the activity's start, taken per row from the timezone
database, so the rows on either side of a DST change carry different offsets. Rows are ordered by
agent and start time.
"""
from __future__ import annotations

from wfm import weeks
from wfm.export.base import Segment, activities, local_stamp, to_csv

HEADER = ["agent_id", "date_local", "activity", "queue", "start_local", "end_local", "utc_offset", "minutes"]


def render(segments: list[Segment], cfg: dict, week: str, agents=None) -> str:
    tz = cfg["tz"]
    acts = sorted((a for seg in segments for a in activities(seg)), key=lambda a: (a.agent_id, a.start))
    rows = []
    for a in acts:
        loc = weeks.to_local(a.start, tz)
        rows.append([a.agent_id, loc.strftime("%Y-%m-%d"), a.kind, a.queue, local_stamp(a.start, tz),
                     local_stamp(a.end, tz), weeks.offset(loc), a.minutes])
    return to_csv(HEADER, rows)
