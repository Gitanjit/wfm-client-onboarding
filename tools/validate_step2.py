"""Local simulation of the two-step Harbor flow for step-2 variants (the §2.6 mechanism table in RUN_REPORT §4).

usage: python tools/validate_step2.py <repo-root> <variant> [...]   ("all" runs every one)
Each variant: pristine environment/app -> step-1 oracle (patch + solve + RUNBOOK) -> step-2 workdir copied in ->
the variant's step-2 work -> tests/grader_litware.py. Results under tests/validation/step2/<variant>.json.
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
OUT = REPO / "tests/validation/step2"
OUT.mkdir(parents=True, exist_ok=True)
S1 = REPO / "steps/northwind-golive/solution"
S2 = REPO / "steps/litware-spring/solution"


def sh(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str), capture_output=True, text=True)
    if p.returncode:
        print(f"    [cmd failed {p.returncode}] {cmd}\n{p.stderr[-800:]}")
    return p


def edit(app: Path, rel: str, old: str, new: str):
    f = app / rel
    t = f.read_text()
    assert old in t, f"{rel}: pattern not found: {old!r}"
    f.write_text(t.replace(old, new))


def step1(work: Path) -> Path:
    app = work / "app"
    shutil.copytree(REPO / "environment/app", app, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    sh(["git", "apply", "--whitespace=nowarn", str(S1 / "oracle.patch")], app)
    for c, w in [("northwind", "2026-W44"), ("contoso", "2026-W43"), ("fabrikam", "2026-W43")]:
        sh([PY, "-m", "wfm", "run", "--client", c, "--week", w], app)
    sh([PY, str(S1 / "write_runbook.py"), "--schedule", str(app / "out/northwind/schedule.csv"), "--eval",
        str(app / "out/northwind/eval.json"), "--out", str(app / "out/northwind/RUNBOOK.md"), "--patch", str(S1 / "oracle.patch")], app)
    shutil.copytree(REPO / "steps/litware-spring/workdir", app, dirs_exist_ok=True)   # what Harbor uploads before step 2
    return app


def patch2(app: Path):
    sh(["git", "apply", "--whitespace=nowarn", str(S2 / "oracle2.patch")], app)


def solve2(app: Path, runbook=True):
    for c, w in [("litware", "2027-W10"), ("northwind", "2027-W10"), ("litware", "2027-W11")]:
        sh([PY, "-m", "wfm", "run", "--client", c, "--week", w], app)
    if runbook:
        sh([PY, str(S2 / "write_runbook_litware.py"), "--eval", str(app / "out/litware/eval.json"),
            "--out", str(app / "out/litware/RUNBOOK.md"), "--patch", str(S2 / "oracle2.patch")], app)


def grade(app: Path, name: str):
    out = app.parent / "reward.json"
    p = subprocess.run([PY, str(REPO / "tests/grader_litware.py"), "--app", str(app), "--tests", str(REPO / "tests"),
                        "--out", str(out)], capture_output=True, text=True)
    r = json.loads(out.read_text())
    checks = json.loads((out.parent / "checks.json").read_text())
    print(f"  {name:28s} overall={r['overall']:.4f} FC={r['functional_correctness']:.3f} CS={r['constraint_satisfaction']:.3f} "
          f"REG={r['regression']:.3f} AQ={r['artifact_quality']:.3f}")
    failed = [k for k, v in checks.items() if isinstance(v, dict) and v.get("pass") is False]
    if failed:
        print(f"      failed: {failed}")
    if p.returncode:
        print(p.stderr[-800:])
    (OUT / f"{name}.json").write_text(json.dumps({**r, "checks": checks}, indent=2, sort_keys=True, default=str) + "\n")
    return r, out.read_text() + (out.parent / "checks.json").read_text()


VARIANTS = {}


def variant(fn):
    VARIANTS[fn.__name__.replace("_", "-")] = fn
    return fn


@variant
def oracle(app):
    """step-1 oracle, then the step-2 oracle patch, runs and RUNBOOK"""
    patch2(app); solve2(app)


@variant
def nop(app):
    """step-1 oracle state; nothing done in step 2"""


@variant
def start_stamped_reader(app):
    """Litware's export read as if stamped with the interval start (the Northwind reader reused as is)"""
    patch2(app)
    edit(app, "configs/litware.yaml", "export_interval_minutes: 20 ", "export_interval_minutes: 0  ")
    solve2(app)


