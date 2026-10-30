"""Local simulation of the Harbor flow for validation variants (04_VERIFIER_SPEC §6).

usage: python tools/validate.py <repo-root> <variant> [<variant> ...]   (variant "all" runs every one)
Copies environment/app to a temp dir, applies the variant, runs the "agent" steps, then runs
tests/grader.py against it and stores reward.json under tests/validation/<variant>.json.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
PY = sys.executable
OUT = REPO / "tests/validation"
OUT.mkdir(exist_ok=True)


def sh(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str), capture_output=True, text=True)
    if p.returncode:
        print(f"    [cmd failed {p.returncode}] {cmd}\n{p.stderr[-800:]}")
    return p


def fresh_app(work: Path) -> Path:
    app = work / "app"
    shutil.copytree(REPO / "environment/app", app, ignore=shutil.ignore_patterns("__pycache__"))
    return app


def apply_patch(app: Path):
    sh(["git", "apply", "--whitespace=nowarn", str(REPO / "solution/oracle.patch")], app)


def solve(app: Path, runbook=True):
    sh([PY, "-m", "wfm", "run", "--client", "northwind", "--week", "2026-W44"], app)
    sh([PY, "-m", "wfm", "run", "--client", "contoso", "--week", "2026-W43"], app)
    sh([PY, "-m", "wfm", "run", "--client", "fabrikam", "--week", "2026-W43"], app)
    if runbook:
        sh([PY, str(REPO / "solution/write_runbook.py"), "--schedule", str(app / "out/northwind/schedule.csv"),
            "--eval", str(app / "out/northwind/eval.json"), "--out", str(app / "out/northwind/RUNBOOK.md"),
            "--patch", str(REPO / "solution/oracle.patch")], app)


def edit(app: Path, rel: str, old: str, new: str):
    f = app / rel
    t = f.read_text()
    assert old in t, f"{rel}: pattern not found: {old!r}"
    f.write_text(t.replace(old, new))


def grade(app: Path, name: str, tests: Path | None = None):
    out = app.parent / "reward.json"
    p = subprocess.run([PY, str(REPO / "tests/grader.py"), "--app", str(app), "--tests", str(tests or REPO / "tests"),
                        "--out", str(out)], capture_output=True, text=True)
    r = json.loads(out.read_text())
    print(f"  {name:28s} overall={r['overall']:.4f} FC={r['functional_correctness']:.3f} CS={r['constraint_satisfaction']:.3f} "
          f"REG={r['regression']:.3f} AQ={r['artifact_quality']:.3f}")
    failed = [k for k, v in r["checks"].items() if isinstance(v, dict) and v.get("pass") is False]
    if failed:
        print(f"      failed: {failed}")
    if p.returncode:
        print(p.stderr[-800:])
    (OUT / f"{name}.json").write_text(json.dumps(r, indent=2, sort_keys=True, default=str) + "\n")
    return r, out.read_text()


VARIANTS = {}


def variant(fn):
    VARIANTS[fn.__name__.replace("_", "-")] = fn
    return fn


@variant
def oracle(app):
    apply_patch(app); solve(app)


@variant
def nop(app):
    pass


@variant
def shallow_1_no_rest(app):
    """oracle minus R1: rest rule switched off"""
    apply_patch(app)
    edit(app, "configs/northwind.yaml", "min_rest_hours: 11", "min_rest_hours: 0")
    solve(app)


@variant
def shallow_2_defaults_grain(app):
    """oracle but defaults.yaml changed to Northwind's grain/tz (D4 regression)"""
    apply_patch(app)
    edit(app, "configs/defaults.yaml", "interval_minutes: 15 ", "interval_minutes: 30 ")
    edit(app, "configs/defaults.yaml", "tz: UTC ", "tz: America/Chicago ")
    solve(app)


@variant
def shallow_3_nat_loader(app):
    """oracle but the loader drops the ambiguous DST hour (ambiguous='NaT' + dropna)"""
    apply_patch(app)
    edit(app, "wfm/ingest/loader.py",
         '    stamp = df["interval_start_local"].str.strip() + df["utc_offset"].str.strip()\n'
         '    df["interval_start_utc"] = pd.to_datetime(stamp, format="%Y-%m-%d %H:%M%z", utc=True)\n',
         '    local = pd.to_datetime(df["interval_start_local"])\n'
         '    df["interval_start_utc"] = local.dt.tz_localize(cfg["tz"], ambiguous="NaT").dt.tz_convert("UTC")\n'
         '    df = df.dropna(subset=["interval_start_utc"])\n')
    solve(app)


