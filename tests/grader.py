"""tests/grader.py — skeleton. Fill the TODOs in Phase 4; keep the structure.

Design rules (04_VERIFIER_SPEC.md):
  * end state only; never import from /app/wfm; never read /app/configs for targets
  * always write reward.json, even on exceptions
  * one docstring per check, numbers recorded under "checks" for legibility
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import indep_eval as ie  # own Erlang C, own coverage evaluator, SOW targets hard-coded  # noqa: E402

DIMS = ["functional_correctness", "constraint_satisfaction", "regression", "artifact_quality"]

SOW = {  # targets are the contract, not the config files
    "northwind": {"priority": (0.90, 30), "standard": (0.80, 20), "occupancy_cap": 0.85,
                  "rules": ["rest11h", "split_pt_only", "break_window_max_surplus",
                            "weekly_hours", "consecutive_days", "skill_match", "no_overlap", "coverage_sane"]},
    "contoso":   {"priority": (0.80, 20), "standard": (0.80, 20), "occupancy_cap": 0.85,
                  "rules": ["weekly_hours", "consecutive_days", "skill_match", "no_overlap"]},
    "fabrikam":  {"priority": (0.80, 20), "standard": (0.80, 20), "occupancy_cap": 0.85,
                  "rules": ["weekly_hours", "consecutive_days", "skill_match", "no_overlap"]},
}
EXPECTED_INTERVALS = {("northwind", "2026-W44"): 338, ("northwind", "2026-W45"): 336,
                      ("contoso", "2026-W44"): 672, ("fabrikam", "2026-W44"): 169}
TOL = {"sla": 0.02, "cost": 1.10, "reg_sla": 0.02, "reg_cost": 1.10, "report_rel": 0.005}


SCRUB = ("OPENROUTER_API_KEY", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "CLAUDE_CODE_OAUTH_TOKEN", "OPENAI_API_KEY")


def run_cli(app: Path, client: str, week: str, timeout: int = 300) -> tuple[int, str]:
    """Run the agent's system with outputs cleared first (a stale hand-written file must not survive)
    and credentials scrubbed from the environment. Returns (exit_code, combined output)."""
    import os
    out_dir = app / "out" / client
    if out_dir.exists():
        shutil.rmtree(out_dir)
    env = {k: v for k, v in os.environ.items() if k not in SCRUB}
    try:
        p = subprocess.run([sys.executable, "-m", "wfm", "run", "--client", client, "--week", week],
                           cwd=app, capture_output=True, text=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return 124, "timeout"
    return p.returncode, (p.stdout + p.stderr)[-4000:]


def read_runbook_early(app: Path) -> str | None:
    """RUNBOOK.md is a deliverable, not a CLI output: capture it BEFORE outputs are cleared."""
    f = app / "out/northwind/RUNBOOK.md"
    return f.read_text() if f.exists() else None


def changed_files(app: Path, tests: Path) -> set[str]:
    """Files under /app whose sha256 differs from the seed manifest, plus new files. Git is not trusted."""
    import hashlib
    manifest = json.loads((tests / "fixtures/seed_manifest.json").read_text())
    changed = set()
    for f in app.rglob("*"):
        if f.is_file() and "/out/" not in str(f) and "__pycache__" not in str(f):
            rel = str(f.relative_to(app))
            h = hashlib.sha256(f.read_bytes()).hexdigest()
            if manifest.get(rel) != h:
                changed.add(rel)
    return changed


def stage_heldout(tests: Path, app: Path) -> None:
    """Copy held-out weeks into the agent's data dirs (grader-side only)."""
    for src, dst in [
        (tests / "heldout/northwind/export_2026-W45.csv", app / "data/northwind/export_2026-W45.csv"),
        (tests / "heldout/contoso/week_2026-W44.csv",     app / "data/contoso/week_2026-W44.csv"),
        (tests / "heldout/fabrikam/week_2026-W44.csv",    app / "data/fabrikam/week_2026-W44.csv"),
    ]:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)


