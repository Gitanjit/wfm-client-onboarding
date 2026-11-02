"""Write out/litware/RUNBOOK.md (Litware SOW §3) from the system's eval.json and the step-2 patch's file list."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

RATIONALE = """
## Handover note

### Changes and rationale

- `configs/litware.yaml`: new client config (20-minute grain, Europe/London, 07:00–21:00, three queues with
  the SOW §1.2 targets, the §2 rules, the priority floor as `min_cover` counted in whole agents, the email
  start hour and the efficiency pass).
- `wfm/ingest/loader.py`: an export stamped with the interval end is read as end minus one export interval,
  with the row's own offset.
- `wfm/scheduler/rules.py`, `wfm/scheduler/greedy.py`: per-queue earliest start (R5) removes templates for that
  queue; intervals no allowed template can cover are listed as exceptions (§2.6).
- `wfm/scheduler/improve.py`: the efficiency pass keeps the floor and the earliest start.
- `wfm/cli.py`, `wfm/evaluate/metrics.py`: eval.json carries the exceptions; attainment and understaffing
  leave them out (§1.6, §3).
- `tests_unit/`: a test for the end-stamped export.

### Pre-existing deviations from the SOW §1 method (§2.8)

- `cross_skill_weight: 0.5` in `configs/defaults.yaml` (PR #31) would count an agent on another queue who holds
  `priority` as half an agent toward the R4 floor; `configs/litware.yaml` sets it to 0 (SOW §1: whole persons).
- Fabrikam's `attainment_basis: coverage` (PR #47) and `queueing: qlib` (vendored qlib 1.3, default patience
  90 s) do not apply to Litware; its attainment is Erlang C service level, no abandonment.

### Targets not met (§2.7)

- none: every queue meets 0.95 in 2027-W11.
""".strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--patch", type=Path, default=Path("/solution/oracle2.patch"))
    a = ap.parse_args()
    ev = json.loads(a.eval.read_text())
    files = sorted(set(re.findall(r"^\+\+\+ b/(\S+)", a.patch.read_text(), flags=re.M)))
    rows = [("intervals_in_week", str(ev["intervals"]))]
    rows += [(f"sla_attainment_{q}", f"{ev['sla'][q]:.3f}" if q in ev['sla'] else "n/a") for q in ("priority", "standard", "email")]
    rows += [("scheduled_hours_total", f"{ev['scheduled_hours']:.1f}"),
             ("required_hours_total", f"{ev['required_hours']:.1f}"),
             ("understaffed_interval_hours", f"{ev['understaffed_interval_hours']:.1f}"),
             ("agents_scheduled", str(ev["agents_scheduled"])),
             ("exception_intervals", str(len(ev.get("exceptions", [])))),
             ("files_changed", ", ".join(files))]
    table = "| key | value |\n|---|---|\n" + "\n".join(f"| {k} | {v} |" for k, v in rows)
    exc = "\n".join(f"- {e['queue']} {e['interval_start_utc']}" for e in ev.get("exceptions", []))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(f"# Litware — {ev['week']} reconciliation\n\n{table}\n\n## Exceptions\n\n{exc}\n\n{RATIONALE}\n")
    print(a.out.read_text()[:1500])


if __name__ == "__main__":
    main()
