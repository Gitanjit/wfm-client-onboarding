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
NW_WEEKS = ("2026-W44", "2026-W45", "2027-W10")   # seen; held-out; held-out with the US spring-forward
EXPECTED_INTERVALS = {("northwind", "2026-W44"): 338, ("northwind", "2026-W45"): 336, ("northwind", "2027-W10"): 334,
                      ("contoso", "2026-W44"): 672, ("fabrikam", "2026-W44"): 169}
SOW_EFFICIENCY_K, SOW_ATTAINMENT_FLOOR = 1.57, 0.95   # Northwind SOW §1.6
QUEUES_NW = ("priority", "standard", "vip")
# reported_sla: eval.json attainment vs the recomputation (instruction, SOW §2.7 "measured as defined in §1");
# vip_ref: vip cannot reach the 0.95 floor with this roster; the §2.7 "achievable value" must be within this of the reference's;
# shortfall: exceptions.md achievable / shortfall vs the recomputation
TOL = {"reg_sla": 0.02, "reg_cost": 1.10, "report_rel": 0.005, "reported_sla": 0.02, "vip_ref": 0.05, "shortfall": 0.03}
GATES = {"functional_correctness": 17 / 18, "constraint_satisfaction": 1.0, "regression": 1.0, "artifact_quality": 10 / 11}
# SOW §2.8 declaration: the handover note names one of the service's deviations from the §1 method by an identifying token
DECLARATION_TOKENS = ("pr #47", "#47", "attainment_basis", "pr #31", "#31", "cross_skill_weight", "cross-skill",
                      "cross skill", "qlib", "patience", "abandonment")
SCRUB = ("OPENROUTER_API_KEY", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "CLAUDE_CODE_OAUTH_TOKEN", "OPENAI_API_KEY")
RUNBOOK_KEYS = ["intervals_in_week", "sla_attainment_priority", "sla_attainment_standard", "sla_attainment_vip",
                "scheduled_hours_total", "required_hours_total", "understaffed_interval_hours", "agents_scheduled",
                "files_changed"]
HELDOUT = {"heldout/northwind/export_2026-W45.csv": "data/northwind/export_2026-W45.csv",
           "heldout/northwind/export_2027-W10.csv": "data/northwind/export_2027-W10.csv",
           "heldout/contoso/week_2026-W44.csv": "data/contoso/week_2026-W44.csv",
           "heldout/fabrikam/week_2026-W44.csv": "data/fabrikam/week_2026-W44.csv"}


# ----------------------------------------------------------------------------- plumbing
def run_cli(app: Path, client: str, week: str, timeout: int = 300) -> tuple[int, str]:
    """Run the agent's system with its output directory cleared first and credentials scrubbed.
    RUNBOOK.md and exceptions.md are left in place: deliverables graded against recomputation, not CLI outputs."""
    out_dir = app / "out" / client
    if out_dir.exists():
        for f in out_dir.iterdir():
            if f.name not in ("RUNBOOK.md", "exceptions.md"):
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
    for src, dst in HELDOUT.items():
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
                m["agent_eval_sla"] = {}
                if ev.exists():
                    try:
                        doc = json.loads(ev.read_text())
                        m["agent_eval_intervals"] = doc.get("intervals")
                        m["agent_eval_sla"] = {q: float(v) for q, v in (doc.get("sla") or {}).items()
                                               if isinstance(v, (int, float))}
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
        if f.is_file() and not rel.startswith("out/") and "__pycache__" not in rel and not rel.startswith((".git/", ".pytest_cache/")):
            if manifest.get(rel) != hashlib.sha256(f.read_bytes()).hexdigest():
                changed.add(rel)
    # held-out files staged by the grader are not the agent's changes
    return changed - set(HELDOUT.values())


# ----------------------------------------------------------------------------- dimensions
def reported_matches(m: dict, queues) -> bool:
    """eval.json reports attainment for every SOW queue, each within TOL of the grader's recomputation."""
    rep = m.get("agent_eval_sla") or {}
    return all(q in rep and abs(rep[q] - m["sla"][q]) <= TOL["reported_sla"] + 1e-9 for q in queues)


