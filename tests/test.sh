#!/usr/bin/env bash
# Verifier entrypoint. Runs in the verifier sandbox; the agent's /app arrives via task.toml `artifacts`.
# Must ALWAYS leave /logs/verifier/reward.json behind.
set -uo pipefail   # no -e on purpose: a grader exception must not skip the reward file

mkdir -p /logs/verifier
# Scrub any model credentials from the verifier's environment before running the agent's code.
unset OPENROUTER_API_KEY ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN CLAUDE_CODE_OAUTH_TOKEN OPENAI_API_KEY 2>/dev/null || true

echo "== wfm-client-onboarding verifier =="
if [ ! -d /app/wfm ]; then
  echo "WARN: /app/wfm missing in verifier sandbox (artifacts not delivered?)"
fi

python /tests/grader.py --app /app --tests /tests --out /logs/verifier/reward.json 2>&1 | tee /logs/verifier/grader.log
status=${PIPESTATUS[0]}

if [ ! -f /logs/verifier/reward.json ]; then
  echo "grader did not write reward.json (exit $status); writing zero reward"
  cat > /logs/verifier/reward.json <<'EOF'
{"overall": 0.0, "functional_correctness": 0.0, "constraint_satisfaction": 0.0, "regression": 0.0, "artifact_quality": 0.0, "checks": {"grader_crashed": true}}
EOF
fi

echo "== reward =="
cat /logs/verifier/reward.json
exit 0
