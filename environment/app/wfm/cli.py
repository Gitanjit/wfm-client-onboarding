"""python -m wfm run --client <name> --week <YYYY-Www>"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from wfm import board, registry, weeks
from wfm.config import OUT_DIR, load_config
from wfm.evaluate.metrics import evaluate
from wfm.export import LAYOUTS, export_schedule
from wfm.export.base import check_week, read_schedule
from wfm.ingest.loader import load_week
from wfm.notify import notify_dir, write_notifications
from wfm.report import compare, history, summary, volume
from wfm.report import markdown as md
from wfm.roster import load_agents
from wfm.scheduler import rules
from wfm.scheduler.greedy import schedule_week, to_frame
from wfm.scheduler.templates import templates_for
from wfm.staffing.required import add_required


def run(client: str, week: str) -> dict:
    cfg = load_config(client)
    demand = load_week(cfg, week)
    req = add_required(demand, cfg)
    agents = load_agents(client)
    shifts = schedule_week(req, cfg, agents, week)
    sched = to_frame(shifts)

    out = OUT_DIR / client
    out.mkdir(parents=True, exist_ok=True)
    sched.to_csv(out / "schedule.csv", index=False)
    exceptions = rules.infeasible(req, cfg, templates_for(cfg)) if cfg.get("queue_earliest_hour") else []
    result = evaluate(req, sched, cfg, agents, week, exclude=set(exceptions))
    result["exceptions"] = [{"queue": q, "interval_start_utc": t.strftime("%Y-%m-%dT%H:%M:%SZ")} for q, t in exceptions]
    (out / "eval.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


# The subcommands below are off the run path: they read the registry, the data files, or what `run`
# wrote to out/. Each returns an exit code.

def _week(s: str) -> str:
    try:
        weeks.parse(s)
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e)) from None
    return s


def _date(s: str) -> date:
    try:
        return date.fromisoformat(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"not a date: {s!r} (expected YYYY-MM-DD)") from None


def _out(args) -> Path:
    return Path(args.out) if getattr(args, "out", None) else OUT_DIR


def _in_range(week: str, first: str | None, last: str | None) -> bool:
    return not ((first and weeks.key(week) < weeks.key(first)) or (last and weeks.key(week) > weeks.key(last)))


def _write_report(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    print(text, end="")
    print(f"wrote {path}", file=sys.stderr)


def _run_outputs(client: str, week: str, out: Path):
    """Config, eval.json and schedule segments of the last run, checked to be this client-week's."""
    cfg = load_config(client)
    ev = history.read_eval(out / client / "eval.json")
    history.check_eval(ev, client, week, out / client / "eval.json")
    segments = read_schedule(out / client / "schedule.csv")
    check_week(segments, week, cfg["tz"])
    return cfg, ev, segments


def clients_cmd(args) -> int:
    reg = registry.load_registry()
    recs = list(reg.values()) if args.status is None else registry.by_status(reg, args.status)
    if args.active_on:
        recs = [r for r in registry.active_on(reg, args.active_on) if r in recs]
    if args.board:
        out = _out(args)
        if args.week:
            _write_report(out / "reports" / f"board_{args.week}.md",
                          board.render(board.board(recs, args.week, out), args.week))
        elif args.first and args.last:
            _write_report(out / "reports" / f"board_{args.first}_{args.last}.md",
                          board.grid(recs, args.first, args.last, out))
        else:
            raise SystemExit("--board needs --week, or --from and --to")
        return 0
    if args.timeline:
        print(registry.timeline(recs, args.until or date.today()))
        return 0
    if args.check:
        problems = [p for r in recs for p in registry.check(r, layouts=LAYOUTS, data=args.data)]
        for p in problems:
            print(p)
        n = {lvl: sum(p.level == lvl for p in problems) for lvl in (registry.ERROR, registry.WARNING, registry.PENDING)}
        print(f"{len(recs)} client(s) checked: {n['error']} error(s), {n['warning']} warning(s), {n['pending']} pending")
        return 1 if n["error"] else 0
    if args.markdown:
        print(registry.render_markdown(recs))
        return 0
    today = date.today()
    rows = [[r.key, r.status, *registry.period(r), len(r.weeks_served(today)) or md.DASH, f"{r.grain} min", r.tz,
             r.export_layout or md.DASH] for r in recs]
    print(md.text_table(["client", "status", "from", "to", "weeks", "grain", "tz", "export"], rows,
                        align="llllrrll", indent=0))
    return 0