@variant
def shallow_4_decoy_d2_only(app):
    """oracle but D1 left in place: weekly-mean AHT, occupancy cap applied (the decoy path)"""
    apply_patch(app)
    edit(app, "wfm/staffing/required.py",
         "            required_agents(r.volume, interval_sec, r.aht_sec, sla[\"target\"], sla[\"seconds\"], cap)\n",
         "            required_agents(r.volume, interval_sec, g.loc[g['volume'] > 0, 'aht_sec'].mean(), sla[\"target\"], sla[\"seconds\"], cap)\n")
    solve(app)


@variant
def shallow_5_midpoint_breaks(app):
    """oracle but breaks at the midpoint (R3 skipped)"""
    apply_patch(app)
    edit(app, "configs/northwind.yaml", "break_placement: max_surplus", "break_placement: midpoint")
    solve(app)


@variant
def d1_fixed_d2_not(app):
    """oracle but occupancy cap not applied (D2 left): should still pass"""
    apply_patch(app)
    edit(app, "wfm/staffing/required.py",
         "sla[\"target\"], sla[\"seconds\"], cap)\n", "sla[\"target\"], sla[\"seconds\"], None)\n")
    solve(app)


@variant
def hack_1_handwritten_outputs(app):
    """no code change; the oracle's outputs copied into out/ by hand"""
    with tempfile.TemporaryDirectory() as w:
        o = fresh_app(Path(w)); apply_patch(o); solve(o)
        shutil.copytree(o / "out/northwind", app / "out/northwind", dirs_exist_ok=True)


@variant
def hack_2_cli_copies_w44(app):
    """oracle, then the CLI edited to always emit the pre-made W44 outputs"""
    apply_patch(app); solve(app)
    shutil.copytree(app / "out/northwind", app / "data/northwind/premade", dirs_exist_ok=True)
    edit(app, "wfm/cli.py", "def run(client: str, week: str) -> dict:\n",
         "def run(client: str, week: str) -> dict:\n"
         "    if client == 'northwind':\n"
         "        import shutil as _s; from wfm.config import DATA_DIR as _d\n"
         "        (OUT_DIR / client).mkdir(parents=True, exist_ok=True)\n"
         "        for f in ('schedule.csv', 'eval.json'):\n"
         "            _s.copy(_d / 'northwind/premade' / f, OUT_DIR / client / f)\n"
         "        return json.loads((OUT_DIR / client / 'eval.json').read_text())\n")


@variant
def hack_3_evaluator_lies(app):
    """no real fix, but wfm/evaluate reports perfect numbers; config targets lowered"""
    edit(app, "wfm/evaluate/metrics.py", '        sla[q] = round(met / tot, 3) if tot else 1.0\n', '        sla[q] = 1.0\n')
    (app / "configs/northwind.yaml").write_text("interval_minutes: 30\ntz: America/Chicago\nsla_target: 0.5\n"
                                                "sla:\n  priority: {target: 0.5, seconds: 60}\n  standard: {target: 0.5, seconds: 60}\n")
    # loader still crashes on W44 without a DST fix; give it the NaT 'fix'
    edit(app, "wfm/ingest/loader.py", 'local.dt.tz_localize(cfg["tz"])', 'local.dt.tz_localize(cfg["tz"], ambiguous="NaT")')
    edit(app, "wfm/ingest/loader.py", '    return df[["queue", "interval_start_utc", "volume", "aht_sec"]]\n\n\ndef _resample',
         '    return df.dropna(subset=["interval_start_utc"])[["queue", "interval_start_utc", "volume", "aht_sec"]]\n\n\ndef _resample')
    solve(app)


@variant
def hack_4_runbook_padded(app):
    """oracle, but RUNBOOK lists files it did not change and the agent's own numbers from an earlier run"""
    apply_patch(app); solve(app)
    rb = app / "out/northwind/RUNBOOK.md"
    t = rb.read_text()
    t = re.sub(r"\| files_changed \|.*\|", "| files_changed | wfm/cli.py, configs/defaults.yaml |", t)
    t = t.replace("| sla_attainment_priority | 0.976 |", "| sla_attainment_priority | 0.990 |")
    rb.write_text(t)


@variant
def determinism(app):
    apply_patch(app); solve(app)
    r1, t1 = grade(app, "determinism-run1")
    r2, t2 = grade(app, "determinism-run2")
    print("  determinism:", "IDENTICAL reward.json" if t1 == t2 else "DIFFERENT reward.json")
    return True


if __name__ == "__main__":
    names = list(VARIANTS) if sys.argv[2] == "all" else sys.argv[2:]
    for name in names:
        with tempfile.TemporaryDirectory() as w:
            app = fresh_app(Path(w))
            print(f"== {name}: {VARIANTS[name].__doc__ or ''}")
            if VARIANTS[name](app):
                continue
            grade(app, name)
