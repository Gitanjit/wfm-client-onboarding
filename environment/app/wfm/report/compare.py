"""Compare two runs: what a change did to a client-week's schedule and evaluation.

Two uses:
  before/after   the archived run of a week (out/<client>/history/<week>/) against the current run in
                 out/<client>/ of the same week, e.g. after a config or code change;
  week on week   two archived weeks of the same client.

Evaluation fields are compared generically (per-queue attainment, hours, staffing, rule counts).
Schedules are compared per agent (shifts and hours), per local weekday (hours) and per template
(shifts); identical schedule files are reported as such.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from wfm import weeks
from wfm.export.base import Shift, read_schedule, shifts
from wfm.report import history
from wfm.report import markdown as md

# eval.json measure -> (label, kind); kind picks the formatting: ratio, hours, count or flag
MEASURES = (("scheduled_hours", "scheduled hours", "hours"), ("agents_scheduled", "agents scheduled", "count"),
            ("understaffed_interval_hours", "understaffed interval-hours", "hours"),
            ("overstaffed_interval_hours", "overstaffed interval-hours", "hours"), ("intervals", "intervals", "count"))


@dataclass(frozen=True)
class Side:
    label: str              # e.g. 'archived 2026-W43' or 'current run'
    week: str
    eval: dict
    schedule: Path


@dataclass(frozen=True)
class AgentDelta:
    agent_id: str
    hours_a: float
    hours_b: float
    shifts_a: int
    shifts_b: int
    days: tuple[str, ...]   # weekdays whose shifts differ


@dataclass
class Comparison:
    client: str
    a: Side
    b: Side
    same_schedule: bool
    evals: list[tuple[str, str, float | None, float | None]] = field(default_factory=list)   # label, kind, a, b
    agents: list[AgentDelta] = field(default_factory=list)
    weekday_hours: list[tuple[str, float, float]] = field(default_factory=list)
    headcount_change: list[tuple[int, list[int]]] = field(default_factory=list)   # local hour, change per weekday
    templates: list[tuple[str, int, int]] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        return not self.same_schedule or any(a != b for _, _, a, b in self.evals)


def archived_side(client: str, week: str, out_dir: Path) -> Side:
    d = history.history_dir(client, out_dir) / week
    ev = history.read_eval(d / "eval.json")
    history.check_eval(ev, client, week, d / "eval.json")
    return Side(f"archived {week}", week, ev, d / "schedule.csv")


def current_side(client: str, week: str, out_dir: Path) -> Side:
    d = out_dir / client
    ev = history.read_eval(d / "eval.json")
    history.check_eval(ev, client, week, d / "eval.json")
    return Side(f"current run {week}", week, ev, d / "schedule.csv")


def _eval_rows(a: dict, b: dict) -> list[tuple[str, str, float | None, float | None]]:
    rows = []
    for q in sorted(set(a.get("sla", {})) | set(b.get("sla", {}))):
        rows.append((f"attainment {q}", "ratio", a.get("sla", {}).get(q), b.get("sla", {}).get(q)))
    rows.append(("meets target", "flag", a.get("meets_target"), b.get("meets_target")))
    for key, name, kind in MEASURES:
        rows.append((name, kind, a.get(key), b.get(key)))
    for r in sorted(set(a.get("violations", {})) | set(b.get("violations", {}))):
        rows.append((f"violations {r}", "count", a.get("violations", {}).get(r, 0), b.get("violations", {}).get(r, 0)))
    return rows


def _shift_keys(mine: list[Shift], week: str, tz: str) -> dict[int, set]:
    """weekday index -> set of comparable shift descriptions (template, queue, local times)."""
    first = weeks.monday(week)
    out: dict[int, set] = {}
    for sh in mine:
        times = tuple((weeks.hhmm(weeks.to_local(s.start, tz)), weeks.hhmm(weeks.to_local(s.end, tz), sh.day))
                      for s in sh.segments)
        out.setdefault((sh.day - first).days, set()).add((sh.template_id, sh.queue, times))
    return out


def headcount(all_shifts: list[Shift], week: str, tz: str) -> Counter:
    """(weekday index, local hour) -> agents on shift at the start of that hour, all queues."""
    first = weeks.monday(week)
    out: Counter = Counter()
    for sh in all_shifts:
        i = (sh.day - first).days
        for h, t in weeks.hour_starts(sh.day, tz):
            out[(i, h)] += sum(1 for s in sh.segments if s.start <= t < s.end)
    return out


def compare(client: str, a: Side, b: Side, tz: str) -> Comparison:
    same = a.schedule.exists() and b.schedule.exists() and a.schedule.read_bytes() == b.schedule.read_bytes()
    c = Comparison(client, a, b, same, _eval_rows(a.eval, b.eval))
    sa, sb = shifts(read_schedule(a.schedule), tz), shifts(read_schedule(b.schedule), tz)
    by_a: dict[str, list[Shift]] = {}
    by_b: dict[str, list[Shift]] = {}
    for sh in sa:
        by_a.setdefault(sh.agent_id, []).append(sh)
    for sh in sb:
        by_b.setdefault(sh.agent_id, []).append(sh)
    for aid in sorted(set(by_a) | set(by_b)):
        ka, kb = _shift_keys(by_a.get(aid, []), a.week, tz), _shift_keys(by_b.get(aid, []), b.week, tz)
        days = tuple(weeks.DAY_NAMES[i] for i in range(7) if ka.get(i, set()) != kb.get(i, set()))
        if days:
            c.agents.append(AgentDelta(aid, sum(s.hours for s in by_a.get(aid, [])), sum(s.hours for s in by_b.get(aid, [])),
                                       len(by_a.get(aid, [])), len(by_b.get(aid, [])), days))
    mon_a, mon_b = weeks.monday(a.week), weeks.monday(b.week)
    for i, name in enumerate(weeks.DAY_NAMES):
        ha = sum(sh.hours for sh in sa if (sh.day - mon_a).days == i)
        hb = sum(sh.hours for sh in sb if (sh.day - mon_b).days == i)
        c.weekday_hours.append((name, ha, hb))
    ha, hb = headcount(sa, a.week, tz), headcount(sb, b.week, tz)
    for h in range(24):
        diff = [hb[(i, h)] - ha[(i, h)] for i in range(7)]
        if any(diff):
            c.headcount_change.append((h, diff))
    ta, tb = Counter(sh.template_id for sh in sa), Counter(sh.template_id for sh in sb)
    c.templates = [(t, ta.get(t, 0), tb.get(t, 0)) for t in sorted(set(ta) | set(tb))]
    return c


def _val(kind: str, v) -> str:
    if v is None:
        return md.DASH
    return {"ratio": md.ratio, "hours": md.num, "flag": md.yes_no}.get(kind, str)(v)


def _delta(kind: str, a, b) -> str:
    if a is None or b is None:
        return md.DASH
    if kind == "flag":
        return "same" if bool(a) == bool(b) else "changed"
    d = b - a
    if d == 0:
        return "0"
    return {"ratio": f"{d:+.3f}", "hours": f"{d:+,.1f}"}.get(kind, f"{d:+d}" if isinstance(d, int) else f"{d:+g}")


def render(c: Comparison) -> str:
    title = f"Compare - {c.client}: {c.a.label} -> {c.b.label}"
    verdict = ("Schedules are byte-identical." if c.same_schedule
               else f"Schedules differ: {len(c.agents)} agent(s) with changed shifts.")
    blocks = [md.heading(title, 1), verdict, md.heading("Evaluation"),
              md.table(["measure", c.a.label, c.b.label, "change"],
                       [[m, _val(k, a), _val(k, b), _delta(k, a, b)] for m, k, a, b in c.evals], align="lrrr")]
    if not c.same_schedule:
        blocks += [md.heading("Hours by weekday"),
                   md.table(["day", c.a.label, c.b.label, "change"],
                            [[d, md.num(a), md.num(b), _delta("hours", a, b)] for d, a, b in c.weekday_hours]),
                   md.heading("Change in agents on shift by local hour"),
                   md.table(["hour", *weeks.DAY_NAMES],
                            [[f"{h:02d}:00", *[f"{d:+d}" if d else "" for d in diff]] for h, diff in c.headcount_change],
                            align="l" + "r" * 7) if c.headcount_change else "No change in hourly headcount.",
                   md.heading("Shifts by template"),
                   md.table(["template", c.a.label, c.b.label, "change"],
                            [[t, a, b, f"{b - a:+d}"] for t, a, b in c.templates]),
                   md.heading("Agents with changed shifts"),
                   md.table(["agent", "hours before", "hours after", "shifts before", "shifts after", "days"],
                            [[d.agent_id, md.num(d.hours_a), md.num(d.hours_b), d.shifts_a, d.shifts_b,
                              " ".join(d.days)] for d in c.agents]) if c.agents else "None."]
    return md.document(*blocks)
