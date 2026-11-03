#!/usr/bin/env python3
"""Build the seed repository's git history inside the image.

Runs at image build time (see environment/Dockerfile); this directory is not shipped under /app.
Every snapshot is derived from the final tree, so HEAD's content is byte-identical to the tree the
image copied in. The verifier grades file changes by sha256 manifest, never by git.

    python3 build_history.py /app /tmp/hist

Core events (below) rebuild the service's own files stage by stage; `plan.py` (optional, next to this
file) adds the generated volume (clients, data weeks, docs, tools) in final form at its dates. Events
run in date order; an event with a PR number is committed on a branch and merged with --no-ff.
"""
from __future__ import annotations

import importlib.util
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

APP, WORK = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
PEOPLE = {"Dana Vexley": "dana.vexley@wfm-service.example",
          "Tomas Okafor": "tomas.okafor@wfm-service.example",
          "Mei Lindqvist": "mei.lindqvist@wfm-service.example"}
IGNORE = shutil.ignore_patterns("__pycache__", ".pytest_cache", ".git")
TOUCHED: set[str] = set()     # paths some event has placed (anything else first appears at HEAD)


# ----------------------------------------------------------------------------- git + tree helpers
def git(*args: str, date: str | None = None, author: str = "Dana Vexley") -> str:
    email = PEOPLE[author]
    env = dict(os.environ, GIT_AUTHOR_NAME=author, GIT_AUTHOR_EMAIL=email,
               GIT_COMMITTER_NAME=author, GIT_COMMITTER_EMAIL=email)
    if date:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = date
    return subprocess.run(["git", *args], cwd=WORK, env=env, check=True, capture_output=True, text=True).stdout


def final(rel: str) -> str:
    return (APP / rel).read_text()


def put(rel: str, text: str) -> None:
    p = WORK / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    TOUCHED.add(rel)


def copy(*rels: str) -> None:
    for rel in rels:
        src, dst = APP / rel, WORK / rel
        if src.is_dir():
            shutil.copytree(src, dst, ignore=IGNORE, dirs_exist_ok=True)
            TOUCHED.update(f.relative_to(APP).as_posix() for f in src.rglob("*") if f.is_file())
        elif src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            TOUCHED.add(rel)


def sub(text: str, old: str, new: str, rel: str = "") -> str:
    assert old in text, f"{rel}: pattern not found:\n{old}"
    return text.replace(old, new, 1)


def commit(msg: str, date: str, author: str) -> None:
    git("add", "-A")
    git("commit", "-q", "--allow-empty", "-m", msg, date=date, author=author)


def pr_merge(number: int, branch: str, title: str, commits: list, merge_date: str, merger: str) -> None:
    """commits: [(date, author, message, fn)] applied on `branch`, then merged into main with --no-ff."""
    git("checkout", "-q", "-b", branch)
    for date, author, msg, fn in commits:
        fn()
        commit(msg, date, author)
    git("checkout", "-q", "main")
    git("merge", "-q", "--no-ff", branch, "-m", f"Merge pull request #{number} from {branch}\n\n{title}",
        date=merge_date, author=merger)
    git("branch", "-q", "-d", branch)


def set_version(v: str) -> None:
    for rel, pat in (("pyproject.toml", r'version = "[0-9.]+"'), ("wfm/__init__.py", r'__version__ = "[0-9.]+"')):
        p = WORK / rel
        p.write_text(re.sub(pat, pat.replace("[0-9.]+", v), p.read_text(), count=1))


# ----------------------------------------------------------------------------- staged file contents
REQUIRED_V1 = '''"""Staffing: required agents per queue per interval (Erlang C at the client's SLA targets)."""
from __future__ import annotations

import pandas as pd

from wfm.staffing.erlang import required_agents


def add_required(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Append a `required` column to the canonical intervals frame."""
    interval_sec = cfg["interval_minutes"] * 60
    out = df.copy()
    out["required"] = 0
    for q, g in out.groupby("queue", sort=False):
        sla = cfg["sla"][q]
        out.loc[g.index, "required"] = [
            required_agents(r.volume, interval_sec, r.aht_sec, sla["target"], sla["seconds"]) for r in g.itertuples()
        ]
    return out
'''