def volume_cmd(args) -> int:
    cfg = load_config(args.client)
    rows = volume.volume_report(cfg, args.first, args.last, min_run=args.min_run)
    print(volume.render(cfg, rows, days=args.days, shape=args.profile), end="")
    if args.csv and rows:
        path = _out(args) / args.client / "reports" / f"volume_{args.first or rows[0].week}_{args.last or rows[-1].week}.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(volume.to_csv(rows))
        print(f"wrote {path}", file=sys.stderr)
    return 0


def archive_cmd(args) -> int:
    a = history.archive(args.client, args.week, _out(args))
    print(f"archived {args.client} {args.week} -> {a.path}" + (" (replaced)" if a.replaced else ""))
    return 0


def backfill_cmd(args) -> int:
    """Run and archive every week with a canonical file in the range (always under out/, where
    `run` writes)."""
    wanted = [w for w in volume.week_files(args.client) if _in_range(w, args.first, args.last)]
    if not wanted:
        raise SystemExit(f"no canonical week files for {args.client} in the range")
    for w in wanted:
        res = run(args.client, w)
        history.archive(args.client, w, OUT_DIR)
        print(f"{w}  sla {json.dumps(res['sla'])}  meets_target {res['meets_target']}  hours {res['scheduled_hours']}")
    return 0


def summary_cmd(args) -> int:
    out = _out(args)
    cfg = load_config(args.client)
    s = summary.summarise(history.load(args.client, out, args.first, args.last), cfg.get("sla_target"),
                          args.first, args.last)
    path = out / args.client / "reports" / f"summary_{args.first or s.first}_{args.last or s.last}.md"
    if args.csv:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.with_suffix(".csv").write_text(summary.to_csv(s))
    _write_report(path, summary.render(s, cfg.get("name")))
    return 0


def compare_cmd(args) -> int:
    out = _out(args)
    cfg = load_config(args.client)
    if args.against:
        a, b = compare.archived_side(args.client, args.against, out), compare.archived_side(args.client, args.week, out)
    else:
        a, b = compare.archived_side(args.client, args.week, out), compare.current_side(args.client, args.week, out)
    c = compare.compare(args.client, a, b, cfg["tz"])
    name = f"compare_{args.week}.md" if a.week == b.week else f"compare_{a.week}_{b.week}.md"
    _write_report(out / args.client / "reports" / name, compare.render(c))
    return 1 if args.fail_on_change and c.changed else 0


def accounts_cmd(args) -> int:
    """Latest archived week of each client in the registry (live and paused by default)."""
    out = _out(args)
    statuses = [args.status] if args.status else ["live", "paused"]
    recs = [r for r in registry.load_registry().values() if r.status in statuses]
    _write_report(out / "reports" / "accounts.md", registry.accounts_table(recs, out))
    return 0


def export_cmd(args) -> int:
    out = _out(args)
    name = args.layout or registry.get(args.client).export_layout
    if name is None:
        raise SystemExit(f"no export_layout for {args.client!r} in clients/registry.yaml: pass --layout")
    cfg, _ev, _segments = _run_outputs(args.client, args.week, out)
    agents = load_agents(args.client)
    for n in sorted(LAYOUTS) if name == "all" else [name]:
        print(export_schedule(out / args.client / "schedule.csv", cfg, args.week, n, out, agents))
    return 0


def notify_cmd(args) -> int:
    out = _out(args)
    cfg, ev, segments = _run_outputs(args.client, args.week, out)
    rec = registry.load_registry().get(args.client)
    earlier = [w for w in history.archived_weeks(args.client, out) if weeks.key(w) < weeks.key(args.week)]
    previous = history.read_eval(history.history_dir(args.client, out) / earlier[-1] / "eval.json") if earlier else None
    written = write_notifications(out, cfg, args.week, ev, segments, load_agents(args.client),
                                  rec.account_manager if rec else None, previous)
    print(f"{len(written)} file(s) under {notify_dir(out, args.client, args.week)}")
    return 0


REPORTS = {"volume": volume_cmd, "archive": archive_cmd, "backfill": backfill_cmd, "summary": summary_cmd,
           "compare": compare_cmd, "accounts": accounts_cmd}


def report_cmd(args) -> int:
    return REPORTS[args.report](args)


