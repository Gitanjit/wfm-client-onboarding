"""python -m wfm run --client <name> --week <YYYY-Www>"""
from __future__ import annotations

import argparse
import json

from wfm.config import OUT_DIR, load_config
from wfm.evaluate.metrics import evaluate
from wfm.ingest.loader import load_week
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


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="wfm", description="Workforce-management service CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="ingest -> staffing -> schedule -> evaluate for one client-week")
    r.add_argument("--client", required=True)
    r.add_argument("--week", required=True, help="ISO week, e.g. 2026-W44")
    args = ap.parse_args(argv)
    if args.cmd == "run":
        res = run(args.client, args.week)
        print(json.dumps({k: res[k] for k in ("client", "week", "intervals", "sla", "meets_target",
                                               "scheduled_hours", "agents_scheduled", "violations")}))


if __name__ == "__main__":
    main()