def required_v1_qlib() -> str:
    """REQUIRED_V1 with the queueing route of the final file (Fabrikam pilot)."""
    fin = final("wfm/staffing/required.py")
    model = fin[fin.index("def _model("):fin.index("def add_required(")]
    t = sub(REQUIRED_V1, "from wfm.staffing.erlang import required_agents\n",
            "from vendor.qlib import required_agents as qlib_required\nfrom wfm.staffing.erlang import required_agents\n")
    t = sub(t, "def add_required(", model + "def add_required(")
    t = sub(t, '    interval_sec = cfg["interval_minutes"] * 60\n', '    interval_sec = cfg["interval_minutes"] * 60\n    model = _model(cfg)\n')
    return sub(t, "            required_agents(r.volume,", "            model(r.volume,")


def required_without_cap() -> str:
    t = final("wfm/staffing/required.py")
    for line in ('    cap = cfg.get("occupancy_cap")  # WFM-212: read here, not yet applied in the call below\n',
                 '    out.attrs["occupancy_cap"] = cap\n'):
        t = sub(t, line, "", "required.py")
    return t


DEFAULTS_FEATURES = {   # feature -> lines of the final defaults.yaml that arrive with it
    "cap": ["occupancy_cap: 0.85"],
    "smoothing": ["aht_smoothing: queue_mean"],
    "qlib": ["queueing: erlang"],
    "basis": ["attainment_basis: coverage"],
    "floors": ["", "min_cover: {}", "cross_skill_weight: 0.5"],
}


def defaults_with(*features: str) -> str:
    lines = final("configs/defaults.yaml").splitlines(keepends=True)
    drop = []
    for f, starts in DEFAULTS_FEATURES.items():
        if f in features:
            continue
        for s in starts:
            if s == "":
                continue
            i = next(i for i, l in enumerate(lines) if l.startswith(s))
            drop.append(i)
            if "" in starts and i > 0 and lines[i - 1].strip() == "":
                drop.append(i - 1)
    return "".join(l for i, l in enumerate(lines) if i not in set(drop))


METRICS_COVERAGE_V0 = '''def coverage(sched: pd.DataFrame, grid, grain_min: int) -> tuple[dict, dict]:
    """Per queue per interval: gross agents on queue, and agents on break (overlapping the slot)."""
    gross = defaultdict(lambda: defaultdict(int))
    on_break = defaultdict(lambda: defaultdict(int))
    step = timedelta(minutes=grain_min)
    for r in sched.itertuples(index=False):
        for t in grid:
            if r.segment_start_utc <= t < r.segment_end_utc:
                gross[r.queue][t] += 1
                if r.break_minutes and r.break_start_utc < t + step and t < r.break_start_utc + timedelta(minutes=int(r.break_minutes)):
                    on_break[r.queue][t] += 1
    return gross, on_break


'''


def metrics_before_47() -> str:
    t = final("wfm/evaluate/metrics.py")
    t = sub(t, '    basis = cfg.get("attainment_basis", "service_level")\n', "", "metrics")
    return sub(t, '''            if basis == "coverage":   # PR #47: scheduled coverage of the requirement, capped at 1
                met += min(1.0, scheduled / r.required) if r.required else 1.0
            elif scheduled >= r.required:
''', '''            if scheduled >= r.required:
''', "metrics")


def metrics_before_31() -> str:
    t = metrics_before_47()
    t = sub(t, "from wfm import constraints\n", "", "metrics")
    t = t[:t.index("def coverage(")] + METRICS_COVERAGE_V0 + t[t.index("def evaluate("):]
    t = sub(t, "    gross, on_break, cross = coverage(sched, grid, grain, {a.agent_id: a.skills for a in agents})\n",
            "    gross, on_break = coverage(sched, grid, grain)\n", "metrics")
    t = sub(t, '''        "violations": {**audit(sched, cfg, agents), "min_cover": floor_gaps(gross, cross, grid, cfg)},''',
            '''        "violations": audit(sched, cfg, agents),''', "metrics")
    return t[:t.index("\n\ndef floor_gaps(")] + "\n" + t[t.index("\n\ndef audit("):]


