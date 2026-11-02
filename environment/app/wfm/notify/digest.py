"""Weekly digest for the account team: a run's eval.json and schedule.csv as plain text.

One digest per client-week, written to out/<client>/notify/<week>/digest.txt. It restates the run;
it computes nothing the evaluator does not, apart from per-day shift counts from the schedule.
"""
from __future__ import annotations

from collections import Counter

from wfm import weeks
from wfm.export.base import Segment, shifts
from wfm.notify import templates
from wfm.report import markdown as md


def recipients(account_manager: str | None) -> str:
    people = [f"{account_manager} (account manager)"] if account_manager else []
    return "; ".join(people + [templates.WFM_TEAM])


def attainment_lines(ev: dict, target: float) -> str:
    rows = [[q, md.ratio(v), md.ratio(target, 2), "met" if v >= target else "below"]
            for q, v in sorted(ev.get("sla", {}).items())]
    return md.text_table(["queue", "attainment", "target", "status"], rows, align="lrrl")


def contract_mix(segments: list[Segment], agents) -> str:
    contract = {a.agent_id: a.contract for a in agents or []}
    counts = Counter(contract.get(aid, "unknown") for aid in sorted({s.agent_id for s in segments}))
    return ", ".join(f"{c} {n}" for c, n in sorted(counts.items())) or "none"


def day_lines(segments: list[Segment], cfg: dict, week: str) -> str:
    tz = cfg["tz"]
    all_shifts = shifts(segments, tz)
    rows = []
    for i, d in enumerate(weeks.days(week)):
        day = [sh for sh in all_shifts if sh.day == d]
        if day:
            first = min(weeks.to_local(sh.start, tz) for sh in day)
            last = max(weeks.to_local(sh.end, tz) for sh in day)
            span = f"{weeks.hhmm(first)}-{weeks.hhmm(last, d)}"
        else:
            span = md.DASH
        rows.append([f"{weeks.DAY_NAMES[i]} {d:%d %b}", len(day), md.num(sum(sh.hours for sh in day)), span])
    return md.text_table(["day", "shifts", "hours", "first-last"], rows, align="lrrl")


def rule_lines(ev: dict) -> str:
    bad = [(k, int(v)) for k, v in sorted(ev.get("violations", {}).items()) if int(v)]
    if not bad:
        return templates.RULES_CLEAN
    return md.text_table(["rule", "count"], bad, align="lr")


def previous_lines(prev: dict | None, ev: dict) -> str:
    """This week against an earlier archived week: attainment per queue, hours, agents, understaffing."""
    if prev is None:
        return templates.NO_PREVIOUS
    rows = []
    for q in sorted(set(prev.get("sla", {})) | set(ev.get("sla", {}))):
        a, b = prev.get("sla", {}).get(q), ev.get("sla", {}).get(q)
        rows.append([f"attainment {q}", md.ratio(a), md.ratio(b), md.DASH if a is None or b is None else f"{b - a:+.3f}"])
    for key, name, digits in (("scheduled_hours", "scheduled hours", 1), ("agents_scheduled", "agents", 0),
                              ("understaffed_interval_hours", "understaffed interval-hours", 1)):
        a, b = prev.get(key), ev.get(key)
        rows.append([name, md.num(a, digits), md.num(b, digits),
                     md.DASH if a is None or b is None else f"{b - a:+,.{digits}f}"])
    return (f"Against {prev['week']} (the last archived week before this one)\n"
            + md.text_table(["", prev["week"], ev["week"], "change"], rows, align="lrrr"))


def digest(ev: dict, segments: list[Segment], cfg: dict, week: str,
           account_manager: str | None = None, agents=None, previous: dict | None = None) -> str:
    return templates.DIGEST.substitute(
        recipients=recipients(account_manager), name=cfg.get("name", cfg["client"]), client=cfg["client"],
        week=week, week_label=weeks.label(week), tz=cfg["tz"], target=md.ratio(cfg["sla_target"], 2),
        attainment=attainment_lines(ev, cfg["sla_target"]),
        hours=md.num(ev.get("scheduled_hours")), agents=ev.get("agents_scheduled", 0),
        contracts=contract_mix(segments, agents),
        under=md.num(ev.get("understaffed_interval_hours")), over=md.num(ev.get("overstaffed_interval_hours")),
        previous=previous_lines(previous, ev), days=day_lines(segments, cfg, week), rules=rule_lines(ev))
