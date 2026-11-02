"""Layout `roster_grid_csv`: one row per agent, one column per local day of the week.

    agent_id,contract,Mon 2026-10-19,...,Sun 2026-10-25,hours
    PW-003,PT,07:00-13:00,OFF,08:00-12:00 / 16:00-20:00,...,22.0

A day cell holds the shift's local wall-clock segments ('HH:MM-HH:MM', a split shift's segments
joined with ' / ', a shift ending at local midnight written '24:00'), or OFF. Breaks are not shown:
the client's ACD places them from the activity layout or its own rules. `hours` is elapsed
scheduled time, as in eval.json. With a roster, agents without a shift that week are listed with
OFF every day, so the grid covers the whole team.
"""
from __future__ import annotations

from wfm import weeks
from wfm.export.base import Segment, shifts, to_csv

OFF = "OFF"


def _cell(day_shifts, tz: str) -> str:
    parts = []
    for sh in day_shifts:
        for seg in sh.segments:
            a, b = weeks.to_local(seg.start, tz), weeks.to_local(seg.end, tz)
            parts.append(f"{weeks.hhmm(a)}-{weeks.hhmm(b, sh.day)}")
    return " / ".join(parts) if parts else OFF


def render(segments: list[Segment], cfg: dict, week: str, agents=None) -> str:
    tz = cfg["tz"]
    days = weeks.days(week)
    contract = {a.agent_id: a.contract for a in agents or []}
    by_agent: dict[str, list] = {}
    for sh in shifts(segments, tz):
        by_agent.setdefault(sh.agent_id, []).append(sh)
    ids = sorted(set(by_agent) | set(contract))
    header = ["agent_id", "contract", *[f"{weeks.DAY_NAMES[i]} {d:%Y-%m-%d}" for i, d in enumerate(days)], "hours"]
    rows = []
    for aid in ids:
        mine = by_agent.get(aid, [])
        cells = [_cell([sh for sh in mine if sh.day == d], tz) for d in days]
        rows.append([aid, contract.get(aid, ""), *cells, f"{sum(sh.hours for sh in mine):.1f}"])
    return to_csv(header, rows)