def _add_subcommands(sub) -> None:
    out_help = "output root (default out/)"
    c = sub.add_parser("clients", help="list clients from clients/registry.yaml")
    c.add_argument("--status", choices=registry.STATUSES)
    c.add_argument("--active-on", type=_date, metavar="YYYY-MM-DD", help="only clients served on that date")
    c.add_argument("--markdown", action="store_true", help="print the client table as markdown")
    c.add_argument("--check", action="store_true", help="compare the registry with configs, rosters and data")
    c.add_argument("--data", action="store_true", help="with --check: also run the file checks on every week file")
    c.add_argument("--board", action="store_true", help="weekly ops board for --week (data, run, archive, export, digest)")
    c.add_argument("--week", type=_week, help="the week for --board")
    c.add_argument("--from", dest="first", type=_week, help="with --to: --board over a range of weeks")
    c.add_argument("--to", dest="last", type=_week)
    c.add_argument("--timeline", action="store_true", help="month-by-month lifecycle of each client")
    c.add_argument("--until", type=_date, metavar="YYYY-MM-DD", help="last day shown by --timeline (default today)")
    c.add_argument("--out", help="output root for --board (default out/)")

    rep = sub.add_parser("report", help="weekly volume, evaluation archive, summaries and comparisons")
    rs = rep.add_subparsers(dest="report", required=True)
    v = rs.add_parser("volume", help="weekly volume and file checks from data/<client>/week_*.csv")
    a = rs.add_parser("archive", help="copy out/<client>/eval.json and schedule.csv into out/<client>/history/<week>/")
    b = rs.add_parser("backfill", help="run and archive every week with a canonical file in the range (out/)")
    s = rs.add_parser("summary", help="multi-week summary of the archived weeks")
    cm = rs.add_parser("compare", help="archived run of --week against the current run, or archived --against")
    acc = rs.add_parser("accounts", help="latest archived week of each client, by account manager")
    for p in (v, a, b, s, cm):
        p.add_argument("--client", required=True)
    for p in (v, b, s):
        p.add_argument("--from", dest="first", type=_week)
        p.add_argument("--to", dest="last", type=_week)
    for p in (a, cm):
        p.add_argument("--week", required=True, type=_week)
    for p in (v, a, s, cm, acc):
        p.add_argument("--out", help=out_help)
    v.add_argument("--min-run", type=int, default=2, help="zero-volume intervals in a row to report (default 2)")
    v.add_argument("--days", action="store_true", help="add contacts per local day")
    v.add_argument("--profile", action="store_true", help="add the weekday and intraday profile over the range")
    v.add_argument("--csv", action="store_true", help="also write the per-week rows to out/<client>/reports/")
    s.add_argument("--csv", action="store_true", help="also write the per-week rows as CSV")
    cm.add_argument("--against", type=_week, help="an archived week to compare with instead of the current run")
    cm.add_argument("--fail-on-change", action="store_true", help="exit 1 if the schedule or the eval differs")
    acc.add_argument("--status", choices=registry.STATUSES, help="default: live and paused")

    e = sub.add_parser("export", help="write the last run's schedule in an ACD layout")
    e.add_argument("--client", required=True)
    e.add_argument("--week", required=True, type=_week)
    e.add_argument("--layout", choices=[*sorted(LAYOUTS), "all"],
                   help="; ".join(f"{n}: {lay.summary}" for n, lay in sorted(LAYOUTS.items()))
                   + "; all: every layout. Default: the client's export_layout in the registry")
    e.add_argument("--out", help=out_help)

    n = sub.add_parser("notify", help="write the weekly digest, agent notices and day sheets under out/<client>/notify/")
    n.add_argument("--client", required=True)
    n.add_argument("--week", required=True, type=_week)
    n.add_argument("--out", help=out_help)


COMMANDS = {"clients": clients_cmd, "report": report_cmd, "export": export_cmd, "notify": notify_cmd}


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="wfm", description="Workforce-management service CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="ingest -> staffing -> schedule -> evaluate for one client-week")
    r.add_argument("--client", required=True)
    r.add_argument("--week", required=True, help="ISO week, e.g. 2026-W44")
    _add_subcommands(sub)
    args = ap.parse_args(argv)
    if args.cmd == "run":
        res = run(args.client, args.week)
        print(json.dumps({k: res[k] for k in ("client", "week", "intervals", "sla", "meets_target",
                                               "scheduled_hours", "agents_scheduled", "violations")}))
    else:
        rc = COMMANDS[args.cmd](args)
        if rc:
            raise SystemExit(rc)


if __name__ == "__main__":
    main()