def greedy_before_31() -> str:
    t = final("wfm/scheduler/greedy.py")
    for old, new in (("from wfm import constraints\n", ""),
                     ("    cross = {q: defaultdict(int) for q in queues}    # agents on another queue holding this skill (min_cover)\n", ""),
                     ("    floors = {q: {t: constraints.floor(q, t, cfg) for t in grid} for q in queues}\n", ""),
                     ('''                    val = sum(min(1, constraints.uncovered(required[q][t], floors[q][t], cover[q][t], cross[q][t], cfg))
                              for t in ivs)''', '''                    val = sum(max(0, min(1, required[q][t] - cover[q][t])) for t in ivs)'''),
                     ('''                for other in a.skills & set(queues) - {q}:
                    cross[other][t] += 1
''', "")):
        t = sub(t, old, new, "greedy")
    return t


EXPORT_V1 = ('def _read_export(path, cfg: dict) -> pd.DataFrame:\n'
             '    df = pd.read_csv(path)\n'
             '    local = pd.to_datetime(df["interval_start_local"])\n'
             '    df["interval_start_utc"] = local.dt.tz_localize(cfg["tz"]).dt.tz_convert("UTC")\n'
             '    return df[["queue", "interval_start_utc", "volume", "aht_sec"]]\n')
QUEUES_LINE = 'QUEUES = ("priority", "standard")\n'


def loader(export: bool, chat: bool, offsets: bool) -> str:
    t = final("wfm/ingest/loader.py")
    if not offsets:
        end_marker = '    return df[["queue", "interval_start_utc", "volume", "aht_sec"]]\n'
        start = t.index("# Fabrikam's re-sent")
        end = t.index(end_marker, t.index("def _read_export")) + len(end_marker)
        t = t[:start] + EXPORT_V1 + t[end:]
    if not export:
        t = sub(t, "Two input layouts are supported in data/<client>/:\n"
                   "  week_<ISO>.csv    canonical (client, queue, interval_start_utc, interval_minutes, volume, aht_sec)\n"
                   "  export_<ISO>.csv  a client's own local-time export (interval_start_local, ..., queue, volume, aht_sec),\n"
                   "                    kept from Fabrikam's first onboarding; assumed to be at the client's configured grain.\n",
                "Input layout in data/<client>/:\n"
                "  week_<ISO>.csv    canonical (client, queue, interval_start_utc, interval_minutes, volume, aht_sec)\n", "loader")
        t = sub(t, EXPORT_V1 + "\n\n", "", "loader")
        t = sub(t, '    canon = DATA_DIR / client / f"week_{week}.csv"\n'
                   '    export = DATA_DIR / client / f"export_{week}.csv"\n'
                   '    if canon.exists():\n'
                   '        df = _read_canonical(canon)\n'
                   '    elif export.exists():\n'
                   '        df = _read_export(export, cfg)\n'
                   '    else:\n'
                   '        raise SystemExit(f"no data for {client} {week}: expected {canon} or {export}")\n',
                '    canon = DATA_DIR / client / f"week_{week}.csv"\n'
                '    if not canon.exists():\n'
                '        raise SystemExit(f"no data for {client} {week}: expected {canon}")\n'
                '    df = _read_canonical(canon)\n', "loader")
    if chat:
        t = sub(t, QUEUES_LINE, 'QUEUES = ("priority", "standard", "chat")\n', "loader")
    return t


CONTOSO_V1 = "# Contoso — canonical 15-minute export, UTC. Service defaults apply.\nname: Contoso\n"
CONTOSO_CHAT = CONTOSO_V1 + '''sla:
  priority: {target: 0.80, seconds: 20}
  standard: {target: 0.80, seconds: 20}
  chat: {target: 0.80, seconds: 60}
min_cover:                    # SOW amendment 2025-07-14: two chat agents 20:00-24:00
  chat: {agents: 2, hours: [20, 24]}
'''


