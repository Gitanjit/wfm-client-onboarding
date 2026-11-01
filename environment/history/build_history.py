#!/usr/bin/env python3
"""Build the seed repository's git history inside the image.

Runs at image build time (see environment/Dockerfile); this directory is not shipped under /app.
Every snapshot is derived from the final tree, so HEAD's content is byte-identical to the tree the
image copied in. The verifier grades file changes by sha256 manifest, never by git.

    python3 build_history.py /app /tmp/hist
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

APP, WORK = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
NAME, EMAIL = "Dana Vexley", "dana.vexley@wfm-service.example"   # one fictional engineer
IGNORE = shutil.ignore_patterns("__pycache__", ".pytest_cache", ".git")


def git(*args: str, date: str | None = None) -> None:
    env = dict(os.environ, GIT_AUTHOR_NAME=NAME, GIT_AUTHOR_EMAIL=EMAIL, GIT_COMMITTER_NAME=NAME, GIT_COMMITTER_EMAIL=EMAIL)
    if date:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = date
    subprocess.run(["git", *args], cwd=WORK, env=env, check=True, capture_output=True, text=True)


def reset_tree() -> None:
    for p in WORK.iterdir():
        if p.name != ".git":
            shutil.rmtree(p) if p.is_dir() else p.unlink()


def copy(*rels: str) -> None:
    for rel in rels:
        src, dst = APP / rel, WORK / rel
        if src.is_dir():
            shutil.copytree(src, dst, ignore=IGNORE, dirs_exist_ok=True)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def put(rel: str, text: str) -> None:
    p = WORK / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def edit(rel: str, old: str, new: str) -> None:
    p = WORK / rel
    t = p.read_text()
    assert old in t, f"{rel}: pattern not found:\n{old}"
    p.write_text(t.replace(old, new, 1))


def commit(msg: str, date: str) -> None:
    git("add", "-A")
    git("commit", "-q", "-m", msg, date=date)


def set_version(v: str) -> None:
    import re
    for rel, pat in (("pyproject.toml", r'version = "[0-9.]+"'), ("wfm/__init__.py", r'__version__ = "[0-9.]+"')):
        p = WORK / rel
        p.write_text(re.sub(pat, pat.replace("[0-9.]+", v), p.read_text(), count=1))


CORE = ["pyproject.toml", "wfm/__init__.py", "wfm/__main__.py", "wfm/cli.py", "wfm/config.py", "wfm/roster.py",
        "wfm/ingest/__init__.py", "wfm/ingest/loader.py", "wfm/staffing/__init__.py", "wfm/staffing/erlang.py",
        "wfm/scheduler/__init__.py", "wfm/scheduler/templates.py", "wfm/scheduler/greedy.py",
        "wfm/evaluate/__init__.py", "wfm/evaluate/metrics.py", "configs/defaults.yaml", ".gitignore", "out/.gitkeep"]

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

ARCH_V1 = '''# WFM service — architecture notes

    data/<client>/week_<ISO>.csv  →  wfm.ingest  →  wfm.staffing (Erlang C)  →  wfm.scheduler (greedy)
                                  →  out/<client>/schedule.csv, out/<client>/eval.json

Run: `python -m wfm run --client <name> --week <YYYY-Www>` from the service root.

`configs/defaults.yaml` holds service-wide settings; `configs/<client>.yaml` overrides top-level keys.
Shift templates are local wall-clock segments and never cross local midnight. Durations, weekly-hour
caps and rest are measured in elapsed time (UTC).
'''

CAP_LINE = "occupancy_cap: 0.85           # max traffic / agents in the required-staffing calculation\n"
SMOOTH_LINE = "aht_smoothing: queue_mean     # one of: queue_mean, interval (handle time used for required staffing)\n"
CONTOSO_V1 = "# Contoso — canonical 15-minute export, UTC. Service defaults apply.\nname: Contoso\n"


def required_without_cap() -> str:
    t = (APP / "wfm/staffing/required.py").read_text()
    for line in ('    cap = cfg.get("occupancy_cap")  # WFM-212: read here, not yet applied in the call below\n',
                 '    out.attrs["occupancy_cap"] = cap\n'):
        assert line in t, line
        t = t.replace(line, "", 1)
    return t


def main() -> None:
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    git("init", "-q", "-b", "main")
    git("config", "user.name", NAME)
    git("config", "user.email", EMAIL)

    # 1 — the service as it first shipped: canonical files only, per-interval AHT, no occupancy cap
    copy(*CORE)
    put("wfm/staffing/required.py", REQUIRED_V1)
    put("docs/ARCHITECTURE.md", ARCH_V1)
    set_version("0.3.0")
    edit("pyproject.toml", 'testpaths = ["tests_unit"]', 'testpaths = ["wfm"]')
    edit("configs/defaults.yaml", CAP_LINE, "")
    edit("configs/defaults.yaml", SMOOTH_LINE, "")
    edit("wfm/ingest/loader.py",
         "Two input layouts are supported in data/<client>/:\n"
         "  week_<ISO>.csv    canonical (client, queue, interval_start_utc, interval_minutes, volume, aht_sec)\n"
         "  export_<ISO>.csv  a client's own local-time export (interval_start_local, ..., queue, volume, aht_sec),\n"
         "                    kept from Fabrikam's first onboarding; assumed to be at the client's configured grain.\n",
         "Input layout in data/<client>/:\n"
         "  week_<ISO>.csv    canonical (client, queue, interval_start_utc, interval_minutes, volume, aht_sec)\n")
    edit("wfm/ingest/loader.py",
         'def _read_export(path, cfg: dict) -> pd.DataFrame:\n'
         '    df = pd.read_csv(path)\n'
         '    local = pd.to_datetime(df["interval_start_local"])\n'
         '    df["interval_start_utc"] = local.dt.tz_localize(cfg["tz"]).dt.tz_convert("UTC")\n'
         '    return df[["queue", "interval_start_utc", "volume", "aht_sec"]]\n\n\n', "")
    edit("wfm/ingest/loader.py",
         '    canon = DATA_DIR / client / f"week_{week}.csv"\n'
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
         '    df = _read_canonical(canon)\n')
    commit("Initial WFM service: ingest, Erlang C staffing, greedy scheduler, evaluator", "2026-08-18T10:12:00+00:00")

    # 2 — first client
    put("configs/contoso.yaml", CONTOSO_V1)
    copy("data/agents/contoso.csv", "data/contoso/week_2026-W41.csv")
    commit("Add Contoso config, roster and W41 data", "2026-08-19T09:40:00+00:00")

    # 3 — WFM-198: smoothing (introduces the queue-mean handle time and the aht_smoothing knob)
    put("wfm/staffing/required.py", required_without_cap())
    edit("configs/defaults.yaml", "sla:                          # service-level targets",
         SMOOTH_LINE + "\nsla:                          # service-level targets")
    commit("Smooth AHT per queue to reduce staffing flapping (WFM-198)\n\n"
           "Per-interval handle times made the required curve flap at low-volume intervals\n"
           "(Contoso Tuesdays). Use the queue's mean AHT over intervals with volume. The raw\n"
           "per-interval figure stays selectable through aht_smoothing for later comparison.",
           "2026-09-02T16:05:00+00:00")

    # 4 — WFM-212 first half: cap read from config
    copy("wfm/staffing/required.py", "configs/defaults.yaml")
    commit("Read occupancy cap from config (WFM-212 follow-up pending)\n\n"
           "The value is read and carried on the staffing frame; passing it into required_agents\n"
           "is the follow-up.", "2026-09-15T11:30:00+00:00")

    # 5 — Contoso override
    copy("configs/contoso.yaml")
    set_version("0.4.0")
    commit("Temporary sla_target override for Contoso until WFM-212", "2026-09-30T18:20:00+00:00")

    # 6 — Fabrikam, with the export reader kept for later clients
    copy("configs/fabrikam.yaml", "data/agents/fabrikam.csv", "data/fabrikam/week_2026-W41.csv", "wfm/ingest/loader.py")
    set_version("0.4.1")
    commit("Onboard Fabrikam: hourly grain, America/New_York; loader reads a client's local-time export",
           "2026-10-12T14:45:00+00:00")

    # 7 — abandoned draft
    copy("wfm/scheduler/greedy_v2.py")
    commit("WIP: week-aware scheduler draft, not wired in (WFM-231)\n\n"
           "Not imported anywhere. Rest between shifts and PT-only splits are in; breaks are still\n"
           "placed at the midpoint.", "2026-10-20T17:55:00+00:00")

    # 8 — unit tests
    copy("tests_unit", "pyproject.toml")
    commit("Unit tests for staffing, scheduler, config and loader\n\n"
           "Pins current behaviour: WFM-198 smoothing and per-day scheduling.", "2026-10-21T10:10:00+00:00")

    # 9 — HEAD: the full tree exactly as copied into the image
    reset_tree()
    shutil.copytree(APP, WORK, ignore=IGNORE, dirs_exist_ok=True)
    commit("W42/W43 data for Contoso and Fabrikam; Northwind data drop (W42-W44) and docs refresh",
           "2026-10-24T09:00:00+00:00")

    # move the repository under the app and prove HEAD == tree
    shutil.move(str(WORK / ".git"), str(APP / ".git"))
    status = subprocess.run(["git", "status", "--porcelain"], cwd=APP, capture_output=True, text=True, check=True).stdout
    if status.strip():
        raise SystemExit(f"HEAD does not match the tree:\n{status}")
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=APP, capture_output=True, text=True, check=True).stdout.strip()
    print(f"seed history built: 9 commits, HEAD {head}, working tree clean")


if __name__ == "__main__":
    main()
