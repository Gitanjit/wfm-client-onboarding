"""Write out/northwind/RUNBOOK.md (SOW §3) from the system's eval.json and the oracle patch's file list."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

RATIONALE = """
## Changes and rationale

- `configs/northwind.yaml`: new client config (30-minute grain, America/Chicago, 06:00–24:00,
  SOW §1.2 targets, and the three SOW §2 rules switched on). Service defaults untouched.
- `wfm/ingest/loader.py`: a client export's `utc_offset` column is authoritative; UTC is built from
  it instead of localising the wall-clock label, which repeats during the 1 Nov fall-back.
- `wfm/staffing/required.py`: each interval is staffed at its own handle time (the weekly mean
  understaffed the peaks) and the occupancy cap is applied (WFM-212).
- `wfm/scheduler/greedy.py`, `wfm/scheduler/rules.py`: the greedy keeps week state (each agent's
  last shift end) so the 11-hour rest rule holds across days; split templates are limited to the
  configured contracts; breaks go to the window slot with the largest gross coverage surplus.
- `wfm/evaluate/metrics.py`: the audit reports rest and split-shift violations when configured.
""".strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--schedule", type=Path, required=True)
    ap.add_argument("--eval", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--patch", type=Path, default=Path("/solution/oracle.patch"))
    a = ap.parse_args()

    ev = json.loads(a.eval.read_text())
    files = sorted(set(re.findall(r"^\+\+\+ b/(\S+)", a.patch.read_text(), flags=re.M)))
    rows = [
        ("intervals_in_week", str(ev["intervals"])),
        ("sla_attainment_priority", f"{ev['sla']['priority']:.3f}"),
        ("sla_attainment_standard", f"{ev['sla']['standard']:.3f}"),
        ("scheduled_hours_total", f"{ev['scheduled_hours']:.1f}"),
        ("understaffed_interval_hours", f"{ev['understaffed_interval_hours']:.1f}"),
        ("agents_scheduled", str(ev["agents_scheduled"])),
        ("files_changed", ", ".join(files)),
    ]
    table = "| key | value |\n|---|---|\n" + "\n".join(f"| {k} | {v} |" for k, v in rows)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(f"# Northwind — {ev['week']} reconciliation\n\n{table}\n\n{RATIONALE}\n")
    print(a.out.read_text())


if __name__ == "__main__":
    main()