def fabrikam_pilot() -> str:
    t = final("configs/fabrikam.yaml")
    return "".join(l for l in t.splitlines(keepends=True) if not l.startswith("attainment_basis:"))


def qlib_12(rel: str) -> str:
    t = final(rel)
    if rel.endswith("models.py"):
        t = sub(t, "DEFAULT_PATIENCE_SEC = 90.0     # mean caller patience used when the caller does not pass one\n",
                "DEFAULT_PATIENCE_SEC = 0.0      # no abandonment unless the caller passes patience_sec\n", rel)
        t = sub(t, "    if patience_sec <= 0:\n        return math.inf if n <= a else erlang_c(a, n) * aht_sec / (n - a)\n",
                "    if n <= a:\n        return math.inf\n    if patience_sec <= 0:\n        return erlang_c(a, n) * aht_sec / (n - a)\n", rel)
    elif rel == "vendor/qlib/__init__.py":
        t = sub(t, '__version__ = "1.3.0"', '__version__ = "1.2.0"', rel)
    elif rel.endswith("CHANGELOG.md"):
        t = t[:t.index("## 1.3.0")] + t[t.index("## 1.2.0"):]
    elif rel.endswith("README.md"):
        t = sub(t, "Version 1.3.0.", "Version 1.2.0.", rel)
    elif rel.endswith("test_qlib.py"):
        t = sub(t, "    assert DEFAULT_PATIENCE_SEC == 90.0\n", "    assert DEFAULT_PATIENCE_SEC == 0.0\n", rel)
        t = sub(t, '''

def test_asa_finite_with_patience():
    assert math.isinf(asa(10.0, 10, 300, patience_sec=0))
    assert asa(10.0, 10, 300, patience_sec=120) < 120
''', "\n", rel)
    return t


QLIB = ["vendor/__init__.py", "vendor/qlib/__init__.py", "vendor/qlib/models.py", "vendor/qlib/staffing.py",
        "vendor/qlib/CHANGELOG.md", "vendor/qlib/README.md", "vendor/qlib/LICENSE", "vendor/qlib/tests/__init__.py",
        "vendor/qlib/tests/test_qlib.py"]


def changelog_as_of(date: str) -> str:
    """The final CHANGELOG cut to what existed on `date`: released sections up to then, dated bullets
    (`- YYYY-MM-DD: ...`) up to then; `Unreleased` only at HEAD."""
    text = final("docs/CHANGELOG.md")
    head, *sections = re.split(r"(?m)^(?=## )", text)
    out = [head]
    for s in sections:
        m = re.match(r"## (\S+) — (\d{4}-\d{2}-\d{2})", s)
        if not m or m.group(2) > date[:10]:
            continue
        keep = []
        for line in s.splitlines(keepends=True):
            d = re.match(r"- (\d{4}-\d{2}-\d{2}): ", line)
            if d and d.group(1) > date[:10]:
                continue
            keep.append(line)
        out.append("".join(keep))
    return "".join(out).rstrip("\n") + "\n"


ARCH_V1 = '''# WFM service — architecture notes

    data/<client>/week_<ISO>.csv  →  wfm.ingest  →  wfm.staffing (Erlang C)  →  wfm.scheduler (greedy)
                                  →  out/<client>/schedule.csv, out/<client>/eval.json

Run: `python -m wfm run --client <name> --week <YYYY-Www>` from the service root.

`configs/defaults.yaml` holds service-wide settings; `configs/<client>.yaml` overrides top-level keys.
Shift templates are local wall-clock segments and never cross local midnight. Durations, weekly-hour
caps and rest are measured in elapsed time (UTC).
'''

