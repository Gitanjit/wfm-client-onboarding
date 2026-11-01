#!/usr/bin/env bash
# Step-2 verifier entrypoint ("litware-spring"). Shared helpers (indep_eval, grader, fixtures, held-out weeks)
# come from the task's tests/; this file overlays tests/test.sh for this step only.
set -uo pipefail
mkdir -p /logs/verifier
unset OPENROUTER_API_KEY ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN CLAUDE_CODE_OAUTH_TOKEN OPENAI_API_KEY 2>/dev/null || true
echo "== wfm-client-onboarding verifier, step 2 (litware-spring) =="
python /tests/grader_litware.py --app /app --tests /tests --out /logs/verifier/reward.json 2>&1 | tee /logs/verifier/grader.log
status=${PIPESTATUS[0]}
if [ ! -f /logs/verifier/reward.json ]; then
  echo "grader did not write reward.json (exit $status); writing zero reward"
  cat > /logs/verifier/reward.json <<'JSON'
{"overall": 0.0, "functional_correctness": 0.0, "constraint_satisfaction": 0.0, "regression": 0.0, "artifact_quality": 0.0, "grader_crashed": 1.0}
JSON
fi
echo "== reward =="
cat /logs/verifier/reward.json
exit 0
