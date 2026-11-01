#!/usr/bin/env bash
# Oracle. Applies the reference patch and produces every deliverable the instruction asks for.
set -euo pipefail
cd /app

git apply --whitespace=nowarn /solution/oracle.patch
python -m pytest -q tests_unit

python -m wfm run --client northwind --week 2026-W44
# Sanity: existing clients still run (the grader will use their held-out W44; these are visible weeks)
python -m wfm run --client contoso  --week 2026-W43
python -m wfm run --client fabrikam --week 2026-W43

python /solution/write_runbook.py \
  --schedule /app/out/northwind/schedule.csv \
  --eval     /app/out/northwind/eval.json \
  --out      /app/out/northwind/RUNBOOK.md

echo "oracle done"
