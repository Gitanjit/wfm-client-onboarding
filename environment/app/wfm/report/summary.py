"""Multi-week summary over archived evaluations (out/<client>/history/<week>/eval.json).

Fields are read as `wfm run` writes them (see docs/ARCHITECTURE.md, eval.json). Queues and rule
names are taken from the evals themselves, so a client with other queues or rules needs no change
here.
"""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from statistics import mean

from wfm import weeks
from wfm.report import markdown as md


@dataclass(frozen=True)
class QueueStats:
    queue: str
    weeks: int
    mean: float
    min: float
    min_week: str
    max: float
    max_week: str
    below_target: int | None     # weeks under sla_target; None when no target was given


@dataclass(frozen=True)
class Range:
    mean: float
    min: float
    max: float


@dataclass
class Summary:
    client: str
    weeks: list[str]
    missing: list[str]
    sla_target: float | None
    queues: list[QueueStats]
    weeks_meeting: int
    hours: Range
    agents: Range
    understaffed: float
    overstaffed: float
    violations: dict[str, int]
    violation_weeks: dict[str, int]
    rows: list[dict] = field(default_factory=list)

    @property
    def first(self) -> str:
        return self.weeks[0]

    @property
    def last(self) -> str:
        return self.weeks[-1]


def _range(values: list[float]) -> Range:
    return Range(mean(values), min(values), max(values))


def _queue_stats(evals: list[dict], q: str, sla_target: float | None) -> QueueStats:
    pts = [(ev["week"], float(ev["sla"][q])) for ev in evals if q in ev.get("sla", {})]
    lo = min(pts, key=lambda p: p[1])          # first week wins a tie: weeks are in order
    hi = max(pts, key=lambda p: p[1])
    below = None if sla_target is None else sum(1 for _, v in pts if v < sla_target)
    return QueueStats(q, len(pts), mean(v for _, v in pts), lo[1], lo[0], hi[1], hi[0], below)


def _row(ev: dict) -> dict:
    viol = ev.get("violations", {})
    return {"week": ev["week"], "intervals": ev.get("intervals"), "sla": dict(ev.get("sla", {})),
            "meets_target": ev.get("meets_target"), "hours": float(ev.get("scheduled_hours", 0.0)),
            "agents": int(ev.get("agents_scheduled", 0)),
            "under": float(ev.get("understaffed_interval_hours", 0.0)),
            "over": float(ev.get("overstaffed_interval_hours", 0.0)),
            "violations": int(sum(int(v) for v in viol.values()))}


def summarise(evals: list[dict], sla_target: float | None = None,
              first: str | None = None, last: str | None = None) -> Summary:
    """Summary of `evals` (in week order). `first`/`last` set the range used to list missing weeks;
    they default to the first and last evaluated week."""
    if not evals:
        raise SystemExit("no archived weeks to summarise: archive weeks with `wfm report archive`")
    wk = [ev["week"] for ev in evals]
    if wk != sorted(wk, key=weeks.key):
        raise ValueError("evals must be in week order")
    span = weeks.week_range(first or wk[0], last or wk[-1])
    queues = sorted({q for ev in evals for q in ev.get("sla", {})})
    rules = sorted({r for ev in evals for r in ev.get("violations", {})})
    rows = [_row(ev) for ev in evals]
    return Summary(
        client=evals[0]["client"], weeks=wk, missing=[w for w in span if w not in set(wk)],
        sla_target=sla_target, queues=[_queue_stats(evals, q, sla_target) for q in queues],
        weeks_meeting=sum(1 for ev in evals if ev.get("meets_target")),
        hours=_range([r["hours"] for r in rows]), agents=_range([r["agents"] for r in rows]),
        understaffed=sum(r["under"] for r in rows), overstaffed=sum(r["over"] for r in rows),
        violations={r: sum(int(ev.get("violations", {}).get(r, 0)) for ev in evals) for r in rules},
        violation_weeks={r: sum(1 for ev in evals if int(ev.get("violations", {}).get(r, 0)) > 0) for r in rules},
        rows=rows)


def render(s: Summary, name: str | None = None) -> str:
    title = f"Weekly summary - {name or s.client}, {s.first}" + ("" if s.first == s.last else f" to {s.last}")
    n = len(s.weeks)
    intro = [f"{n} week(s) archived for `{s.client}`; {s.weeks_meeting} of {n} met the evaluator target"
             + (f" ({md.ratio(s.sla_target, 2)} per queue)." if s.sla_target is not None else ".")]
    if s.missing:
        intro.append(f"Not archived in the range: {', '.join(s.missing)}.")

    att = md.table(["queue", "weeks", "mean", "min", "week of min", "max", "week of max", "weeks below target"],
                   [[q.queue, q.weeks, md.ratio(q.mean), md.ratio(q.min), q.min_week, md.ratio(q.max), q.max_week,
                     q.below_target] for q in s.queues])
    staffing = md.table(["measure", "mean", "min", "max"],
                        [["scheduled hours", md.num(s.hours.mean), md.num(s.hours.min), md.num(s.hours.max)],
                         ["agents scheduled", md.num(s.agents.mean), md.num(s.agents.min, 0), md.num(s.agents.max, 0)]])
    totals = md.table(["interval-hours over the range", "total"],
                      [["understaffed", md.num(s.understaffed)], ["overstaffed", md.num(s.overstaffed)]])
    rules = (md.table(["rule", "total", "weeks with any"],
                      [[r, s.violations[r], s.violation_weeks[r]] for r in s.violations])
             if s.violations else "No rule checks in the archived evals.")

    queues = [q.queue for q in s.queues]
    per_week = md.table(["week", "intervals", *queues, "meets target", "hours", "agents", "under h", "over h", "violations"],
                        [[r["week"], r["intervals"], *[md.ratio(r["sla"].get(q)) for q in queues],
                          md.yes_no(r["meets_target"]), md.num(r["hours"]), r["agents"], md.num(r["under"]),
                          md.num(r["over"]), r["violations"]] for r in s.rows])
    return md.document(md.heading(title, 1), " ".join(intro),
                       md.heading("Attainment"), att,
                       md.heading("Hours and staffing"), staffing, totals,
                       md.heading("Rule checks"), rules,
                       md.heading("Per week"), per_week)


def to_csv(s: Summary) -> str:
    """Per-week rows for a spreadsheet: one attainment column per queue, then the weekly figures."""
    queues = [q.queue for q in s.queues]
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["week", "intervals", *[f"sla_{q}" for q in queues], "meets_target", "scheduled_hours",
                "agents_scheduled", "understaffed_interval_hours", "overstaffed_interval_hours", "violations"])
    for r in s.rows:
        w.writerow([r["week"], r["intervals"], *[r["sla"].get(q, "") for q in queues], r["meets_target"],
                    r["hours"], r["agents"], r["under"], r["over"], r["violations"]])
    return buf.getvalue()

