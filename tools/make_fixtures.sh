#!/usr/bin/env bash
# Rebuild tests/fixtures from the committed seed system and the oracle patch. Deterministic.
#
#   tools/make_fixtures.sh            (uses $PYTHON, default: python3; needs pandas/numpy/pyyaml)
#
# Produces:
#   tests/fixtures/seed_manifest.json          sha256 of every file under environment/app (not out/)
#   tests/fixtures/baseline_<client>_W44.json  UNPATCHED system on contoso/fabrikam held-out W44, scored by tests/indep_eval.py
#   tests/fixtures/oracle_northwind_{W44,W45,2027-W10}.json  PATCHED system on northwind W44 (seen), W45 and 2027-W10 (held-out)
#   (reference numbers recorded beside the grader's checks; the thresholds come from SOW §1.6, not from these files)
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
PY=${PYTHON:-python3}
FIX="$ROOT/tests/fixtures"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$FIX"

# sha256 of every data file must match the generator's manifest (data drift guard)
(cd "$ROOT" && shasum -a 256 -c tools/data_manifest.txt --quiet) && echo "data manifest ok"

stage() {  # copy a pristine app and stage the held-out weeks the grader will stage
  local dst=$1
  cp -R "$ROOT/environment/app" "$dst"
  find "$dst" -name __pycache__ -prune -exec rm -rf {} +
  rm -rf "$dst/out"; mkdir -p "$dst/out"
  cp "$ROOT/tests/heldout/northwind/export_2026-W45.csv" "$dst/data/northwind/"
  cp "$ROOT/tests/heldout/northwind/export_2027-W10.csv" "$dst/data/northwind/"
  cp "$ROOT/tests/heldout/contoso/week_2026-W44.csv"     "$dst/data/contoso/"
  cp "$ROOT/tests/heldout/fabrikam/week_2026-W44.csv"    "$dst/data/fabrikam/"
}

score() {  # client week app_dir out_json
  "$PY" - "$@" <<'EOF'
import json, sys
from pathlib import Path
root = Path(sys.argv[5])
sys.path.insert(0, str(root / "tests"))
import indep_eval as ie
client, week, app, out = sys.argv[1], sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4])
data = app / "data" / client
f = data / f"week_{week}.csv"
if not f.exists():
    f = data / f"export_{week}.csv"
m = ie.evaluate(client, week, app / "out" / client / "schedule.csv", f, app / "data/agents" / f"{client}.csv")
assert not any(m["violations"].values()), m["violations"]
fx = {k: m[k] for k in ("client", "week", "intervals", "sla", "scheduled_hours", "required_hours",
                        "understaffed_interval_hours", "overstaffed_interval_hours", "agents_scheduled")}
out.write_text(json.dumps(fx, indent=2, sort_keys=True) + "\n")
print(f"{out.name}: intervals={fx['intervals']} sla={ {q: round(v, 3) for q, v in fx['sla'].items()} } hours={fx['scheduled_hours']} "
      f"required={fx['required_hours']} ratio={fx['scheduled_hours'] / fx['required_hours']:.4f}")
EOF
}

# 1. seed manifest
"$PY" - "$ROOT/environment/app" "$FIX/seed_manifest.json" <<'EOF'
import hashlib, json, sys
from pathlib import Path
app, out = Path(sys.argv[1]), Path(sys.argv[2])
m = {}
for f in sorted(app.rglob("*")):
    rel = f.relative_to(app).as_posix()
    if f.is_file() and not rel.startswith("out/") and "__pycache__" not in rel and not rel.startswith((".git/", ".pytest_cache/")):
        m[rel] = hashlib.sha256(f.read_bytes()).hexdigest()
out.write_text(json.dumps(m, indent=2, sort_keys=True) + "\n")
print(f"seed_manifest.json: {len(m)} files")
EOF

# 2. baselines: unpatched system on the regression clients' held-out week
stage "$WORK/seed"
for c in contoso fabrikam; do
  (cd "$WORK/seed" && "$PY" -m wfm run --client $c --week 2026-W44 >/dev/null)
  score $c 2026-W44 "$WORK/seed" "$FIX/baseline_${c}_W44.json" "$ROOT"
done

# 3. oracle: patched system on northwind seen + held-out weeks
stage "$WORK/oracle"
(cd "$WORK/oracle" && git apply --whitespace=nowarn "$ROOT/steps/northwind-golive/solution/oracle.patch")
for w in 2026-W44 2026-W45 2027-W10; do
  (cd "$WORK/oracle" && "$PY" -m wfm run --client northwind --week $w >/dev/null)
  score northwind $w "$WORK/oracle" "$FIX/oracle_northwind_${w#2026-}.json" "$ROOT"
done
echo "fixtures written to $FIX"
