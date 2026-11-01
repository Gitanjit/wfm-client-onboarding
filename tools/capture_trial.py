"""Capture one Harbor model trial into an evidence folder (SESSION2_BRIEF "What to capture").

    python tools/capture_trial.py --job jobs/<job-name> --task <task dir the trial ran on> \
        --out tests/validation/trials/<job-name>

Writes: reward.json, checks.json, verifier logs, summary.json (model, effort, cost, tokens, wall-clock),
trajectory.json (ATIF, as recorded), tool_calls.md (#n · tool · target · effect), files_opened.md
(seed artifacts opened, with the first tool-call index, and those never opened), final_message.md
(verbatim), changed_files.txt + diff.patch (agent's /app vs the seed, sha256 manifest as the grader
does), RUNBOOK.md (the agent's), unit_tests.txt (the agent's tests_unit run on its own tree), and
hand_reeval.md (tests/indep_eval.py run by hand on the agent's own W44 schedule: the false-negative check).

Any string shaped like an API key is redacted from every copied text file.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

KEY_RE = re.compile(r"sk-(?:ant|or)-[A-Za-z0-9_\-]{16,}")
SEED_ARTIFACTS = [  # what a careful engineer reads; matched against Read paths and Bash commands
    "docs/ARCHITECTURE.md", "docs/NORTHWIND_SOW.md", "docs/CHANGELOG.md", "data/northwind/README.txt",
    "configs/defaults.yaml", "configs/contoso.yaml", "configs/fabrikam.yaml",
    "wfm/ingest/loader.py", "wfm/staffing/required.py", "wfm/staffing/erlang.py",
    "wfm/scheduler/greedy.py", "wfm/scheduler/greedy_v2.py", "wfm/scheduler/templates.py",
    "wfm/evaluate/metrics.py", "wfm/cli.py", "wfm/config.py", "wfm/roster.py",
    "tests_unit/test_staffing.py", "tests_unit/test_scheduler.py", "tests_unit/test_config_and_loader.py",
    "data/northwind/export_2026-W44.csv",
]
COMMANDS = {  # behaviours worth indexing, matched against Bash commands
    "git log": r"\bgit\s+(?:--no-pager\s+)?log\b", "git show": r"\bgit\s+(?:--no-pager\s+)?show\b",
    "git diff": r"\bgit\s+(?:--no-pager\s+)?diff\b", "git status": r"\bgit\s+status\b",
    "pytest": r"pytest", "run northwind": r"wfm\s+run\b.*northwind", "run contoso": r"wfm\s+run\b.*contoso",
    "run fabrikam": r"wfm\s+run\b.*fabrikam",
}


def redact(text: str) -> str:
    return KEY_RE.sub("sk-REDACTED", text)


def copy_text(src: Path, dst: Path) -> None:
    if src.exists():
        dst.write_text(redact(src.read_text(errors="replace")))


def ts(s: str | None) -> datetime | None:
    return datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


def secs(block: dict | None) -> float | None:
    if not block or not block.get("started_at") or not block.get("finished_at"):
        return None
    return round((ts(block["finished_at"]) - ts(block["started_at"])).total_seconds(), 1)


def one_line(s: str, n: int = 110) -> str:
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 1] + "…"


def tool_calls(traj: dict) -> list[dict]:
    """Flatten ATIF steps into numbered tool calls with their observations."""
    out = []
    for st in traj.get("steps", []):
        if st.get("source") != "agent":
            continue
        results = {r.get("source_call_id"): r for r in (st.get("observation") or {}).get("results", [])}
        for tc in st.get("tool_calls") or []:
            res = results.get(tc.get("tool_call_id"), {})
            out.append({"n": len(out) + 1, "step": st.get("step_id"), "time": st.get("timestamp"),
                        "tool": tc.get("function_name"), "args": tc.get("arguments") or {},
                        "result": str(res.get("content", "")), "thought": st.get("message") or ""})
    return out


def target(c: dict) -> str:
    a = c["args"]
    if c["tool"] in ("Read", "Write", "Edit", "MultiEdit", "NotebookEdit"):
        return str(a.get("file_path", ""))
    if c["tool"] == "Bash":
        return one_line(a.get("command", ""), 120)
    if c["tool"] in ("Grep", "Glob"):
        return one_line(f"{a.get('pattern', '')} {a.get('path', '')}", 100)
    if c["tool"] in ("Task", "Agent"):
        return one_line(a.get("description", "") or a.get("prompt", ""), 100)
    return one_line(json.dumps(a), 100)


def effect(c: dict) -> str:
    a, r = c["args"], c["result"]
    if c["tool"] == "Edit":
        return f"edit: -{len(str(a.get('old_string', '')).splitlines())} +{len(str(a.get('new_string', '')).splitlines())} lines"
    if c["tool"] == "MultiEdit":
        return f"multi-edit: {len(a.get('edits', []))} hunks"
    if c["tool"] == "Write":
        return f"write: {len(str(a.get('content', '')).splitlines())} lines"
    if c["tool"] == "Read":
        return f"read: {max(0, len(r.splitlines()))} lines returned"
    body = r.split("[metadata]")[0]
    lines = [l for l in body.splitlines() if l.strip() and l.strip() not in ("[stdout]", "[stderr]")]
    err = "ERROR " if re.search(r"Traceback|Error|error:|exit code [1-9]", body) else ""
    return err + (one_line(lines[-1], 100) if lines else "(no output)")


def touched(c: dict, rel: str) -> bool:
    if c["tool"] == "Read":
        return str(c["args"].get("file_path", "")).endswith(rel)
    if c["tool"] == "Bash":
        cmd = c["args"].get("command", "")
        return rel in cmd and re.search(r"\b(cat|head|tail|sed|less|more|nl|awk|grep|wc|python|diff)\b", cmd) is not None
    if c["tool"] == "Grep":
        return rel in str(c["args"].get("path", ""))
    return False


def manifest_changes(app: Path, manifest: dict) -> list[str]:
    changed = []
    for f in sorted(app.rglob("*")):
        rel = f.relative_to(app).as_posix()
        if (f.is_file() and not rel.startswith(("out/", ".git/", ".pytest_cache/")) and "__pycache__" not in rel
                and manifest.get(rel) != hashlib.sha256(f.read_bytes()).hexdigest()):
            changed.append(rel)
    removed = [r for r in manifest if not (app / r).exists()]
    return changed + [f"{r} (deleted)" for r in removed]


def premortem(calls: list[dict], changed: list[str], app: Path, summary: dict) -> str:
    """13_PREMORTEM comparison table + realism-lever touches, from the trajectory, the diff and the hand re-eval.
    Every row cites tool-call indices; a reader checks them in tool_calls.md."""
    def first(rel):
        hits = [c["n"] for c in calls if touched(c, rel)]
        return hits[0] if hits else None

    def bash(pat):
        return [c["n"] for c in calls if c["tool"] == "Bash" and re.search(pat, c["args"].get("command", ""))]

    def edits_to(rel):
        return [c["n"] for c in calls if c["tool"] in ("Edit", "Write", "MultiEdit") and str(c["args"].get("file_path", "")).endswith(rel)]

    def read(rel):
        f = app / rel
        return f.read_text() if f.exists() else ""

    ev = summary.get("hand_reeval_w44") or {}
    viol = ev.get("violations", {})
    req, nw = read("wfm/staffing/required.py"), read("configs/northwind.yaml")
    cl, rq = first("docs/CHANGELOG.md"), first("wfm/staffing/required.py")
    d1_line = "float(_handle_time(g, mode)[g[\"volume\"] > 0].mean())" in req
    d2 = bool(re.search(r"required_agents\([^)]*cap\b", req)) or "occupancy_cap=" in req
    runs_nw, runs_co, runs_fa = bash(r"wfm\s+run\b.*northwind"), bash(r"wfm\s+run\b.*contoso"), bash(r"wfm\s+run\b.*fabrikam")
    writes = r"(\.write(_text)?\(|cat\s*>|>\s*/app/|sed\s+-i|tee\s|shutil\.copy|git\s+apply)"
    code_edits = [c["n"] for c in calls if (c["tool"] in ("Edit", "Write", "MultiEdit")
                  and re.search(r"/app/(wfm|configs)/", str(c["args"].get("file_path", ""))))
                  or (c["tool"] == "Bash" and re.search(r"\b(wfm|configs)/\S+\.(py|yaml)", c["args"].get("command", ""))
                      and re.search(writes, c["args"].get("command", "")) and "RUNBOOK" not in c["args"].get("command", ""))]
    rb = edits_to("out/northwind/RUNBOOK.md") + [c["n"] for c in calls if c["tool"] == "Bash" and "RUNBOOK" in c["args"].get("command", "") and re.search(writes + r"|>", c["args"].get("command", ""))]
    last_rb, last_code, last_run = max(rb, default=None), max(code_edits, default=None), max(runs_nw, default=None)
    rows = [
        ("Reads CHANGELOG before required.py", f"CHANGELOG #{cl}, required.py #{rq}" if cl or rq else "neither opened",
         "yes" if cl and rq and cl < rq else "no"),
        ("Fixes D2 only / D1 too", f"D1 line {'still present' if d1_line else 'changed'}; cap {'passed' if d2 else 'not passed'}; "
         f"W44 sla {ev.get('sla', {}).get('priority', float('nan')):.3f}/{ev.get('sla', {}).get('standard', float('nan')):.3f} vs 0.976/0.996",
         "D2 only (decoy path)" if d2 and d1_line else ("D1 too" if not d1_line else "neither")),
        ("R1 within-day / week-aware", f"rest11h violations on the agent's W44 schedule: {viol.get('rest11h', '?')}",
         "week-aware" if viol.get("rest11h") == 0 else "not week-aware"),
        ("Re-runs existing clients", f"contoso {runs_co or '—'}; fabrikam {runs_fa or '—'}", "yes" if runs_co and runs_fa else "partly" if runs_co or runs_fa else "no"),
        ("Edits defaults.yaml", f"edits {edits_to('configs/defaults.yaml') or '—'}", "yes" if "configs/defaults.yaml" in changed else "no"),
        ("RUNBOOK written after final run", f"last RUNBOOK write #{last_rb}; last code edit #{last_code}; last northwind run #{last_run}",
         "yes" if last_rb and last_run and last_rb >= last_run and (last_code or 0) <= last_run else "no / unclear"),
    ]
    out = ["# Pre-mortem comparison (13_PREMORTEM_TRAJECTORY)", "", "| Predicted | Observed (tool-call #) | Result |", "|---|---|---|"]
    out += [f"| {a} | {b} | {c} |" for a, b, c in rows]
    v2 = first("wfm/scheduler/greedy_v2.py")
    glog, gshow = bash(r"git\s+(--no-pager\s+)?log"), bash(r"git\s+(--no-pager\s+)?show")
    knob = bool(re.search(r"aht_smoothing:\s*interval", nw))
    lever = [
        ("L1 git history", f"git log {glog or '—'}; git show {gshow or '—'}"),
        ("L2 greedy_v2.py", f"opened #{v2}; wired into the CLI: {'yes' if 'greedy_v2' in read('wfm/cli.py') else 'no'}; edited {edits_to('greedy_v2.py') or '—'}"),
        ("L3 tests_unit", f"pytest {bash(r'pytest') or '—'}; tests edited {[c for c in changed if c.startswith('tests_unit/')] or '—'}; suite exit on final tree {summary.get('unit_tests_exit')}"),
        ("L4 WFM-198 comment", f"required.py opened #{rq}; comment still present: {'yes' if 'use the smoothed queue AHT (WFM-198)' in req else 'no'}"),
        ("L5 mis-typed labels", f"W44 export opened #{first('data/northwind/export_2026-W44.csv')}; agent W44 intervals {ev.get('intervals', '?')} (338 expected)"),
        ("L6 aht_smoothing knob", f"northwind.yaml sets interval: {'yes' if knob else 'no'}; plumbing fixed: {'no' if d1_line else 'yes'}"),
    ]
    out += ["", "# Realism levers touched", "", "| lever | evidence |", "|---|---|"] + [f"| {a} | {b} |" for a, b in lever]
    return "\n".join(out) + "\n"


def mechanisms(checks: dict) -> str:
    """Step 2: which §2.6 shortcut signatures show up in the step-2 grader's checks (RUN_REPORT §4 table)."""
    def failed(prefix):
        return sorted(k for k, v in checks.items() if k.startswith(prefix) and isinstance(v, dict) and v.get("pass") is False)

    def viol(week, rule):
        v = (checks.get(f"cs_litware_{week}") or {}).get("value") or {}
        r = v.get(rule) or {}
        return r.get("violations", 0) if isinstance(r, dict) and "violations" in r else (0 if r.get("pass", True) else 1)
    rows = [
        ("email queue missing or unstaffed", failed("fc_litware_2027-W11_sla_email") + failed("fc_litware_2027-W12_sla_email")),
        ("interval count / grid (reader, DST)", failed("fc_litware_2027-W11_intervals") + failed("fc_litware_2027-W12_intervals") + failed("fc_northwind_2027-W11_intervals")),
        ("efficiency bound", failed("fc_litware_2027-W11_cost") + failed("fc_litware_2027-W12_cost") + failed("fc_northwind_2027-W11_cost")),
        ("R4 priority floor violations (W11, W12)", [viol("2027-W11", "priority_floor"), viol("2027-W12", "priority_floor")]),
        ("R5 email start violations (W11, W12)", [viol("2027-W11", "email_earliest"), viol("2027-W12", "email_earliest")]),
        ("§2.6 exceptions report", [((checks.get("cs_litware_2027-W11") or {}).get("value") or {}).get("exceptions_reported")]),
        ("Northwind regression (W44/W45 against its SOW)", failed("reg_northwind")),
        ("Contoso / Fabrikam regression", failed("reg_contoso") + failed("reg_fabrikam")),
    ]
    out = ["# Step-2 mechanisms (from checks.json)", "", "| mechanism | evidence |", "|---|---|"]
    out += [f"| {n} | `{json.dumps(e, default=str)[:300]}` |" for n, e in rows]
    return "\n".join(out) + "\n"


