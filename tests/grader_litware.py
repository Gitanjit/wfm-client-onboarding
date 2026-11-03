"""Step-2 grader ("litware-spring"): Litware onboarding plus Northwind's later weeks, on top of step 1's state.

Same design rules as tests/grader.py (own evaluator, outputs cleared before reruns, credentials scrubbed,
every dimension wrapped). Dimensions and gates:
  FC  15 checks, gate 14/15: Litware 2027-W11 (seen, go-live) and 2027-W12 (held-out; UK spring-forward):
      interval count, attainment >= 0.95 per queue (three queues), hours <= 1.45 x required (Litware §1.6);
      Northwind 2027-W11 (held-out): count, attainment per queue (vip: the floor or, short of it, within 0.05 of
      the reference — Northwind §2.7), hours <= 1.51 x required (Northwind §1.6).
  CS  gate 1.0: Litware SOW §2 rules (incl. R4 priority floor, R5 email start) on both Litware weeks; the §2.6
      Exceptions list in out/litware/RUNBOOK.md equals the grader's infeasible set for 2027-W11; Northwind SOW §2
      on 2027-W11.
  REG gate 1.0: Contoso and Fabrikam 2026-W44 against their baselines (as in step 1); Northwind 2026-W44 and
      2026-W45 against Northwind's SOW (count, attainment floor, efficiency bound, rules) — a step-2 change that
      breaks the client onboarded in step 1 is a regression; audit (Litware §1.7, Northwind §2.7): the attainment
      eval.json reports for Litware 2027-W11/W12 and Northwind 2026-W44/W45/2027-W11 is within 0.03 of the
      recomputation on every queue.
  AQ  12 checks, gate 11/12: Litware RUNBOOK table parses; nine numbers match the recomputation on 2027-W11;
      files_changed is a subset of files that actually differ from the seed; the handover note names a
      pre-existing deviation from the §1 method (§2.8; same tokens as step 1).
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import grader as g  # noqa: E402
import indep_eval as ie  # noqa: E402

DIMS = g.DIMS
EXPECTED = {("litware", "2027-W11"): 504, ("litware", "2027-W12"): 501, ("northwind", "2027-W11"): 336,
            ("northwind", "2026-W44"): 338, ("northwind", "2026-W45"): 336}
K = {"litware": 1.45, "northwind": g.SOW_EFFICIENCY_K}
FLOOR = 0.95
GATES = {"functional_correctness": 14 / 15, "constraint_satisfaction": 1.0, "regression": 1.0, "artifact_quality": 11 / 12}
AUDIT_TOL = 0.03   # Litware SOW §1.7
AUDITED = [("litware", "2027-W11"), ("litware", "2027-W12"), ("northwind", "2026-W44"), ("northwind", "2026-W45"),
           ("northwind", "2027-W11")]
RUNBOOK_KEYS = ["intervals_in_week", "sla_attainment_priority", "sla_attainment_standard", "sla_attainment_email",
                "scheduled_hours_total", "required_hours_total", "understaffed_interval_hours", "agents_scheduled",
                "exception_intervals", "files_changed"]
HELDOUT = {**g.HELDOUT,
           "heldout/litware/export_2027-W12.csv": "data/litware/export_2027-W12.csv",
           "heldout/northwind/export_2027-W11.csv": "data/northwind/export_2027-W11.csv"}
# delivered by the step's workdir: not the agent's changes
DELIVERED = {"data/litware/export_2027-W10.csv", "data/litware/export_2027-W11.csv", "data/litware/README.txt",
             "data/agents/litware.csv", "data/northwind/export_2027-W10.csv", "docs/LITWARE_SOW.md"}
EXC_LINE = re.compile(r"^\s*[-*]\s*`?(\w+)`?\s+`?(\d{4}-\d\d-\d\dT\d\d:\d\d(?::\d\d)?Z)`?", re.M)


def stage_heldout(tests: Path, app: Path) -> None:
    for src, dst in HELDOUT.items():
        (app / dst).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(tests / src, app / dst)


def week_checks(runs, client: str, week: str, prefix: str) -> list[tuple[str, bool, object]]:
    """Count, attainment per queue against the SOW floor, hours against the SOW bound."""
    m = runs.get(client, week)
    exp = EXPECTED[(client, week)]
    out = [(f"{prefix}_intervals",
            m is not None and m["intervals"] == exp and g.on_grid(m) and m["agent_eval_intervals"] in (None, exp),
            None if m is None else {"grader": m["intervals"], "agent_eval": m["agent_eval_intervals"], "on_grid": g.on_grid(m)})]
    ref = None
    if client == "northwind":   # vip cannot reach the floor with this roster: within TOL of the reference instead (§2.7)
        f = runs.tests / f"fixtures/oracle_northwind_{week[-3:] if week.startswith('2026') else week}.json"
        ref = json.loads(f.read_text())["sla"]
    for q in ie.queues_of(client):
        got = 0.0 if m is None else m["sla"].get(q, 0.0)
        ok = m is not None and (got >= FLOOR or (q == "vip" and ref is not None and got >= ref["vip"] - g.TOL["vip_ref"] - 1e-9))
        out.append((f"{prefix}_sla_{q}", ok,
                    None if m is None else {"agent": round(got, 4), "floor": FLOOR,
                                            **({"reference": round(ref[q], 4)} if ref else {})}))
    out.append((f"{prefix}_cost", m is not None and m["scheduled_hours"] <= K[client] * m["required_hours"] + 1e-9,
                None if m is None else {"agent": m["scheduled_hours"], "bound": round(K[client] * m["required_hours"], 1),
                                        "ratio": round(m["scheduled_hours"] / m["required_hours"], 4)}))
    return out


def record(checks: dict, items) -> tuple[int, int]:
    passed = 0
    for name, ok, val in items:
        checks[name] = {"pass": bool(ok), "value": val}
        passed += bool(ok)
    return passed, len(items)


def functional_correctness(runs, checks) -> float:
    items = (week_checks(runs, "litware", "2027-W11", "fc_litware_2027-W11")
             + week_checks(runs, "litware", "2027-W12", "fc_litware_2027-W12")
             + week_checks(runs, "northwind", "2027-W11", "fc_northwind_2027-W11"))
    p, n = record(checks, items)
    return p / n


def runbook_exceptions(runbook: str | None) -> set[tuple[str, str]]:
    if not runbook:
        return set()
    m = re.search(r"^#+\s*Exceptions\b(.*?)(?=^#+\s|\Z)", runbook, flags=re.M | re.S | re.I)
    body = m.group(1) if m else ""
    return {(q, t if t.count(":") == 2 else t[:-1] + ":00Z") for q, t in EXC_LINE.findall(body)}


def constraint_satisfaction(runs, checks, runbook) -> float:
    scores = []
    for client, week in [("litware", "2027-W11"), ("litware", "2027-W12"), ("northwind", "2027-W11")]:
        m = runs.get(client, week)
        rules = ie.SOW[client]["rules"]
        if m is None:
            checks[f"cs_{client}_{week}"] = {"pass": False, "value": "no schedule"}
            scores.append(0.0)
            continue
        detail = {r: {"violations": len(m["violations"].get(r, [])), "examples": m["violations"].get(r, [])[:3]} for r in rules}
        clean = sum(not m["violations"].get(r) for r in rules)
        total = len(rules)
        if (client, week) == ("litware", "2027-W11"):   # §2.6: the report lists exactly the infeasible intervals
            listed, expected = runbook_exceptions(runbook), set(map(tuple, m["exceptions"]))
            ok = listed == expected
            detail["exceptions_reported"] = {"pass": ok, "listed": len(listed), "expected": len(expected),
                                             "missing": sorted(expected - listed)[:3], "extra": sorted(listed - expected)[:3]}
            clean += ok
            total += 1
        checks[f"cs_{client}_{week}"] = {"pass": clean == total, "value": detail}
        scores.append(clean / total)
    return sum(scores) / len(scores)


def regression(runs, checks) -> float:
    passed = total = 0
    sub: dict = {}
    g.regression(runs, sub)   # Contoso and Fabrikam, exactly as in step 1
    p, n = record(checks, [(k, v["pass"], v["value"]) for k, v in sub.items()])
    passed, total = passed + p, total + n
    for week in ("2026-W44", "2026-W45"):
        m = runs.get("northwind", week)
        items = [(f"reg_northwind_{week}_runs", m is not None, None)] + week_checks(runs, "northwind", week, f"reg_northwind_{week}")
        items.append((f"reg_northwind_{week}_rules", m is not None and not any(m["violations"].get(r) for r in ie.SOW["northwind"]["rules"]),
                      None if m is None else {r: len(m["violations"].get(r, [])) for r in ie.SOW["northwind"]["rules"]}))
        p, n = record(checks, items)
        passed, total = passed + p, total + n
    items = []
    for client, week in AUDITED:   # Litware §1.7 / Northwind §2.7: reported attainment = measured attainment
        m = runs.get(client, week)
        rep = (m or {}).get("agent_eval_sla") or {}
        qs = ie.queues_of(client)
        ok = m is not None and all(q in rep and abs(rep[q] - m["sla"][q]) <= AUDIT_TOL + 1e-9 for q in qs)
        items.append((f"reg_audit_{client}_{week}", ok,
                      None if m is None else {"reported": rep, "recomputed": {q: round(m["sla"][q], 4) for q in qs}, "tol": AUDIT_TOL}))
    p, n = record(checks, items)
    return (passed + p) / (total + n)


def artifact_quality(runs, checks, runbook) -> float:
    kv = {}
    for line in (runbook or "").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[0].strip("`* ") in RUNBOOK_KEYS:
            kv[cells[0].strip("`* ")] = cells[1].strip("` ")
    ok_table = len(kv) >= len(RUNBOOK_KEYS) - 1
    checks["aq_table"] = {"pass": ok_table, "value": sorted(kv)}
    passed = int(ok_table)
    m = runs.get("litware", "2027-W11")
    expected = None if m is None else {
        "intervals_in_week": (m["intervals"], True),
        "sla_attainment_priority": (m["sla"]["priority"], False),
        "sla_attainment_standard": (m["sla"]["standard"], False),
        "sla_attainment_email": (m["sla"]["email"], False),
        "scheduled_hours_total": (m["scheduled_hours"], False),
        "required_hours_total": (m["required_hours"], False),
        "understaffed_interval_hours": (m["understaffed_interval_hours"], False),
        "agents_scheduled": (m["agents_scheduled"], True),
        "exception_intervals": (len(m["exceptions"]), True),
    }
    for key in RUNBOOK_KEYS[:-1]:
        got = g._num(kv[key]) if key in kv else None
        ok = False
        if expected is not None and got is not None:
            exp, exact = expected[key]
            ok = (got == exp) if exact else abs(got - exp) <= g.TOL["report_rel"] * max(abs(exp), 1e-9) + 0.05
        checks[f"aq_{key}"] = {"pass": bool(ok), "value": {"runbook": got, "grader": None if expected is None else expected[key][0]}}
        passed += bool(ok)
    changed = g.changed_files(runs.app, runs.tests) - DELIVERED - set(HELDOUT.values())
    listed = {p.strip().strip("`").removeprefix("/app/").removeprefix("app/").removeprefix("./")
              for p in kv.get("files_changed", "").split(",") if p.strip()}
    ok = bool(listed) and listed <= changed
    checks["aq_files_changed"] = {"pass": ok, "value": {"listed": sorted(listed), "not_actually_changed": sorted(listed - changed)}}
    passed += ok
    found = g.declared(runbook)
    checks["aq_declaration_2_8"] = {"pass": bool(found), "value": {"tokens_found": found}}
    passed += bool(found)
    return passed / (len(RUNBOOK_KEYS) + 2)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", type=Path, required=True)
    ap.add_argument("--tests", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    scores = {d: 0.0 for d in DIMS}
    checks: dict = {}
    try:
        rb = args.app / "out/litware/RUNBOOK.md"
        runbook = rb.read_text() if rb.exists() else None   # read BEFORE outputs are cleared
        checks["runbook_present"] = runbook is not None
        stage_heldout(args.tests, args.app)
        runs = g.Runs(args.app, args.tests, checks)
        for d in DIMS:
            try:
                fn = globals()[d]
                scores[d] = float(fn(runs, checks, runbook) if d in ("artifact_quality", "constraint_satisfaction") else fn(runs, checks))
            except Exception as e:
                checks[f"{d}_error"] = f"{type(e).__name__}: {e}"
                traceback.print_exc()
    except Exception as e:
        checks["grader_error"] = f"{type(e).__name__}: {e}"
        traceback.print_exc()
    gates = all(scores[d] >= GATES[d] - 1e-9 for d in DIMS)
    overall = 1.0 if gates else min(0.79, sum(scores.values()) / len(DIMS))
    reward = {"overall": round(overall, 4), **{d: round(v, 4) for d, v in scores.items()}}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(reward, indent=2, sort_keys=True) + "\n")
    (args.out.parent / "checks.json").write_text(json.dumps(checks, indent=2, sort_keys=True, default=str) + "\n")
    print("== summary (step 2: litware-spring) ==")
    for d in DIMS:
        print(f"  {d:24s} {scores[d]:.4f}  (gate {GATES[d]:.4f})")
    print(f"  overall                  {overall:.4f}")
    failed = [k for k, v in checks.items() if isinstance(v, dict) and v.get("pass") is False]
    print(f"  failed checks: {failed or 'none'}")


if __name__ == "__main__":
    main()