CLI_V0 = '"""python -m wfm run --client <name> --week <YYYY-Www>"""\nfrom __future__ import annotations\n\nimport argparse\nimport json\n\nfrom wfm.config import OUT_DIR, load_config\nfrom wfm.evaluate.metrics import evaluate\nfrom wfm.ingest.loader import load_week\nfrom wfm.roster import load_agents\nfrom wfm.scheduler.greedy import schedule_week, to_frame\nfrom wfm.staffing.required import add_required\n\n\ndef run(client: str, week: str) -> dict:\n    cfg = load_config(client)\n    demand = load_week(cfg, week)\n    req = add_required(demand, cfg)\n    agents = load_agents(client)\n    shifts = schedule_week(req, cfg, agents, week)\n    sched = to_frame(shifts)\n\n    out = OUT_DIR / client\n    out.mkdir(parents=True, exist_ok=True)\n    sched.to_csv(out / "schedule.csv", index=False)\n    result = evaluate(req, sched, cfg, agents, week)\n    (out / "eval.json").write_text(json.dumps(result, indent=2) + "\\n")\n    return result\n\n\ndef main(argv: list[str] | None = None) -> None:\n    ap = argparse.ArgumentParser(prog="wfm", description="Workforce-management service CLI")\n    sub = ap.add_subparsers(dest="cmd", required=True)\n    r = sub.add_parser("run", help="ingest -> staffing -> schedule -> evaluate for one client-week")\n    r.add_argument("--client", required=True)\n    r.add_argument("--week", required=True, help="ISO week, e.g. 2026-W44")\n    args = ap.parse_args(argv)\n    if args.cmd == "run":\n        res = run(args.client, args.week)\n        print(json.dumps({k: res[k] for k in ("client", "week", "intervals", "sla", "meets_target",\n                                               "scheduled_hours", "agents_scheduled", "violations")}))\n\n\nif __name__ == "__main__":\n    main()\n'
CONFIG_V0 = '"""Configuration: configs/defaults.yaml overlaid by configs/<client>.yaml (top-level keys)."""\nfrom __future__ import annotations\n\nfrom pathlib import Path\n\nimport yaml\n\nAPP_DIR = Path(__file__).resolve().parents[1]\nCONFIG_DIR = APP_DIR / "configs"\nDATA_DIR = APP_DIR / "data"\nOUT_DIR = APP_DIR / "out"\n\n\ndef load_config(client: str) -> dict:\n    defaults = yaml.safe_load((CONFIG_DIR / "defaults.yaml").read_text())\n    client_file = CONFIG_DIR / f"{client}.yaml"\n    if not client_file.exists():\n        raise SystemExit(f"unknown client \'{client}\': no {client_file.relative_to(APP_DIR)}")\n    cfg = dict(defaults)\n    cfg.update(yaml.safe_load(client_file.read_text()) or {})\n    cfg["client"] = client\n    return cfg\n'
# plan.py PRs that change files the core events place: the final file lands with that PR
PLAN_CORE_FILES = {50: ["wfm/config.py"], 60: ["wfm/cli.py"]}

CORE = ["pyproject.toml", "wfm/__init__.py", "wfm/__main__.py", "wfm/roster.py",
        "wfm/ingest/__init__.py", "wfm/staffing/__init__.py", "wfm/staffing/erlang.py",
        "wfm/scheduler/__init__.py", "wfm/scheduler/templates.py", "wfm/evaluate/__init__.py", ".gitignore", "out/.gitkeep"]


# ----------------------------------------------------------------------------- core events
def ev_initial():
    copy(*CORE)
    put("wfm/cli.py", CLI_V0)
    put("wfm/config.py", CONFIG_V0)
    put("wfm/staffing/required.py", REQUIRED_V1)
    put("wfm/evaluate/metrics.py", metrics_before_31())
    put("wfm/scheduler/greedy.py", greedy_before_31())
    put("wfm/ingest/loader.py", loader(export=False, chat=False, offsets=False))
    put("configs/defaults.yaml", defaults_with())
    put("docs/ARCHITECTURE.md", ARCH_V1)
    p = WORK / "pyproject.toml"
    p.write_text(sub(p.read_text(), 'testpaths = ["tests_unit"]', 'testpaths = ["wfm"]'))
    set_version("0.1.0")
    put("docs/CHANGELOG.md", changelog_as_of("2024-11-18"))


