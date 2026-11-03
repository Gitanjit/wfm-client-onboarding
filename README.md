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

## `abl/closed`: the template set closed (v4 candidate; not the submitted task)

Northwind SOW §2.5 and Litware SOW §2.10 add one sentence: "Shifts use the templates listed in ARCHITECTURE
for this client; no other shapes." The grader enforces it as the SOW §2 rule `templates_in_set`
(`tests/indep_eval.py`): each shift (an agent's rows on one local day, back-to-back rows merged) has the local
segments of one ARCHITECTURE template that fits the client's operating hours, with one break if the template
is six hours or more and none otherwise. It counts in step-1 CS, step-2 CS and step-2 REG (Northwind's carried
weeks). The oracle is unchanged.

With the set closed, vip cannot reach 0.95 in any graded week: `tools/vip_bound.py`, desk 11 (all FT, so
no split template), gives a ceiling of 0.923 (W44), 0.929 (W45), 0.917 (2027-W10) and 0.940 (2027-W11).

Validation on this branch: step 1 oracle 1.0, nop 0.25; step 2 oracle 1.0, nop 0.399. Replays under this
grader (`tests/validation/closed_replays/`): s6-opus-1's step-2 /app, which added client templates, scores
0.79 (CS and REG fail on `templates_in_set`); s7-r1-opus-k151's step-1 /app scores 0.79; s6-opus-1's step-1
/app (stock templates plus the §2.7 row) scores 1.0.
