"""Grader for wfm-client-onboarding. End state only; own evaluator; reward.json always written.

Design rules (RUN_REPORT §5):
  * never import from /app/wfm; never read /app/configs for targets (SOW targets live in indep_eval.SOW)
  * outputs are cleared before every CLI rerun, so a hand-written schedule cannot survive
  * credentials are scrubbed from the environment the agent's code runs in
  * every dimension is wrapped: a crash scores 0 for that dimension and never kills the grader
  * one docstring per check; numbers recorded under "checks" for legibility
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import indep_eval as ie  # noqa: E402

DIMS = ["functional_correctness", "constraint_satisfaction", "regression", "artifact_quality"]
EXPECTED_INTERVALS = {("northwind", "2026-W44"): 338, ("northwind", "2026-W45"): 336,
                      ("contoso", "2026-W44"): 672, ("fabrikam", "2026-W44"): 169}
TOL = {"sla": 0.02, "cost": 1.10, "reg_sla": 0.02, "reg_cost": 1.10, "report_rel": 0.005}
GATES = {"functional_correctness": 0.875, "constraint_satisfaction": 1.0, "regression": 1.0, "artifact_quality": 0.75}
SCRUB = ("OPENROUTER_API_KEY", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "CLAUDE_CODE_OAUTH_TOKEN", "OPENAI_API_KEY")
RUNBOOK_KEYS = ["intervals_in_week", "sla_attainment_priority", "sla_attainment_standard",
                "scheduled_hours_total", "understaffed_interval_hours", "agents_scheduled", "files_changed"]


# ----------------------------------------------------------------------------- plumbing
def run_cli(app: Path, client: str, week: str, timeout: int = 300) -> tuple[int, str]:
    """Run the agent's system with its output directory cleared first and credentials scrubbed.
    RUNBOOK.md is left in place: it is a deliverable graded against recomputation, not a CLI output."""
    out_dir = app / "out" / client
    if out_dir.exists():
        for f in out_dir.iterdir():
            if f.name != "RUNBOOK.md":
                shutil.rmtree(f) if f.is_dir() else f.unlink()
    env = {k: v for k, v in os.environ.items() if k not in SCRUB}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        p = subprocess.run([sys.executable, "-m", "wfm", "run", "--client", client, "--week", week],
                           cwd=app, capture_output=True, text=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return 124, "timeout"
    return p.returncode, (p.stdout + p.stderr)[-2000:]


def stage_heldout(tests: Path, app: Path) -> None:
    """Copy held-out weeks into the agent's data directories (grader side only)."""
    for src, dst in [
        ("heldout/northwind/export_2026-W45.csv", "data/northwind/export_2026-W45.csv"),
        ("heldout/contoso/week_2026-W44.csv", "data/contoso/week_2026-W44.csv"),
        ("heldout/fabrikam/week_2026-W44.csv", "data/fabrikam/week_2026-W44.csv"),
    ]:
        (app / dst).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(tests / src, app / dst)


def demand_file(app: Path, client: str, week: str) -> Path:
    f = app / "data" / client / f"week_{week}.csv"
    return f if f.exists() else app / "data" / client / f"export_{week}.csv"


class Runs:
    """Runs each client-week once and caches the grader's metrics for every dimension."""

    def __init__(self, app: Path, tests: Path, checks: dict):
        self.app, self.tests, self.checks, self.cache = app, tests, checks, {}

    def get(self, client: str, week: str) -> dict | None:
        key = (client, week)
        if key in self.cache:
            return self.cache[key]
        rc, out = run_cli(self.app, client, week)
        sched = self.app / "out" / client / "schedule.csv"
        self.checks[f"run_{client}_{week}"] = {"exit": rc, "schedule_present": sched.exists(),
                                              "tail": out.strip().splitlines()[-1][:300] if out.strip() else ""}
        m = None
        if rc == 0 and sched.exists():
            try:
                m = ie.evaluate(client, week, sched, demand_file(self.app, client, week),
                                self.app / "data/agents" / f"{client}.csv")
                ev = self.app / "out" / client / "eval.json"
                m["agent_eval_intervals"] = None
                if ev.exists():
                    try:
                        m["agent_eval_intervals"] = json.loads(ev.read_text()).get("intervals")
                    except Exception:
                        m["agent_eval_intervals"] = "unparseable"
            except Exception as e:
                self.checks[f"run_{client}_{week}"]["evaluate_error"] = f"{type(e).__name__}: {e}"
                m = None
        self.cache[key] = m
        return m


def on_grid(m: dict) -> bool:
    """Every segment lies on the grader's week grid (no row outside the week, none on a non-existent slot)."""
    return not any("off the week grid" in s for s in m["violations"].get("coverage_sane", []))