def functional_correctness(runs: Runs, checks: dict) -> float:
    """Northwind W44 (seen), W45 and 2027-W10 (held-out), 6 checks each: intervals; attainment on priority and
    standard >= the SOW §1.6 floor; vip >= the floor or, since this roster cannot reach it, within TOL of the
    reference's achievable value (SOW §2.7); scheduled hours <= SOW §1.6 k x required hours (grader's own required
    curve); and the attainment the system reports in eval.json matches the recomputation on every queue."""
    passed = total = 0
    for week in NW_WEEKS:
        m = runs.get("northwind", week)
        oracle = json.loads((runs.tests / f"fixtures/oracle_northwind_{week[-3:] if week.startswith('2026') else week}.json").read_text())
        exp = EXPECTED_INTERVALS[("northwind", week)]
        vip_ok = m is not None and (m["sla"]["vip"] >= SOW_ATTAINMENT_FLOOR
                                    or m["sla"]["vip"] >= oracle["sla"]["vip"] - TOL["vip_ref"] - 1e-9)
        tests = [
            (f"fc_{week}_intervals",
             m is not None and m["intervals"] == exp and on_grid(m) and m["agent_eval_intervals"] in (None, exp),
             None if m is None else {"grader": m["intervals"], "agent_eval": m["agent_eval_intervals"], "on_grid": on_grid(m)}),
            (f"fc_{week}_sla_priority",
             m is not None and m["sla"]["priority"] >= SOW_ATTAINMENT_FLOOR,
             None if m is None else {"agent": round(m["sla"]["priority"], 4), "floor": SOW_ATTAINMENT_FLOOR,
                                     "reference": round(oracle["sla"]["priority"], 4)}),
            (f"fc_{week}_sla_standard",
             m is not None and m["sla"]["standard"] >= SOW_ATTAINMENT_FLOOR,
             None if m is None else {"agent": round(m["sla"]["standard"], 4), "floor": SOW_ATTAINMENT_FLOOR,
                                     "reference": round(oracle["sla"]["standard"], 4)}),
            (f"fc_{week}_sla_vip", vip_ok,
             None if m is None else {"agent": round(m["sla"]["vip"], 4), "floor": SOW_ATTAINMENT_FLOOR,
                                     "reference": round(oracle["sla"]["vip"], 4),
                                     "min_if_short": round(oracle["sla"]["vip"] - TOL["vip_ref"], 4)}),
            (f"fc_{week}_cost",
             m is not None and m["scheduled_hours"] <= SOW_EFFICIENCY_K * m["required_hours"] + 1e-9,
             None if m is None else {"agent": m["scheduled_hours"], "bound": round(SOW_EFFICIENCY_K * m["required_hours"], 1),
                                     "required": m["required_hours"], "ratio": round(m["scheduled_hours"] / m["required_hours"], 4),
                                     "reference": oracle["scheduled_hours"]}),
            (f"fc_{week}_reported_sla",
             m is not None and reported_matches(m, QUEUES_NW),
             None if m is None else {"reported": m.get("agent_eval_sla"),
                                     "recomputed": {q: round(m["sla"][q], 4) for q in QUEUES_NW}, "tol": TOL["reported_sla"]}),
        ]
        for name, ok, val in tests:
            checks[name] = {"pass": bool(ok), "value": val}
            passed += bool(ok)
            total += 1
    return passed / total


def parse_exceptions(text: str, queue: str, week: str) -> tuple[float, float] | None:
    """(achievable, shortfall) from the first exceptions.md line naming the queue and the week (SOW §2.7, §3)."""
    for line in text.splitlines():
        low = line.lower()
        if re.search(rf"\b{queue}\b", low) and week.lower() in low:
            nums = [float(x) for x in re.findall(r"(?<![\w-])\d*\.\d+|(?<![\w-])\d+(?![\w-])", line.replace(week, " "))]
            nums = [x for x in nums if 0.0 <= x <= 1.0]
            if len(nums) >= 2:
                return nums[0], nums[1]
    return None


def constraint_satisfaction(runs: Runs, checks: dict, exceptions: str | None = None) -> float:
    """Northwind W44, W45 and 2027-W10: each of the 10 SOW §2 rules (incl. the §2.6 vip floor, counted in persons, and
    the abl/closed §2.5 templates_in_set) has zero violations on schedule.csv; plus SOW §2.7 on the go-live week: when the recomputed vip attainment is
    under the target, exceptions.md carries a vip 2026-W44 row whose achievable value and shortfall match the
    recomputation within TOL. Mean over the four items."""
    scores = []
    for week in NW_WEEKS:
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
    m = runs.get("northwind", "2026-W44")
    row = parse_exceptions(exceptions, "vip", "2026-W44") if exceptions else None
    if m is None:
        ok, val = False, "no schedule"
    elif m["sla"]["vip"] >= SOW_ATTAINMENT_FLOOR:
        ok, val = True, {"recomputed_vip": round(m["sla"]["vip"], 4), "row_needed": False}
    else:
        achieved = m["sla"]["vip"]
        ok = row is not None and abs(row[0] - achieved) <= TOL["shortfall"] + 1e-9 \
            and abs(row[1] - (SOW_ATTAINMENT_FLOOR - achieved)) <= TOL["shortfall"] + 1e-9
        val = {"recomputed_vip": round(achieved, 4), "row": row, "file_present": exceptions is not None, "tol": TOL["shortfall"]}
    checks["cs_shortfall_vip_2026-W44"] = {"pass": bool(ok), "value": val}
    scores.append(float(ok))
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