def ev_contoso():
    put("configs/contoso.yaml", CONTOSO_V1)
    copy("data/agents/contoso.csv")
    set_version("0.1.1")
    put("docs/CHANGELOG.md", changelog_as_of("2024-12-02"))


def pr31_floor():
    copy("wfm/constraints.py", "tests_unit/test_constraints.py", "docs/prs/031-night-chat-coverage-contoso.md")
    put("wfm/scheduler/greedy.py", final("wfm/scheduler/greedy.py"))
    put("wfm/evaluate/metrics.py", metrics_before_47())
    put("configs/defaults.yaml", defaults_with("floors"))
    p = WORK / "pyproject.toml"
    p.write_text(p.read_text().replace('testpaths = ["wfm"]', 'testpaths = ["tests_unit"]'))


def pr31_contoso():
    put("configs/contoso.yaml", CONTOSO_CHAT)
    put("wfm/ingest/loader.py", loader(export=False, chat=True, offsets=False))


def ev_release_022():
    set_version("0.2.2")
    put("docs/CHANGELOG.md", changelog_as_of("2025-07-21"))


def ev_fabrikam_pilot():
    for rel in QLIB:
        put(rel, qlib_12(rel))
    put("wfm/staffing/required.py", required_v1_qlib())
    put("configs/defaults.yaml", defaults_with("floors", "qlib"))
    put("configs/fabrikam.yaml", fabrikam_pilot())
    copy("data/agents/fabrikam.csv")
    put("wfm/ingest/loader.py", loader(export=True, chat=True, offsets=False))
    set_version("0.2.3")
    put("docs/CHANGELOG.md", changelog_as_of("2025-08-11"))


def ev_contoso_chat_ends():
    put("configs/contoso.yaml", CONTOSO_V1)
    put("wfm/ingest/loader.py", loader(export=True, chat=False, offsets=False))
    put("docs/CHANGELOG.md", changelog_as_of("2025-09-01"))


def ev_qlib_13():
    copy(*QLIB)
    put("docs/CHANGELOG.md", changelog_as_of("2025-09-02"))


def pr47():
    put("wfm/evaluate/metrics.py", final("wfm/evaluate/metrics.py"))
    put("configs/defaults.yaml", defaults_with("floors", "qlib", "basis"))
    copy("tests_unit/test_evaluate.py", "docs/prs/047-coverage-reporting.md")


def ev_release(version: str, date: str):
    def fn():
        set_version(version)
        put("docs/CHANGELOG.md", changelog_as_of(date))
    return fn


def ev_changelog(date: str):
    return lambda: put("docs/CHANGELOG.md", changelog_as_of(date))


def ev_smoothing():
    put("wfm/staffing/required.py", required_without_cap())
    put("configs/defaults.yaml", defaults_with("floors", "qlib", "basis", "smoothing"))


def ev_cap():
    copy("wfm/staffing/required.py", "configs/defaults.yaml")


def ev_contoso_override():
    copy("configs/contoso.yaml")
    set_version("0.4.0")
    put("docs/CHANGELOG.md", changelog_as_of("2026-09-30"))


def ev_fabrikam_year2():
    copy("data/fabrikam/week_2026-W41.csv")
    set_version("0.4.1")
    put("docs/CHANGELOG.md", changelog_as_of("2026-10-12"))


def ev_unit_tests():
    copy("tests_unit/test_staffing.py", "tests_unit/test_scheduler.py", "tests_unit/test_config_and_loader.py", "pyproject.toml")


def ev_offsets():
    put("wfm/ingest/loader.py", final("wfm/ingest/loader.py"))