def changed_files(app: Path, tests: Path) -> set[str]:
    """Files under /app whose sha256 differs from the seed manifest, plus new files. Git is not trusted."""
    manifest = json.loads((tests / "fixtures/seed_manifest.json").read_text())
    changed = set()
    for f in app.rglob("*"):
        rel = f.relative_to(app).as_posix()
        if f.is_file() and not rel.startswith("out/") and "__pycache__" not in rel and not rel.startswith(".git/"):
            if manifest.get(rel) != hashlib.sha256(f.read_bytes()).hexdigest():
                changed.add(rel)
    # held-out files staged by the grader are not the agent's changes
    return changed - {"data/northwind/export_2026-W45.csv", "data/contoso/week_2026-W44.csv", "data/fabrikam/week_2026-W44.csv"}


# ----------------------------------------------------------------------------- dimensions
def functional_correctness(runs: Runs, checks: dict) -> float:
    """Northwind W44 (seen) and W45 (held-out), 4 checks each: intervals, SLA per queue vs oracle-0.02, cost <= oracle*1.10."""
    passed = total = 0
    for week in ("2026-W44", "2026-W45"):
        m = runs.get("northwind", week)
        oracle = json.loads((runs.tests / f"fixtures/oracle_northwind_{week[-3:]}.json").read_text())
        exp = EXPECTED_INTERVALS[("northwind", week)]
        tests = [
            (f"fc_{week}_intervals",
             m is not None and m["intervals"] == exp and on_grid(m) and m["agent_eval_intervals"] in (None, exp),
             None if m is None else {"grader": m["intervals"], "agent_eval": m["agent_eval_intervals"], "on_grid": on_grid(m)}),
            (f"fc_{week}_sla_priority",
             m is not None and m["sla"]["priority"] >= oracle["sla"]["priority"] - TOL["sla"],
             None if m is None else {"agent": round(m["sla"]["priority"], 4), "oracle": round(oracle["sla"]["priority"], 4)}),
            (f"fc_{week}_sla_standard",
             m is not None and m["sla"]["standard"] >= oracle["sla"]["standard"] - TOL["sla"],
             None if m is None else {"agent": round(m["sla"]["standard"], 4), "oracle": round(oracle["sla"]["standard"], 4)}),
            (f"fc_{week}_cost",
             m is not None and m["scheduled_hours"] <= oracle["scheduled_hours"] * TOL["cost"],
             None if m is None else {"agent": m["scheduled_hours"], "oracle": oracle["scheduled_hours"]}),
        ]
        for name, ok, val in tests:
            checks[name] = {"pass": bool(ok), "value": val}
            passed += bool(ok)
            total += 1
    return passed / total


def constraint_satisfaction(runs: Runs, checks: dict) -> float:
    """Northwind W44 and W45: each of the 8 SOW rules has zero violations on schedule.csv; mean over the two weeks."""
    scores = []
    for week in ("2026-W44", "2026-W45"):
        m = runs.get("northwind", week)
        rules = ie.SOW["northwind"]["rules"]
        if m is None:
            checks[f"cs_{week}"] = {"pass": False, "value": "no schedule"}
            scores.append(0.0)
            continue
        clean = 0
        detail = {}
        for r in rules:
            v = m["violations"].get(r, [])
            detail[r] = {"violations": len(v), "examples": v[:3]}
            clean += not v
        checks[f"cs_{week}"] = {"pass": clean == len(rules), "value": detail}
        scores.append(clean / len(rules))
    return sum(scores) / len(scores)


def regression(runs: Runs, checks: dict) -> float:
    """Contoso W44 and Fabrikam W44 (held-out): runs, intervals, SLA >= baseline-0.02, cost <= baseline*1.10, standard rules clean."""
    passed = total = 0
    for client in ("contoso", "fabrikam"):
        m = runs.get(client, "2026-W44")
        base = json.loads((runs.tests / f"fixtures/baseline_{client}_W44.json").read_text())
        exp = EXPECTED_INTERVALS[(client, "2026-W44")]
        rules = ie.SOW[client]["rules"]
        tests = [
            (f"reg_{client}_runs", m is not None, None),
            (f"reg_{client}_intervals",
             m is not None and m["intervals"] == exp and on_grid(m) and m["agent_eval_intervals"] in (None, exp),
             None if m is None else {"grader": m["intervals"], "agent_eval": m["agent_eval_intervals"], "on_grid": on_grid(m)}),
            (f"reg_{client}_sla", m is not None and all(m["sla"][q] >= base["sla"][q] - TOL["reg_sla"] for q in m["sla"]),
             None if m is None else {"agent": {q: round(v, 4) for q, v in m["sla"].items()},
                                     "baseline": {q: round(v, 4) for q, v in base["sla"].items()}}),
            (f"reg_{client}_cost", m is not None and m["scheduled_hours"] <= base["scheduled_hours"] * TOL["reg_cost"],
             None if m is None else {"agent": m["scheduled_hours"], "baseline": base["scheduled_hours"]}),
            (f"reg_{client}_rules", m is not None and not any(m["violations"].get(r) for r in rules),
             None if m is None else {r: len(m["violations"].get(r, [])) for r in rules}),
        ]
        for name, ok, val in tests:
            checks[name] = {"pass": bool(ok), "value": val}
            passed += bool(ok)
            total += 1
    return passed / total


