# collinear-candidate/wfm-client-onboarding

A long-horizon, two-step Harbor task in one container. Step 1 (`northwind-golive`): onboard a new
contact-centre client into a small workforce-management service and meet its contract, including an
efficiency bound, without regressing two existing clients. Step 2 (`litware-spring`, months later, a
fresh agent conversation on the same filesystem): onboard a fourth client whose contract and data break
step-1 shortcuts, and keep the first three clients whole. Trial reward = mean of the two steps.
Full write-up: [`RUN_REPORT.md`](RUN_REPORT.md).

```
harbor run -p . -a oracle                                                              # expect 1.0 on both steps
harbor run -p . -a claude-code -m openrouter/anthropic/claude-opus-5.5 --effort high   # brief's form: -a claude -m opus-5-5
harbor run -p . -a claude-code -m anthropic/claude-opus-5-5 --effort high              # same, on an Anthropic key
harbor view ./jobs
```

Layout: `task.toml` (`[[steps]]`, `mean`) · `environment/` (Dockerfile + the seed system in `app/`) ·
`steps/northwind-golive/` (instruction, oracle patch + runbook writer) · `steps/litware-spring/`
(instruction, `workdir/` = Litware SOW, data and roster delivered into /app before step 2, oracle patch on
top of step 1's, `tests/test.sh`) · `tests/` (both graders, independent evaluator, fixtures, held-out weeks,
validation tables) · `tools/` (data generator, fixtures builder, validation scripts for each step).
The single-step revision is tag `single-v1`.
