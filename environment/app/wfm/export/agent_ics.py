"""Layout `agent_ics`: one iCalendar file (RFC 5545) per scheduled agent, for clients whose agents
take their shifts into a calendar rather than an ACD.

    out/<client>/export/agent_ics_<week>/<agent_id>.ics

One VEVENT per schedule segment, times in UTC (`...Z`), so calendar clients place them correctly
on both sides of a DST change. The break, if the segment holds one, is in the DESCRIPTION with its
local time. UIDs are built from client, week, agent and the segment's position in the agent's week,
and DTSTAMP is the start of the local week, so re-exporting the same schedule gives the same bytes
and calendar clients update events in place instead of duplicating them.
"""
from __future__ import annotations

from wfm import weeks
from wfm.export.base import Segment

PRODID = "-//WFM service//schedule export//EN"
UID_DOMAIN = "wfm-service.example"
FOLD = 75   # octets per line before folding (RFC 5545 3.1)


def escape(text: str) -> str:
    """TEXT value escaping: backslash, semicolon, comma and newline."""
    return text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def fold(line: str) -> list[str]:
    """Split a content line into pieces of at most 75 octets; continuation pieces start with a space."""
    out, cur, size = [], "", 0
    for ch in line:
        n = len(ch.encode("utf-8"))
        limit = FOLD if not out else FOLD - 1
        if size + n > limit:
            out.append(cur)
            cur, size = "", 0
        cur += ch
        size += n
    out.append(cur)
    return [out[0]] + [" " + piece for piece in out[1:]]


def stamp(t) -> str:
    return t.strftime("%Y%m%dT%H%M%SZ")


def _description(seg: Segment, index: int, count: int, tz: str) -> str:
    a, b = weeks.to_local(seg.start, tz), weeks.to_local(seg.end, tz)
    parts = [f"{seg.queue}, template {seg.template_id}, {weeks.hhmm(a)}-{weeks.hhmm(b, a.date())} local ({tz})."]
    if count > 1:
        parts.append(f"Segment {index + 1} of {count} of the shift.")
    if seg.break_start is not None:
        bs, be = weeks.to_local(seg.break_start, tz), weeks.to_local(seg.break_end, tz)
        parts.append(f"Break {weeks.hhmm(bs)}-{weeks.hhmm(be)} local ({seg.break_minutes} min).")
    return " ".join(parts)


def calendar(agent_id: str, segs: list[Segment], cfg: dict, week: str) -> str:
    tz, client = cfg["tz"], cfg["client"]
    name = cfg.get("name", client)
    dtstamp = stamp(weeks.bounds_utc(week, tz)[0])
    ordered = sorted(segs, key=lambda s: (s.start, s.segment_idx))
    per_shift = {}
    for s in ordered:   # segments of one template placement on one local day form a shift
        per_shift.setdefault((s.template_id, weeks.to_local(s.start, tz).date()), []).append(s)
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", f"PRODID:{PRODID}", "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
             f"X-WR-CALNAME:{escape(f'{name} {week} {agent_id}')}", f"X-WR-TIMEZONE:{tz}"]
    for i, s in enumerate(ordered):
        shift = per_shift[(s.template_id, weeks.to_local(s.start, tz).date())]
        lines += ["BEGIN:VEVENT", f"UID:{client}-{week}-{agent_id}-{i}@{UID_DOMAIN}", f"DTSTAMP:{dtstamp}",
                  f"DTSTART:{stamp(s.start)}", f"DTEND:{stamp(s.end)}",
                  f"SUMMARY:{escape(f'{name}: {s.queue} shift')}",
                  f"DESCRIPTION:{escape(_description(s, shift.index(s), len(shift), tz))}",
                  "TRANSP:OPAQUE", "END:VEVENT"]
    lines.append("END:VCALENDAR")
    return "".join(piece + "\r\n" for line in lines for piece in fold(line))


def render(segments: list[Segment], cfg: dict, week: str, agents=None) -> dict[str, str]:
    """{file name: calendar text} for every agent with at least one segment in the week."""
    by_agent: dict[str, list[Segment]] = {}
    for s in segments:
        by_agent.setdefault(s.agent_id, []).append(s)
    return {f"{aid}.ics": calendar(aid, segs, cfg, week) for aid, segs in sorted(by_agent.items())}