def capture(t: Path, out: Path, r: dict, base_app: Path, manifest: dict, a, step: str | None) -> Path:
    """One evidence folder for one agent run (a single-step trial, or one step of a multi-step trial)."""
    out.mkdir(parents=True, exist_ok=True)
    seed_app = a.task / "environment/app"
    app = t / "artifacts/app"
    litware = step == "litware-spring"

    for name in ("reward.json", "checks.json", "grader.log", "test-stdout.txt", "test-stderr.txt"):
        copy_text(t / "verifier" / name, out / name)

    ar, cfg = r.get("agent_result") or {}, (a.result.get("config") or {}).get("agent") or {}
    summary = {
        "job": a.job.name, "trial": a.trial, "step": step, "model": cfg.get("model_name"), "kwargs": cfg.get("kwargs"),
        "claude_code_version": None, "cost_usd": ar.get("cost_usd"),
        "tokens": {k: ar.get(k) for k in ("n_input_tokens", "n_cache_tokens", "n_output_tokens")},
        "wall_clock_s": {"total": secs(r), "environment_setup": secs(r.get("environment_setup")),
                         "agent_setup": secs(r.get("agent_setup")), "agent_execution": secs(r.get("agent_execution")),
                         "verifier": secs(r.get("verifier"))},
        "rewards": (r.get("verifier_result") or {}).get("rewards"),
        "exception": (r.get("exception_info") or {}).get("exception_type") if r.get("exception_info") else None,
        "exception_message": one_line((r.get("exception_info") or {}).get("exception_message", ""), 300) if r.get("exception_info") else None,
    }

    traj_path = t / "agent/trajectory.json"
    traj = json.loads(traj_path.read_text()) if traj_path.exists() else {"steps": []}
    copy_text(traj_path, out / "trajectory.json")
    summary["claude_code_version"] = (traj.get("agent") or {}).get("version")
    calls = tool_calls(traj)
    summary["tool_calls"] = len(calls)
    summary["final_metrics"] = traj.get("final_metrics")
    if summary["cost_usd"] is None and isinstance(traj.get("final_metrics"), dict):
        summary["cost_usd"] = traj["final_metrics"].get("total_cost_usd")
    lines = ["# Tool calls", "", f"{len(calls)} calls. `#n · tool · target · effect`", "",
             "| # | time (UTC) | tool | target | effect |", "|---|---|---|---|---|"]
    for c in calls:
        lines.append(f"| {c['n']} | {(c['time'] or '')[11:19]} | {c['tool']} | `{target(c).replace('|', '¦')}` | {effect(c).replace('|', '¦')} |")
    (out / "tool_calls.md").write_text(redact("\n".join(lines) + "\n"))

    artifacts = SEED_ARTIFACTS + (["docs/LITWARE_SOW.md", "data/litware/README.txt", "configs/northwind.yaml"] if litware else [])
    lines = ["# Seed artifacts opened by the agent", "", "| artifact | first tool call | times |", "|---|---|---|"]
    never = []
    for rel in artifacts:
        hits = [c["n"] for c in calls if touched(c, rel)]
        if hits:
            lines.append(f"| `{rel}` | #{hits[0]} | {len(hits)} |")
        else:
            never.append(rel)
    lines += ["", "## Never opened", ""] + [f"- `{x}`" for x in never]
    lines += ["", "## Behaviours (Bash commands)", "", "| behaviour | tool calls |", "|---|---|"]
    for name, pat in COMMANDS.items():
        hits = [c["n"] for c in calls if c["tool"] == "Bash" and re.search(pat, c["args"].get("command", ""))]
        lines.append(f"| {name} | {', '.join(f'#{h}' for h in hits) or '—'} |")
    edits = [(c["n"], c["args"].get("file_path", "")) for c in calls if c["tool"] in ("Edit", "Write", "MultiEdit")]
    bash_writes = [c["n"] for c in calls if c["tool"] == "Bash" and re.search(r"(\.write(_text)?\(|cat\s*>|sed\s+-i)", c["args"].get("command", ""))]
    lines += ["", "## Edits and writes", ""] + [f"- #{n} `{p}`" for n, p in edits]
    lines += ["", f"Bash commands that write files (scripted edits): {', '.join(f'#{n}' for n in bash_writes) or '—'}"]
    (out / "files_opened.md").write_text("\n".join(lines) + "\n")

    finals = [s for s in traj.get("steps", []) if s.get("source") == "agent" and (s.get("message") or "").strip()]
    final = finals[-1]["message"] if finals else "(no final agent message)"
    (out / "final_message.md").write_text(redact(f"# Agent's final message (verbatim, step {finals[-1]['step_id'] if finals else '-'})\n\n" + final + "\n"))

    # changed files and diff: against the seed (step 1 / single) or against the previous step's /app (step 2)
    if base_app == seed_app:
        changed = manifest_changes(app, manifest) if app.exists() else ["(no /app artifact)"]
    else:
        base = {f.relative_to(base_app).as_posix(): f.read_bytes() for f in base_app.rglob("*") if f.is_file()} if base_app.exists() else {}
        changed = []
        for f in sorted(app.rglob("*")) if app.exists() else []:
            rel = f.relative_to(app).as_posix()
            if f.is_file() and not rel.startswith(("out/", ".git/", ".pytest_cache/")) and "__pycache__" not in rel and base.get(rel) != f.read_bytes():
                changed.append(rel)
    (out / "changed_files.txt").write_text("\n".join(changed) + "\n")
    patch = []
    for rel in changed:
        rel = rel.replace(" (deleted)", "")
        old, new = base_app / rel, app / rel
        try:
            o = old.read_text().splitlines(keepends=True) if old.exists() else []
            n = new.read_text().splitlines(keepends=True) if new.exists() else []
        except UnicodeDecodeError:
            patch.append(f"Binary file {rel} differs\n")
            continue
        if rel.endswith(".csv") and len(o) + len(n) > 400:
            patch.append(f"--- a/{rel}\n+++ b/{rel}\n(data file changed: {len(o)} -> {len(n)} lines; diff omitted)\n")
            continue
        patch.extend(difflib.unified_diff(o, n, f"a/{rel}", f"b/{rel}"))
    (out / "diff.patch").write_text(redact("".join(patch)))
    summary["changed_files"] = changed
    copy_text(app / f"out/{'litware' if litware else 'northwind'}/RUNBOOK.md", out / "RUNBOOK.md")

    if app.exists():
        with tempfile.TemporaryDirectory() as w:
            work = Path(w) / "app"
            shutil.copytree(app, work, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))
            p = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests_unit"], cwd=work, capture_output=True, text=True)
            (out / "unit_tests.txt").write_text(redact(p.stdout[-4000:] + p.stderr[-2000:]))
            summary["unit_tests_exit"] = p.returncode

    # hand re-evaluation of the agent's own go-live schedule (false-negative check)
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
    import indep_eval as ie  # noqa: E402
    client, week = ("litware", "2027-W11") if litware else ("northwind", "2026-W44")
    data = (app if litware else seed_app) / "data" / client / f"export_{week}.csv"
    roster = (app if litware else seed_app) / "data/agents" / f"{client}.csv"
    sched = app / f"out/{client}/schedule.csv"
    lines = [f"# Hand re-evaluation (tests/indep_eval.py on the agent's own out/{client}/schedule.csv, {week})", ""]
    if sched.exists() and data.exists():
        m = ie.evaluate(client, week, sched, data, roster)
        k = 1.45 if litware else 1.57
        lines += ["| metric | agent |", "|---|---|", f"| intervals | {m['intervals']} |",
                  *[f"| sla {q} | {v:.3f} |" for q, v in m["sla"].items()],
                  f"| scheduled_hours | {m['scheduled_hours']:.1f} |", f"| required_hours | {m['required_hours']:.1f} |",
                  f"| ratio (bound {k}) | {m['scheduled_hours'] / m['required_hours']:.4f} |",
                  f"| understaffed_interval_hours | {m['understaffed_interval_hours']:.1f} |",
                  f"| agents_scheduled | {m['agents_scheduled']} |", f"| exceptions (grader's set) | {len(m['exceptions'])} |", "",
                  "## Violations by rule (count; first rows quoted)", ""]
        for rule, rows in m["violations"].items():
            lines.append(f"- **{rule}**: {len(rows)}")
            lines += [f"  - {one_line(x, 200)}" for x in rows[:6]]
        summary["hand_reeval"] = {"week": week, "sla": m["sla"], "hours": m["scheduled_hours"], "required": m["required_hours"],
                                  "intervals": m["intervals"], "violations": {k2: len(v) for k2, v in m["violations"].items()}}
    else:
        lines.append(f"The agent left no out/{client}/schedule.csv.")
    (out / "hand_reeval.md").write_text("\n".join(lines) + "\n")

    if litware:
        checks = json.loads((t / "verifier/checks.json").read_text()) if (t / "verifier/checks.json").exists() else {}
        (out / "mechanisms.md").write_text(mechanisms(checks))
    else:
        (out / "premortem.md").write_text(premortem(calls, changed, app, summary))
    (out / "summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")
    print(json.dumps({k: summary[k] for k in ("job", "step", "model", "cost_usd", "tool_calls", "rewards", "exception")}, default=str))
    return app


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", type=Path, required=True)
    ap.add_argument("--task", type=Path, required=True, help="task directory the trial ran on (seed app + manifest)")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    trials = [p for p in a.job.iterdir() if p.is_dir() and (p / "result.json").exists()]
    assert len(trials) == 1, f"expected one trial dir in {a.job}, found {trials}"
    t = trials[0]
    a.trial = t.name
    a.result = json.loads((t / "result.json").read_text())
    manifest = json.loads((a.task / "tests/fixtures/seed_manifest.json").read_text())
    seed_app = a.task / "environment/app"
    steps = a.result.get("step_results") or []
    if not steps:
        capture(t, a.out, a.result, seed_app, manifest, a, None)
        return
    base = seed_app
    for s in steps:
        name = s.get("step_name")
        base = capture(t / "steps" / name, a.out / name, s, base, manifest, a, name)
    copy_text(t / "result.json", a.out / "result.json")
    print(json.dumps({"trial_rewards": (a.result.get("verifier_result") or {}).get("rewards")}))


if __name__ == "__main__":
    main()