def functional_correctness(app, tests, checks) -> float:
    """Northwind W44 (seen) + W45 (held-out): interval count, SLA per queue vs oracle-0.03, cost <= oracle*1.10."""
    passed, total = 0, 0
    for week in ["2026-W44", "2026-W45"]:
        rc, out = run_cli(app, "northwind", week)
        checks[f"fc_{week}_cli_exit"] = rc
        sched = app / "out/northwind/schedule.csv"
        oracle = json.loads((tests / f"fixtures/oracle_northwind_{week[-3:]}.json").read_text())
        m = ie.evaluate("northwind", week, sched, tests, SOW["northwind"]) if rc == 0 and sched.exists() else None
        for name, ok in [
            (f"fc_{week}_intervals", m is not None and m["intervals"] == EXPECTED_INTERVALS[("northwind", week)]),
            (f"fc_{week}_sla_priority", m is not None and m["sla"]["priority"] >= oracle["sla"]["priority"] - TOL["sla"]),
            (f"fc_{week}_sla_standard", m is not None and m["sla"]["standard"] >= oracle["sla"]["standard"] - TOL["sla"]),
            (f"fc_{week}_cost", m is not None and m["scheduled_hours"] <= oracle["scheduled_hours"] * TOL["cost"]),
        ]:
            checks[name] = {"pass": bool(ok), "value": None if m is None else m.get(name.split("_", 2)[-1])}
            passed += bool(ok); total += 1
    return passed / total


def constraint_satisfaction(app, tests, checks) -> float:
    """Northwind W44 + W45: every SOW §2 rule has zero violations (audited on schedule.csv directly)."""
    # TODO: for each week, rerun CLI (or reuse), ie.audit(...) -> {rule: [violations]}; score = rules clean / rules
    raise NotImplementedError


def regression(app, tests, checks) -> float:
    """Contoso W44 + Fabrikam W44 (held-out): runs, interval count, SLA >= baseline-0.02, cost <= baseline*1.15, rules clean."""
    # TODO per 04 §3
    raise NotImplementedError


def artifact_quality(app, tests, checks) -> float:
    """RUNBOOK.md table: present, keys parse, numbers within 0.5% of recomputation on the RE-RUN W44 outputs,
    files_changed non-empty and ⊆ changed_files() (sha256 manifest, not git)."""
    # TODO: parse markdown table; recompute from agent's W44 outputs via ie; git diff --name-only seed..HEAD
    raise NotImplementedError


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", type=Path, required=True)
    ap.add_argument("--tests", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    scores = {d: 0.0 for d in DIMS}
    checks: dict = {}
    try:
        checks["runbook_text_captured"] = read_runbook_early(args.app) is not None
        RUNBOOK_TEXT = read_runbook_early(args.app)  # noqa: N806  (pass into artifact_quality)
        stage_heldout(args.tests, args.app)
        for d in DIMS:
            try:
                scores[d] = float(globals()[d](args.app, args.tests, checks))
            except Exception as e:  # a crashed dimension scores 0 but never kills the grader
                checks[f"{d}_error"] = f"{type(e).__name__}: {e}"
                traceback.print_exc()
    except Exception as e:
        checks["grader_error"] = f"{type(e).__name__}: {e}"
        traceback.print_exc()

    gates = (scores["constraint_satisfaction"] == 1.0 and scores["regression"] == 1.0
             and scores["functional_correctness"] >= 0.875 and scores["artifact_quality"] >= 0.75)
    overall = 1.0 if gates else min(0.79, sum(scores.values()) / len(DIMS))
    reward = {"overall": round(overall, 4), **{d: round(v, 4) for d, v in scores.items()}, "checks": checks}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(reward, indent=2, sort_keys=True))
    print(json.dumps({k: v for k, v in reward.items() if k != "checks"}, indent=2))


if __name__ == "__main__":
    main()
