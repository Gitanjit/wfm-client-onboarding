#!/usr/bin/env bash
# Final packaging (SESSION6_DECISIONS 2c). Idempotent: on an already-finalized commit it changes nothing and re-checks.
#   PYTHON=<python with pandas/numpy/pyyaml> [KEYFILE=<.env holding the API key>] tools/finalize.sh [--skip-harbor]
# 1 strip the author's review markers, regenerate fixtures, commit if anything changed · 2 marker and key greps ·
# 3 real-path oracle (forced build) and nop on a clean export of HEAD · 4 harbor lint · 5 jobs/ and secrets never
# tracked · 6 git archive zip to dist/ · 7 print the tag command.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd); cd "$ROOT"
PY=${PYTHON:-python3}; MARK='G: your'' call'   # split so this file never matches its own grep
[ -z "$(git status --porcelain --untracked-files=no)" ] || { echo "FAIL: commit or stash first"; exit 1; }
"$PY" - "$MARK" <<'PYEOF'
import re, sys
from pathlib import Path
pat = re.compile(r"^\s*<!-- " + re.escape(sys.argv[1]) + r".*-->\s*$")
files = [f for r in ("environment/app", "steps") for f in Path(r).rglob("*") if f.suffix in (".md", ".txt")]
for p in files + [Path("instruction.md")]:
    if p.is_file():
        t = p.read_text(); s = "".join(l for l in t.splitlines(keepends=True) if not pat.match(l))
        if s != t: p.write_text(s); print("stripped", p)
PYEOF
PYTHON="$PY" tools/make_fixtures.sh >/dev/null
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
  git commit -qam "Strip the author's review markers; regenerate fixtures (tools/finalize.sh)"; echo "committed $(git rev-parse --short HEAD)"
fi
! git grep -n "$MARK" -- . ':!ledger/' || { echo "FAIL: review markers left"; exit 1; }   # ledger/ quotes the marker (D-032, D-033)
! git grep -nE 'sk-[A-Za-z0-9_-]{16,}' || { echo "FAIL: key-shaped string tracked"; exit 1; }   # plain "sk-" hits "desk-11"
if [ -n "${KEYFILE:-}" ]; then
  K=$(grep -E '^ANTHROPIC_API_KEY=' "$KEYFILE" | cut -d= -f2- | tr -d '[:space:]"'"'")
  [ -z "$K" ] || ! git grep -qF -- "$K" || { echo "FAIL: API key tracked"; exit 1; }
fi
echo "greps: clean"
if [ "${1:-}" != "--skip-harbor" ]; then
  W=$(mktemp -d); T="$W/wfm-client-onboarding"; mkdir -p "$T" "$W/jobs"; git archive HEAD | tar -x -C "$T"
  harbor run -p "$T" -o "$W/jobs" -a oracle --force-build --job-name fin-oracle -q >/dev/null
  harbor run -p "$T" -o "$W/jobs" -a nop --job-name fin-nop -q >/dev/null
  "$PY" - "$W/jobs" <<'PYEOF'
import json, sys
from pathlib import Path
want = {"fin-oracle": (1.0, 1.0), "fin-nop": (0.25, 0.0862)}
ok = True
for job, exp in want.items():
    got = tuple(json.loads(p.read_text())["overall"] for s in ("northwind-golive", "litware-spring")
                for p in Path(sys.argv[1], job).glob(f"*/steps/{s}/verifier/reward.json"))
    print(f"{job}: {' / '.join(map(str, got))} (expect {' / '.join(map(str, exp))})"); ok &= got == exp
sys.exit(0 if ok else 1)
PYEOF
  rm -rf "$W"
fi
{ harbor lint --json --extend-select root-agent --extend-select unpinned-image . || true; } | "$PY" -c '   # exits 1 on any finding
import json, sys; f = [x for x in json.load(sys.stdin) if x["rule"] != "root-agent"]
print("lint:", f or "only the optional root-agent rule"); sys.exit(1 if f else 0)'
[ -z "$(git ls-files jobs .secrets '*.env' '*.key')" ] || { echo "FAIL: jobs/ or secrets tracked"; exit 1; }
for p in jobs/x .env x.key dist/x; do git check-ignore -q "$p" || { echo "FAIL: $p not ignored"; exit 1; }; done
mkdir -p dist; Z="dist/wfm-client-onboarding-$(git rev-parse --short HEAD).zip"
git archive --format=zip --prefix=wfm-client-onboarding/ -o "$Z" HEAD
! unzip -Z1 "$Z" | grep -E '(^|/)(jobs|\.secrets)/|\.env$|\.key$' || { echo "FAIL: excluded path in zip"; exit 1; }
echo "zip: $Z ($(unzip -Z1 "$Z" | wc -l | tr -d ' ') entries, $(wc -c < "$Z" | tr -d ' ') bytes, sha256 $(shasum -a 256 "$Z" | cut -c1-12))"
echo "next: git tag ${TAG:-multi-v3-final} $(git rev-parse --short HEAD)"
