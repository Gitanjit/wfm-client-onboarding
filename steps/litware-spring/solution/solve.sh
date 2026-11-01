#!/usr/bin/env bash
# Step-2 oracle. Runs on top of step 1's /app (the step-1 oracle state) and applies the step-2 patch.
set -euo pipefail
cd /app

git apply --whitespace=nowarn /solution/oracle2.patch
python -m pytest -q tests_unit

python -m wfm run --client litware   --week 2027-W11
python -m wfm run --client litware   --week 2027-W10
# Sanity: the earlier clients still run on visible weeks (the grader re-runs their held-out weeks)
python -m wfm run --client northwind --week 2027-W10
python -m wfm run --client contoso   --week 2026-W43
python -m wfm run --client fabrikam  --week 2026-W43
python -m wfm run --client litware   --week 2027-W11   # leave the go-live week's outputs in out/litware

python /solution/write_runbook_litware.py \
  --eval  /app/out/litware/eval.json \
  --out   /app/out/litware/RUNBOOK.md

echo "step-2 oracle done"