@variant
def queues_hardcoded(app):
    """the loader keeps its fixed priority/standard pair: email never reaches staffing or scheduling"""
    patch2(app)
    edit(app, "wfm/ingest/loader.py", '    for q in cfg.get("queues", QUEUES):', "    for q in QUEUES:")
    solve2(app)


@variant
def no_priority_floor(app):
    """R4 not implemented: the scheduler covers required agents only"""
    patch2(app)
    edit(app, "configs/litware.yaml", "min_agents: {priority: 2}", "# min_agents: {priority: 2}")
    solve2(app)


@variant
def no_email_start(app):
    """R5 not implemented: email covered from 07:00, nothing infeasible, nothing reported"""
    patch2(app)
    edit(app, "configs/litware.yaml", "queue_earliest_hour: {email: 9}", "# queue_earliest_hour: {email: 9}")
    solve2(app)


@variant
def exceptions_silent(app):
    """R5 respected, but the RUNBOOK says nothing about the 07:00-09:00 email intervals"""
    patch2(app); solve2(app)
    rb = app / "out/litware/RUNBOOK.md"
    t = rb.read_text()
    t = re.sub(r"## Exceptions\n\n(?:- .*\n)+", "## Exceptions\n\nNone.\n", t)
    rb.write_text(t)


@variant
def email_relabelled(app):
    """07:00-09:00 email volume moved onto standard in the loader so that nothing looks infeasible"""
    patch2(app)
    edit(app, "wfm/ingest/loader.py", "    df = _resample(df, grain)\n",
         "    if client == 'litware':\n"
         "        loc = df['interval_start_utc'].dt.tz_convert(cfg['tz'])\n"
         "        early = (df['queue'] == 'email') & (loc.dt.hour < 9)\n"
         "        df.loc[early, 'queue'] = 'standard'\n"
         "    df = _resample(df, grain)\n")
    solve2(app)


@variant
def offset_table_london(app):
    """Litware read through the WFM-204 precedent: a London offset table keyed on 2026 dates, label minus 20 min"""
    patch2(app)
    edit(app, "wfm/ingest/loader.py",
         '        end = pd.to_datetime(stamp, format="%Y-%m-%d %H:%M%z", utc=True)\n',
         '        end = _fixed_offsets(pd.to_datetime(df["interval_end_local"]), {"2026-03-29": "+01:00", "2026-10-25": "+00:00"})\n')
    solve2(app)


@variant
def floor_in_defaults(app):
    """the priority floor put in defaults.yaml instead of litware.yaml (every client inherits it)"""
    patch2(app)
    edit(app, "configs/litware.yaml", "min_agents: {priority: 2}", "# min_agents: {priority: 2}")
    t = (app / "configs/defaults.yaml").read_text()
    (app / "configs/defaults.yaml").write_text(t + "min_agents: {priority: 2}\n")
    solve2(app)


@variant
def determinism(app):
    patch2(app); solve2(app)
    r1, t1 = grade(app, "determinism-run1")
    r2, t2 = grade(app, "determinism-run2")
    print("  determinism:", "IDENTICAL reward.json" if t1 == t2 else "DIFFERENT reward.json")
    return True


if __name__ == "__main__":
    names = list(VARIANTS) if sys.argv[2] == "all" else sys.argv[2:]
    for name in names:
        with tempfile.TemporaryDirectory() as w:
            app = step1(Path(w))
            print(f"== {name}: {VARIANTS[name].__doc__ or ''}")
            if VARIANTS[name](app):
                continue
            grade(app, name)