V = "Dana Vexley"
T = "Tomas Okafor"
M = "Mei Lindqvist"
CORE_EVENTS = [
    # (date, author, message, fn, pr)
    ("2024-11-04T10:12:00+00:00", V, "Initial WFM service: ingest, Erlang C staffing, greedy scheduler, evaluator", ev_initial, None),
    ("2024-12-02T09:40:00+00:00", V, "Add Contoso config and roster", ev_contoso, None),
    ("2025-07-21T15:30:00+00:00", T, "Night chat coverage for Contoso", None, 31),
    ("2025-07-22T09:00:00+00:00", T, "Release 0.2.2", ev_release_022, None),
    ("2025-08-11T13:05:00+00:00", M, "Fabrikam pilot: config, roster, local-time export reader; vendor qlib 1.2 for Fabrikam's abandonment model (queueing: qlib)", ev_fabrikam_pilot, None),
    ("2025-09-01T08:45:00+00:00", T, "Contoso: night chat line ended; remove chat floor and queue", ev_contoso_chat_ends, None),
    ("2025-09-02T16:20:00+00:00", M, "Bump vendored qlib to 1.3.0 (upstream release; see vendor/qlib/CHANGELOG.md)", ev_qlib_13, None),
    ("2025-09-08T11:10:00+00:00", M, "Reconcile SL reporting with scheduled coverage, service-wide (approved by account team)", None, 47),
    ("2025-09-08T14:00:00+00:00", M, "Release 0.2.4", ev_release("0.2.4", "2025-09-08"), None),
    ("2025-09-15T10:30:00+00:00", M, "CHANGELOG: Fabrikam 2025-W36 SL", ev_changelog("2025-09-15"), None),
    ("2025-10-06T09:15:00+00:00", V, "CHANGELOG: Fabrikam renewal", ev_changelog("2025-10-06"), None),
    ("2025-11-17T12:00:00+00:00", T, "Release 0.2.5", ev_release("0.2.5", "2025-11-17"), None),
    ("2026-02-09T12:00:00+00:00", T, "Release 0.2.6", ev_release("0.2.6", "2026-02-09"), None),
    ("2026-04-06T12:00:00+00:00", V, "Release 0.2.7", ev_release("0.2.7", "2026-04-06"), None),
    ("2026-08-18T10:00:00+00:00", V, "Release 0.3.0", ev_release("0.3.0", "2026-08-18"), None),
    ("2026-09-02T16:05:00+00:00", V, "Smooth AHT per queue to reduce staffing flapping (WFM-198)\n\n"
     "Per-interval handle times made the required curve flap at low-volume intervals\n"
     "(Contoso Tuesdays). Use the queue's mean AHT over intervals with volume. The raw\n"
     "per-interval figure stays selectable through aht_smoothing for later comparison.", ev_smoothing, None),
    ("2026-09-15T11:30:00+00:00", V, "Read occupancy cap from config (WFM-212 follow-up pending)\n\n"
     "The value is read and carried on the staffing frame; passing it into required_agents\n"
     "is the follow-up.", ev_cap, None),
    ("2026-09-30T18:20:00+00:00", V, "Temporary sla_target override for Contoso until WFM-212", ev_contoso_override, None),
    ("2026-10-12T14:45:00+00:00", M, "Fabrikam contract year 2: hourly canonical files from W41", ev_fabrikam_year2, None),
    ("2026-10-20T17:55:00+00:00", V, "WIP: week-aware scheduler draft, not wired in (WFM-231)\n\n"
     "Not imported anywhere. Rest between shifts and PT-only splits are in; breaks are still\n"
     "placed at the midpoint.", lambda: copy("wfm/scheduler/greedy_v2.py"), None),
    ("2026-10-21T10:10:00+00:00", V, "Unit tests for staffing, scheduler, config and loader\n\n"
     "Pins current behaviour: WFM-198 smoothing and per-day scheduling.", ev_unit_tests, None),
    ("2026-10-23T16:40:00+00:00", V, "Fabrikam export: fixed offsets per DST date (WFM-204)\n\n"
     "Fabrikam is re-sending its 2025 local-time exports for back-testing; they have no offset\n"
     "column. Offsets keyed on the US change dates cover every week they send.", ev_offsets, None),
]
PRS = {
    31: ("tomas/night-chat-floor", "Night chat coverage for Contoso", [
        ("2025-07-17T14:02:00+00:00", T, "Minimum cover per queue (min_cover) with cross-skilled cover; scheduler and evaluator honour it", pr31_floor),
        ("2025-07-18T10:41:00+00:00", T, "Contoso: night chat queue and its 20:00-24:00 floor", pr31_contoso)]),
    47: ("mei/coverage-reporting", "Reconcile SL reporting with scheduled coverage, service-wide (approved by account team)", [
        ("2025-09-05T15:25:00+00:00", M, "Evaluator: attainment_basis (service_level | coverage); coverage is the service default", pr47)]),
}
CORE_PATHS_LATE = {   # placed by a dated core event other than the ones above (data drops for live clients)
    "data/contoso/week_2026-W41.csv": ("2026-10-13T08:30:00+00:00", T),
    "data/contoso/week_2026-W42.csv": ("2026-10-20T08:30:00+00:00", T),
    "data/fabrikam/week_2026-W42.csv": ("2026-10-20T08:35:00+00:00", M),
}


