# collinear-candidate/wfm-client-onboarding

A long-horizon Harbor task: onboard a new contact-centre client into a small workforce-management
service without regressing the existing clients. Full write-up: [`RUN_REPORT.md`](RUN_REPORT.md).

```
harbor run -p . -a oracle                                                              # expect overall 1.0
harbor run -p . -a claude-code -m openrouter/anthropic/claude-opus-5.5 --effort high   # brief's form: -a claude -m opus-5-5
harbor view ./jobs
```

Layout: `instruction.md` · `task.toml` · `environment/` (Dockerfile + the seed system in `app/`) ·
`solution/` (oracle patch + runbook writer) · `tests/` (grader, independent evaluator, fixtures,
held-out weeks, validation table) · `tools/` (data generator, fixtures builder, validation script).