def parse_runbook(text: str) -> dict[str, str]:
    """Key/value pairs from the first two-column markdown table whose first column holds SOW §3 keys."""
    kv = {}
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[0].strip("`* ") in RUNBOOK_KEYS:
            kv[cells[0].strip("`* ")] = cells[1].strip("` ")
    return kv


def _num(s: str) -> float | None:
    m = re.search(r"-?\d+(?:\.\d+)?", s.replace(",", ""))
    return float(m.group()) if m else None


def artifact_quality(runs: Runs, checks: dict, runbook: str | None) -> float:
    """RUNBOOK.md: table parses (1); six numbers within 0.5% (counts exact) of the grader's recomputation on the
    re-run W44 outputs (6); files_changed non-empty and a subset of files that actually differ from the seed (1)."""
    kv = parse_runbook(runbook) if runbook else {}
    checks["aq_table"] = {"pass": len(kv) >= 6, "value": sorted(kv)}
    passed = int(len(kv) >= 6)
    m = runs.get("northwind", "2026-W44")
    expected = None if m is None else {
        "intervals_in_week": (m["intervals"], True),
        "sla_attainment_priority": (m["sla"]["priority"], False),
        "sla_attainment_standard": (m["sla"]["standard"], False),
        "scheduled_hours_total": (m["scheduled_hours"], False),
        "understaffed_interval_hours": (m["understaffed_interval_hours"], False),
        "agents_scheduled": (m["agents_scheduled"], True),
    }
    for key in RUNBOOK_KEYS[:6]:
        got = _num(kv.get(key, "")) if key in kv else None
        ok = False
        if expected is not None and got is not None:
            exp, exact = expected[key]
            ok = (got == exp) if exact else abs(got - exp) <= TOL["report_rel"] * max(abs(exp), 1e-9) + 1e-9
        checks[f"aq_{key}"] = {"pass": bool(ok), "value": {"runbook": got, "grader": None if expected is None else expected[key][0]}}
        passed += bool(ok)
    changed = changed_files(runs.app, runs.tests)
    listed = {p.strip().strip("`").removeprefix("/app/").removeprefix("app/").removeprefix("./")
              for p in kv.get("files_changed", "").split(",") if p.strip()}
    ok = bool(listed) and listed <= changed
    checks["aq_files_changed"] = {"pass": ok, "value": {"listed": sorted(listed), "not_actually_changed": sorted(listed - changed),
                                                        "actually_changed": sorted(changed)}}
    passed += ok
    return passed / 8


# ----------------------------------------------------------------------------- main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", type=Path, required=True)
    ap.add_argument("--tests", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    scores = {d: 0.0 for d in DIMS}
    checks: dict = {}
    try:
        runbook_path = args.app / "out/northwind/RUNBOOK.md"
        runbook = runbook_path.read_text() if runbook_path.exists() else None   # read BEFORE outputs are cleared
        checks["runbook_present"] = runbook is not None
        checks["preflight_wfm_help"] = subprocess.run([sys.executable, "-m", "wfm", "--help"], cwd=args.app,
                                                      capture_output=True).returncode == 0
        stage_heldout(args.tests, args.app)
        runs = Runs(args.app, args.tests, checks)
        for d in DIMS:
            try:
                fn = globals()[d]
                scores[d] = float(fn(runs, checks, runbook) if d == "artifact_quality" else fn(runs, checks))
            except Exception as e:
                checks[f"{d}_error"] = f"{type(e).__name__}: {e}"
                traceback.print_exc()
    except Exception as e:
        checks["grader_error"] = f"{type(e).__name__}: {e}"
        traceback.print_exc()

    gates = all(scores[d] >= GATES[d] for d in DIMS)
    overall = 1.0 if gates else min(0.79, sum(scores.values()) / len(DIMS))
    reward = {"overall": round(overall, 4), **{d: round(v, 4) for d, v in scores.items()}, "checks": checks}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(reward, indent=2, sort_keys=True, default=str) + "\n")

    print("== summary ==")
    for d in DIMS:
        print(f"  {d:24s} {scores[d]:.4f}  (gate {GATES[d]})")
    print(f"  overall                  {overall:.4f}")
    failed = [k for k, v in checks.items() if isinstance(v, dict) and v.get("pass") is False]
    print(f"  failed checks: {failed or 'none'}")


if __name__ == "__main__":
    main()
