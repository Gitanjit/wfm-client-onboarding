"""Per-agent shift notices: each agent's week in local wall-clock time, one text file per agent.

Every agent on the roster gets a notice, including those with no shift that week. Times are local
to the client; a shift ending at local midnight is written 24:00.
"""
from __future__ import annotations

from wfm import weeks
from wfm.export.base import Segment, Shift, shifts
from wfm.notify import templates
from wfm.report import markdown as md


def _shift_text(sh: Shift, tz: str) -> tuple[str, str, str]:
    times = ", ".join(f"{weeks.hhmm(weeks.to_local(s.start, tz))}-{weeks.hhmm(weeks.to_local(s.end, tz), sh.day)}"
                      for s in sh.segments)
    brk = ", ".join(f"{weeks.hhmm(weeks.to_local(s.break_start, tz))} ({s.break_minutes} min)" for s in sh.breaks)
    return times, sh.queue, brk


def notice(agent_id: str, contract: str, mine: list[Shift], cfg: dict, week: str) -> str:
    tz = cfg["tz"]
    if mine:
        rows = []
        for i, d in enumerate(weeks.days(week)):
            day = [sh for sh in mine if sh.day == d]
            label = f"{weeks.DAY_NAMES[i]} {d:%d %b}"
            if not day:
                rows.append([label, templates.DAY_OFF, "", ""])
            for sh in day:
                rows.append([label, *_shift_text(sh, tz)])
        body = md.text_table(["day", "shift", "queue", "break"], rows, align="llll")
    else:
        body = "  " + templates.NO_SHIFTS
    cap = cfg["weekly_hours"].get(contract)
    return templates.AGENT.substitute(
        agent_id=agent_id, contract=contract or "?", name=cfg.get("name", cfg["client"]),
        week_label=weeks.label(week), tz=tz, shifts=body,
        hours=md.num(sum(sh.hours for sh in mine)), cap=md.DASH if cap is None else md.num(float(cap)))


def notices(segments: list[Segment], cfg: dict, week: str, agents) -> dict[str, str]:
    """{agent_id: text} for every roster agent and any scheduled agent missing from the roster."""
    by_agent: dict[str, list[Shift]] = {}
    for sh in shifts(segments, cfg["tz"]):
        by_agent.setdefault(sh.agent_id, []).append(sh)
    contract = {a.agent_id: a.contract for a in agents or []}
    return {aid: notice(aid, contract.get(aid, ""), by_agent.get(aid, []), cfg, week)
            for aid in sorted(set(contract) | set(by_agent))}