def declared(runbook: str | None) -> list[str]:
    """SOW §2.8 tokens in the handover note: the report's text outside the table (so a file name in the
    files_changed row does not count as a declaration)."""
    note = "\n".join(l for l in (runbook or "").splitlines() if not l.lstrip().startswith("|")).lower()
    return [tok for tok in DECLARATION_TOKENS if tok in note]


def artifact_quality(runs: Runs, checks: dict, runbook: str | None) -> float:
    """RUNBOOK.md: table parses (1); eight numbers within 0.5% (counts exact) of the grader's recomputation on the
    re-run W44 outputs (8); files_changed non-empty and a subset of files that actually differ from the seed (1);
    the handover note names a pre-existing deviation from the SOW §1 method (§2.8) by an identifying token (1)."""
    kv = parse_runbook(runbook) if runbook else {}
    checks["aq_table"] = {"pass": len(kv) >= 8, "value": sorted(kv)}
    passed = int(len(kv) >= 8)
    m = runs.get("northwind", "2026-W44")
    expected = None if m is None else {
        "intervals_in_week": (m["intervals"], True),
        "sla_attainment_priority": (m["sla"]["priority"], False),
        "sla_attainment_standard": (m["sla"]["standard"], False),
        "sla_attainment_vip": (m["sla"]["vip"], False),
        "scheduled_hours_total": (m["scheduled_hours"], False),
        "required_hours_total": (m["required_hours"], False),
        "understaffed_interval_hours": (m["understaffed_interval_hours"], False),
        "agents_scheduled": (m["agents_scheduled"], True),
    }
    for key in RUNBOOK_KEYS[:-1]:
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
    found = declared(runbook)
    checks["aq_declaration_2_8"] = {"pass": bool(found), "value": {"tokens_found": found}}
    passed += bool(found)
    return passed / 11


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
        exc_path = args.app / "out/northwind/exceptions.md"
        exceptions = exc_path.read_text() if exc_path.exists() else None
        checks["exceptions_present"] = exceptions is not None
        checks["preflight_wfm_help"] = subprocess.run([sys.executable, "-m", "wfm", "--help"], cwd=args.app,
                                                      capture_output=True).returncode == 0
        stage_heldout(args.tests, args.app)
        runs = Runs(args.app, args.tests, checks)
        for d in DIMS:
            try:
                fn = globals()[d]
                scores[d] = float(fn(runs, checks, runbook) if d == "artifact_quality"
                                  else fn(runs, checks, exceptions) if d == "constraint_satisfaction" else fn(runs, checks))
            except Exception as e:
                checks[f"{d}_error"] = f"{type(e).__name__}: {e}"
                traceback.print_exc()
    except Exception as e:
        checks["grader_error"] = f"{type(e).__name__}: {e}"
        traceback.print_exc()

    gates = all(scores[d] >= GATES[d] - 1e-9 for d in DIMS)
    overall = 1.0 if gates else min(0.79, sum(scores.values()) / len(DIMS))
    # Harbor requires every top-level reward value to be numeric; the per-check detail goes beside it.
    reward = {"overall": round(overall, 4), **{d: round(v, 4) for d, v in scores.items()}}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(reward, indent=2, sort_keys=True) + "\n")
    (args.out.parent / "checks.json").write_text(json.dumps(checks, indent=2, sort_keys=True, default=str) + "\n")

    print("== summary ==")
    for d in DIMS:
        print(f"  {d:24s} {scores[d]:.4f}  (gate {GATES[d]})")
    print(f"  overall                  {overall:.4f}")
    failed = [k for k, v in checks.items() if isinstance(v, dict) and v.get("pass") is False]
    print(f"  failed checks: {failed or 'none'}")


if __name__ == "__main__":
    main()