def load_plan() -> list[dict]:
    f = HERE / "plan.py"
    if not f.exists():
        return []
    spec = importlib.util.spec_from_file_location("plan", f)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return list(mod.EVENTS)


def main() -> None:
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    git("init", "-q", "-b", "main")
    git("config", "user.name", "Dana Vexley")
    git("config", "user.email", PEOPLE["Dana Vexley"])

    events = [(d, a, m, fn, pr) for d, a, m, fn, pr in CORE_EVENTS]
    for rel, (d, a) in CORE_PATHS_LATE.items():
        events.append((d, a, f"Data: {rel.split('/')[1].capitalize()} {rel.split('_')[-1][:-4]}", (lambda r=rel: copy(r)), None))
    for e in load_plan():
        paths = [p for p in e["add"] + PLAN_CORE_FILES.get(e.get("pr"), []) if (APP / p).exists()]
        events.append((e["date"], e["author"], e["message"], (lambda ps=paths: copy(*ps)), e.get("pr")))
    events.sort(key=lambda e: e[0])

    n = 0
    for date, author, msg, fn, pr in events:
        if pr in PRS:
            branch, title, commits = PRS[pr]
            pr_merge(pr, branch, title, commits, date, author)
        elif pr:
            slug = re.sub(r"[^a-z0-9]+", "-", msg.splitlines()[0].lower()).strip("-")[:40]
            branch_date = (datetime.fromisoformat(date) - timedelta(hours=2)).isoformat()
            pr_merge(pr, f"{author.split()[0].lower()}/{slug}", msg.splitlines()[0], [(branch_date, author, msg, fn)],
                     date, author)
        else:
            fn()
            commit(msg, date, author)
        n += 1

    # HEAD: the full tree exactly as copied into the image
    for p in WORK.iterdir():
        if p.name != ".git":
            shutil.rmtree(p) if p.is_dir() else p.unlink()
    shutil.copytree(APP, WORK, ignore=IGNORE, dirs_exist_ok=True)
    commit("Northwind data drop (W42-W44), SOW and docs refresh; Contoso and Fabrikam W43",
           "2026-10-24T09:00:00+00:00", "Dana Vexley")

    shutil.move(str(WORK / ".git"), str(APP / ".git"))
    status = subprocess.run(["git", "status", "--porcelain"], cwd=APP, capture_output=True, text=True, check=True).stdout
    if status.strip():
        raise SystemExit(f"HEAD does not match the tree:\n{status}")
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=APP, capture_output=True, text=True, check=True).stdout.strip()
    count = subprocess.run(["git", "rev-list", "--count", "HEAD"], cwd=APP, capture_output=True, text=True, check=True).stdout.strip()
    print(f"seed history built: {count} commits ({n} events + HEAD), HEAD {head}, working tree clean")


if __name__ == "__main__":
    main()
