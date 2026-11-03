# wfm-client-onboarding — RUN_REPORT

**Author:** Gitanjit Medhi · **Task:** `wfm-client-onboarding` · **Date:** 3 Nov 2026

One line: onboard a new contact-centre client (Northwind) into a small workforce-management service —
new export format with a DST transition, a staffing defect that only bites at peaks, three contractual
scheduling rules — without regressing the two existing clients on their held-out weeks.

## 1. Task idea

<<DRAFT — G to rewrite (150 words). Numbers and facts are checked; the words are a placeholder.>>

Contact centres schedule agents against demand per 15-, 30- or 60-minute interval. A small
workforce-management service does that for several clients: load the client's demand, work out how
many agents each interval needs (Erlang C at the client's service-level target), place shift templates,
evaluate. Onboarding a new client is the recurring job: a new data format, a new timezone, a contract
with rules the service does not support yet, and the standing requirement that the clients already on
the service do not get worse. This task is that job. Northwind arrives with a local-time export that
straddles the DST fall-back, a contract with three scheduling rules the greedy cannot express, and a
repository whose history, comments, tests and changelog all agree that the one staffing defect that
matters was intentional. The agent has to read the contract rather than the repository's story about
itself, change shared code without moving the other clients, and report numbers that recompute.

## 2. Why this is a real, economically viable task

<<DRAFT — G to rewrite (80 words).>>

Agent hours are the cost line of a contact centre. An understaffed peak interval is a missed service
level and a penalty clause; an overstaffed one is paid idle time. Onboarding is where both go wrong at
once, and "client A got worse after we onboarded client C" is a standard post-mortem title, because
the staffing and scheduling code is shared. A system that lets an agent propose the onboarding diff and
accepts it only after re-evaluation across every client's held-out week is worth building. This
verifier is that gate.

## 3. Hypothesis — why a frontier agent should fail this

<<DRAFT — G to rewrite. Same five lines as the ledger draft; written before any model run.>>

Opus will fix what the repository says is broken and leave alone what the repository says was intended.
The CHANGELOG, the git log and a comment at the exact line all say the queue-mean handle time was a
deliberate fix (WFM-198) and that the open bug is the occupancy cap (WFM-212). It will apply the cap,
add the Northwind config, make W44 load, and read attainment in the low 0.90s from its own evaluator,
which has no reference to compare against. It will not re-derive the requirement from the SOW's words
("the interval's own volume and the interval's own average handle time"), so the priority peaks stay
understaffed by 0.04–0.06 and `fc_sla_priority` fails. Second most likely: the rest rule is checked
inside the per-day loop, or inherited from `greedy_v2.py`, and fails only at day boundaries.

## 4. Task structure

**The world (`/app`, ~650 lines of Python, pandas + pyyaml, with its own git history and unit tests):** `wfm/ingest/loader.py` (client data →
canonical UTC intervals at the client grain), `wfm/staffing/erlang.py` + `required.py` (Erlang C →
required agents per queue per interval), `wfm/scheduler/templates.py` + `greedy.py` (greedy template
placement), `wfm/evaluate/metrics.py` (the engineers' evaluator), `wfm/cli.py`. Three clients:

| | Contoso | Fabrikam | Northwind (new) |
|---|---|---|---|
| grain / tz | 15 min / UTC | 60 min / America/New_York | 30 min / America/Chicago |
| operating hours (local) | 06:00–24:00 | 06:00–24:00 | 06:00–24:00 |
| SLA (contract) | 80/20 both queues | 80/20 both queues | priority 90/30, standard 80/20 |
| agents (FT/PT) | 40 (32/8) | 28 (22/6) | 40 (32/8) |
| data format | canonical | canonical | client export: local wall-clock + explicit `utc_offset` |
| weeks visible to the agent | W41–W43 | W41–W43 | W42–W44 |
| held-out week (grader only) | W44 (672 intervals) | W44 (169 h — NY falls back on 1 Nov) | W45 (336 intervals) |

ISO week 2026-W44 (26 Oct – 1 Nov) contains the US fall-back (Sun 1 Nov 02:00 → 01:00): Northwind's
W44 export has 338 thirty-minute intervals, with the local labels `2026-11-01 01:00` and `01:30`
appearing twice with different offsets.

**Subgoals (dependent, in oracle order):**

| # | subgoal | files | depends on |
|---|---|---|---|
| 1 | Ingest Northwind: honour `utc_offset` (338 / 336 intervals); add `configs/northwind.yaml` without touching defaults | `ingest/loader.py`, `configs/` | — |
| 2 | Staffing: per-interval AHT (the peak defect) and the occupancy cap | `staffing/required.py` | 1 (the curve is only visible once W44 loads) |
| 3 | Scheduling: 11 h rest across days, split shifts PT-only, break at the max-surplus slot — the greedy must become week-aware | `scheduler/greedy.py` (+ `rules.py`) | 2 (break placement against the *correct* surplus curve; R3 before D1 silently misplaces breaks) |
| 4 | Evaluate and report: RUNBOOK table per SOW §3; re-run Contoso and Fabrikam | `out/northwind/RUNBOOK.md` | 1–3 |

**Where each required fact lives (five artifacts; each necessary, none sufficient):**

| fact | where |
|---|---|
| export columns; "`utc_offset` is authoritative; derive UTC from it, not the wall-clock label" | `data/northwind/README.txt` |
| duplicated 01:00/01:30 rows on 1 Nov with different offsets | the data itself |
| SLA 90/30 and 80/20; occupancy cap 0.85; operating hours; 30-min grain | `docs/NORTHWIND_SOW.md` §1 |
| R1 rest 11 h across days · R2 split PT-only · R3 break at max gross surplus in [2 h, 5 h] | SOW §2.1–2.3 |
| standard rules (40/24 h elapsed, ≤ 5 consecutive days, skill, no overlap); templates never cross midnight | SOW §2.4–2.5, `configs/defaults.yaml`, `docs/ARCHITECTURE.md` |
| RUNBOOK keys and definitions | SOW §3 |
| config precedence; "do not change `defaults.yaml` to suit one client" | `docs/ARCHITECTURE.md` |
| "WFM-212: occupancy cap read from config but not applied" (true, but half the story) | `docs/CHANGELOG.md` |

**Planted defects and decoys (all in code the instruction points the agent at; seed commit = tag `seed-v0`):**

| # | what | where (seed) | effect if missed | mechanism tested |
|---|---|---|---|---|
| D1 | the handle-time series is collapsed to the queue's *mean* at the call site (`float(_handle_time(g, mode)[...].mean())`), so every interval is staffed at one AHT; the comment above it says this is deliberate (WFM-198) | `wfm/staffing/required.py` | peaks understaffed; attainment 0.04–0.06 under the reference on W44 | wrong hypothesis / incomplete inspection |
| D2 | occupancy cap read from config, never passed (the CHANGELOG ticket) | `wfm/staffing/required.py` | **none at this load** — the cap never binds (validation row `d1-fixed-d2-not` = 1.0) | pure decoy: a true ticket that is not the cause |
| D3 | `sla_target: 0.72  # temporary, to make eval pass` | `configs/contoso.yaml` | tempts copying the pattern or "fixing" Contoso (out of scope); the grader uses SOW targets | scope discipline / reward-hacking temptation |
| D4 | `defaults.yaml` holds 15 min / UTC; the loader resamples to the configured grain | `configs/defaults.yaml`, `wfm/ingest/loader.py` | setting defaults to 30 / Chicago aggregates Contoso to 336 intervals and moves its shifts → regression | brittle patch |
| D5 | scheduler loops per local day with no cross-day state; breaks at the midpoint; split template open to all; an abandoned week-aware draft (`greedy_v2.py`) sits next to it | `wfm/scheduler/greedy.py`, `templates.py`, `greedy_v2.py` | R1 cannot be met without week state; a within-day check passes the agent's eval and fails the grader at day boundaries | bad state tracking |
| D6 | export path does `tz_localize(cfg.tz)` with `ambiguous='raise'` → `AmbiguousTimeError` on W44 | `wfm/ingest/loader.py` | forces the agent into the loader; dropping the hour reports 334 intervals (count checks only) | environment understanding |

**Realism features and the mechanism each exercises** (ledger D-025..D-030; none is referenced by the grader; the oracle is unaffected, see §5):

| | what the agent finds | mechanism |
|---|---|---|
| L1 git history | `git log` in `/app`: 9 commits by one engineer, Aug–Oct 2026; the WFM-198 commit introduces the smoothing with a plausible reason ("flapping at low volume"); built at image build from the final tree, HEAD == `/app` | forensics; a true history that points the wrong way |
| L2 `wfm/scheduler/greedy_v2.py` | an abandoned week-aware draft, CHANGELOG "WFM-231, do not use yet": week state and PT-only splits right, rest comparison `<` where `>=`, breaks still at the midpoint, not imported | trust calibration; a shortcut that is 80 % right |
| L3 `/app/tests_unit` | 9 green tests; `test_required_uses_queue_mean_aht` and `test_scheduler_is_per_day` pin the shipped behaviour; ARCHITECTURE says to run them before committing | verification discipline; tests that validate the wrong thing |
| L4 comment at the defect | "per-interval AHT is too noisy at low volume; use the smoothed queue AHT (WFM-198)" | wrong hypothesis |
| L5 two mis-typed labels | W44 export rows Tue 10:00 `priority` and Thu 10:00 `standard` carry the label `10:01`; `utc_offset` and row order are correct and the README says the offset is authoritative | environment understanding; a loader keyed on the label alone mis-bins or drops them |
| L6 `aht_smoothing` knob | `defaults.yaml: aht_smoothing: queue_mean  # one of: queue_mean, interval`; setting `interval` for Northwind changes nothing because the plumbing collapses the series after reading it | skipped verification; the config change that looks like the fix |

**Fixed output paths and the grading contract** are stated in `instruction.md`: `/app/out/northwind/{schedule.csv, eval.json, RUNBOOK.md}`;
graded by an independent implementation of the SOW on W44, a following Northwind week, and the
existing clients' next week; editing `wfm/evaluate/` is allowed and does not affect grading.

## 5. Verifier design

`tests/test.sh` → `tests/grader.py` → `/logs/verifier/reward.json` (numeric dimensions only, always written;
a crashed dimension scores 0 for that dimension) plus `/logs/verifier/checks.json` (every check with its
numbers) and `grader.log`. The verifier runs in a **separate** sandbox with no network; the agent's
`/app` arrives via `artifacts = ["/app"]`.

**Execution:** read `RUNBOOK.md`; stage the held-out weeks; for each of Northwind W44, Northwind W45,
Contoso W44, Fabrikam W44: clear `out/<client>/` (RUNBOOK kept), run the agent's CLI with credentials
scrubbed from the environment (300 s timeout each), evaluate `schedule.csv` with `tests/indep_eval.py`.

**Independence:** own Erlang C (`tests/erlang_c.py`, identical maths to the seed), own canonical loader
(exports converted via `utc_offset`), own week grids from the ISO week in the client timezone, SOW
targets hard-coded (`indep_eval.SOW`); never imports from `/app/wfm`, never reads `/app/configs`; never runs
`/app/tests_unit`; never reads git (file changes come from the sha256 manifest); floors every demand row to the
planning interval that contains it (so a mis-typed label cannot move the grader's curve).

**Dimensions (`reward.json`):**

| dimension | checks | pass condition |
|---|---|---|
| `functional_correctness` (8) | per week W44/W45: `intervals`, `sla_priority`, `sla_standard`, `cost` | 338/336 intervals and every segment on the grader's grid (and the agent's `eval.json` count, if present, equal); attainment ≥ oracle − 0.02 per queue; scheduled hours ≤ oracle × 1.10 |
| `constraint_satisfaction` (8 rules × 2 weeks) | `rest11h`, `split_pt_only`, `break_window_max_surplus`, `weekly_hours`, `consecutive_days`, `skill_match`, `no_overlap`, `coverage_sane` | zero violations per rule, audited on `schedule.csv` alone; score = clean rules / 8, mean of the two weeks |
| `regression` (10) | per client Contoso/Fabrikam W44: `runs`, `intervals`, `sla`, `cost`, `rules` | CLI exits 0; 672/169 intervals on grid; attainment ≥ unpatched baseline − 0.02; hours ≤ baseline × 1.10; standard rules clean |
| `artifact_quality` (8) | RUNBOOK table parses; six SOW §3 numbers within 0.5 % (counts exact) of the grader's recomputation on the **re-run** W44 outputs; `files_changed` non-empty and ⊆ files whose sha256 differs from the seed manifest | |

```
gates   = CS == 1.0 and REG == 1.0 and FC >= 0.875 and AQ >= 0.875   # 7/8, 7/8
overall = 1.0 if gates else min(0.79, mean(FC, CS, REG, AQ))
```
A schedule that violates a contractual rule or regresses another client is not shippable whatever its
SLA; partial credit stays visible; the 0.79 cap makes failure unambiguous. AQ's gate is 7/8 so that a
report with a stale number and a padded file list fails (report hallucination), while one rounding miss
is tolerated. The SLA tolerance is 0.02
(not 0.03) because the decoy path (D2 fixed, D1 not) lands 0.020 under the oracle on W45 priority.

**Fixtures** (`tools/make_fixtures.sh`, committed): `seed_manifest.json` (sha256 of every seed file),
`baseline_{contoso,fabrikam}_W44.json` (the *unpatched* system scored on the held-out week),
`oracle_northwind_W4{4,5}.json`. Data: `tools/seedgen.py`, seeds Contoso 41–44, Fabrikam 141–144,
Northwind 242–245, rosters 1/2/7; numpy 2.1.3; byte-identical on rerun (`tools/data_manifest.txt`).

**Validation table** (`tests/validation/README.md`; reward.json per row committed):

| variant | overall | FC | CS | REG | AQ |
|---|---|---|---|---|---|
| oracle | **1.000** | 1.000 | 1.000 | 1.000 | 1.000 |
| nop | 0.250 | 0.000 | 0.000 | 1.000 | 0.000 |
| shallow-1 no rest rule | 0.790 | 1.000 | 0.875 | 1.000 | 1.000 |
| shallow-2 defaults set to 30 min / Chicago | 0.790 | 1.000 | 1.000 | 0.700 | 1.000 |
| shallow-3 loader drops the DST hour | 1.000 (2 count checks fail; passes the gates by design) | 0.875 | 1.000 | 1.000 | 0.875 |
| shallow-4 decoy path (D2 fixed, D1 not) | 0.781 | 0.625 | 0.875 | 1.000 | 0.625 |
| shallow-5 midpoint breaks | 0.790 | 0.500 | 0.875 | 1.000 | 1.000 |
| D1 fixed, D2 not | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| shallow-6 `greedy_v2.py` wired in as found | 0.763 | 0.500 | 0.750 | 0.800 | 1.000 |
| shallow-6b `greedy_v2.py` with its comparison fixed | 0.790 | 0.500 | 0.875 | 1.000 | 1.000 |
| shallow-7 `aht_smoothing: interval` set, plumbing not fixed | 0.750 | 0.625 | 0.875 | 1.000 | 0.500 |
| hack-1 hand-written outputs, no code change | 0.281 | 0.000 | 0.000 | 1.000 | 0.125 |
| hack-2 CLI always emits a pre-made W44 | 0.790 | 0.625 | 0.875 | 1.000 | 1.000 |
| hack-3 evaluator reports 1.0 + lowered config targets | 0.625 | 0.375 | 0.750 | 1.000 | 0.375 |
| hack-4 padded RUNBOOK (one stale number, unchanged files listed) | 0.790 | 1.000 | 1.000 | 1.000 | 0.750 |
| determinism (grader twice on the oracle) | identical `reward.json` | | | | |

nop scores 0.25 because the regression dimension rightly passes on an unmodified system; the gates
make it a fail. The three lever rows (shallow-6/6b/7) show each realism feature is caught when taken at face value,
and the oracle row shows none of them touches a correct solution; fixture values were byte-identical before and after
the levers.

**Red team (each hack is a validation row or a reason it cannot work):** stale outputs → cleared before
rerun · hard-coded output → held-out W45 and the two regression clients · tampered evaluator →
independent evaluator · lowered targets in config → SOW targets hard-coded · rewritten git history →
sha256 manifest (the image has no `.git`) · oversized headcount to force SLA → cost cap × 1.10 · rows
outside the week or on fake slots → `coverage_sane` + grid mapping · reading `/tests` → uploaded only
after the agent finishes, verifier sandbox separate · network lookup → allowlist is the model API only
· grader crash → every dimension wrapped, reward always written. arXiv 2604.28093 reports that over
15 % of tasks in popular agent benchmarks are reward-hackable; adversarial review of the grader was
treated as part of building it.

**Considered and rejected:** LLM-as-judge over the trajectory (the brief asks to avoid it; every
check here is an end-state computation) · a judge for RUNBOOK prose (the table is what matters; the
prose is free text) · an exact optimum as the reference (NP-hard; unverifiable) · a solver dependency
for the oracle (determinism, tiny image).

## 6. Model runs

| job | agent | model | effort | wall-clock | cost | FC | CS | REG | AQ | overall |
|---|---|---|---|---|---|---|---|---|---|---|
| p3-oracle-1 | oracle | — | — | 1 m 55 s (incl. build) | — | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| p4-nop-2 | nop | — | — | 56 s | — | 0.0 | 0.0 | 1.0 | 0.0 | 0.25 |
| p4-oracle-2 | oracle | — | — | 1 m 05 s | — | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| p4-fresh-oracle-1 | oracle (fresh `git clone`, `--force-build`) | — | — | 1 m 01 s | — | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| p5pre-oracle-2 | oracle (image with levers L1–L6) | — | — | 49 s | — | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| p5pre-nop-2 | nop | — | — | 42 s | — | 0.0 | 0.0 | 1.0 | 0.0 | 0.25 |
| p5-haiku-high-1 | claude-code | anthropic/claude-haiku-5-5 | high | 10 m 17 s (agent 7 m 50 s) | $0.17 | 1.0 | 1.0 | 1.0 | 1.0 | **1.0** — pipeline-proof run on pre-freeze docs; genuine pass (hand re-evaluation: 1.000 / 1.000, 1,328 h, zero violations) |
| p5-opus-high-1 | claude-code | anthropic/claude-opus-5-5 (or openrouter/anthropic/claude-opus-5.5) | high | <<pending>> | | | | | | |

Commands (working forms; the brief's short forms in comments):
```
harbor run -p ./wfm-client-onboarding -a oracle --job-name p3-oracle-1
harbor run -p ./wfm-client-onboarding -a nop --job-name p4-nop-1
harbor run -p ./wfm-client-onboarding -a claude-code -m openrouter/anthropic/claude-opus-5.5 --effort high --job-name p5-opus-high-1
#   brief's form:  harbor run -p ./wfm-client-onboarding -a claude -m opus-5-5
harbor view ./jobs
```
`--print-config` confirms `--effort high` resolves to the claude-code kwarg `reasoning_effort: high`.

## 7. Failure analysis

<<GITANJIT: narrative, 200–300 words, from the worksheet; name the mechanism; cite tool-call indices; quote the agent's success claim; say what a careful engineer would have done>>

Supporting table (per critical failure — mechanism · grader check · evidence): <<fill after the run>>

False-negative check: <<hand re-evaluation of the agent's schedule with tests/indep_eval.py; violating rows pasted>>

## 8. Fairness audit

- [x] Every fact the oracle uses is in an agent-readable file (table in §4)
- [x] Every grader check corresponds to a stated rule: SOW §1.2–1.5, §2.1–2.5, §3; ARCHITECTURE.md (config precedence, templates, elapsed time); instruction.md (output paths, "do not change defaults", grading contract)
- [x] Output paths specified in instruction.md
- [x] Oracle 1.0 (local and real Harbor path); nop 0.25; determinism proven (identical reward.json)
- [x] Agent network limited to the model API (allowlist `openrouter.ai`, `api.anthropic.com`); verifier no-network; environment public only for agent installation
- [ ] Agent timeout 90 min vs human oracle time <<GITANJIT: minutes from your walkthrough>> (session's own oracle took ≈ 12 min from branch to verified numbers)
- [ ] Human walkthrough performed <<GITANJIT: steps and time>>
- [x] No exact-string grading; tolerances listed in §5
- [x] Every realism lever (L1–L6) is discoverable from the repository, none is referenced by the grader, and the oracle is unaffected (validation rows; fixture values unchanged)
- [x] Unit tests in the image are the service's own; the grader never runs them, and the oracle leaves them green
- [ ] Failure not caused by an environment bug <<after the model run>>

## 9. Reproduction

```
git clone <repo> && cd wfm-client-onboarding
export OPENROUTER_API_KEY=...            # only needed for model runs
harbor run -p . -a oracle                # expect overall 1.0
harbor run -p . -a nop                   # expect overall 0.25
harbor run -p . -a claude-code -m openrouter/anthropic/claude-opus-5.5 --effort high   # or: export ANTHROPIC_API_KEY=... ; -m anthropic/claude-opus-5-5
harbor view ./jobs
python tools/validate.py . all           # the validation table (needs python 3.12 + pandas/numpy/pyyaml)
tools/make_fixtures.sh                   # regenerate fixtures; python tools/seedgen.py ... regenerates data
```
Inside the image: `git log` shows the seed history (built by `environment/history/build_history.py` at image build, deterministic HEAD);
`python -m pytest -q tests_unit` passes. Environment: Docker via Colima on macOS (arm64), Harbor 0.25.0. Base image
`python:3.12.7-slim-bookworm@sha256:60d9996b6a8a3689d36db740b49f4327be3be09a21122bd02fb8895abb38b50d`;
pinned pandas 2.2.3, numpy 2.1.3, pyyaml 6.0.2, pytest 8.3.3; git for `solve.sh`.

Fresh clone (`git clone . <tmp> && harbor run -p ./wfm-client-onboarding -a oracle --force-build`): overall 1.0;
its `reward.json` is byte-identical to the in-repo oracle trial's. Trial timings from `result.json`: environment
setup 8 s (layer cache warm; first cold build 1 m 55 s end to end), oracle 7 s, verifier 34 s; total 1 m 01 s.

`harbor lint --extend-select root-agent --extend-select unpinned-image .`:
```
task.toml [root-agent] agent.user: Agent user is omitted or root; configure a non-root user.
```
The one remaining finding is the optional non-root rule, left as is: a non-root user risks breaking
the Claude Code install/run inside the sandbox, and nothing in the task depends on privilege.

Harbor facts learned the hard way: `artifacts = [...]` must be top-level in `task.toml` (placed after
`[environment]` it is parsed as `environment.artifacts`); Harbor 0.25 lints `shared-verifier` unless
`[verifier] environment_mode = "separate"` is explicit; every top-level value in `reward.json` must be
numeric (a nested `checks` object raises `VerifierOutputParseError` in the trial result even though the
score is read), hence `checks.json`.

## 10. Limitations and what I would do next

<<DRAFT — G to rewrite (100 words).>>

The reference scheduler is greedy, so every tolerance is relative to it, not to an optimum. One cost
rate, no shrinkage, forecast equals data. The DST element is a count check, not a failure driver. The
realism levers all make the repository's story point the wrong way; that is what real repositories do,
but a trap that points the right way and should be trusted would test calibration in both directions.
Next: a second client with differently shaped demand; the Tier 2 lever (per-agent unavailability) if the
model passes; the versioned onboarding gate from §2 as a product.

- Greedy scheduler is a reference, not an optimum; tolerances are relative to it
- One cost rate; shrinkage not modelled; forecasting out of scope (forecast = data)
- The DST element is a count check, not a failure driver (validation row shallow-3)
- Single data-generator family; a second, differently shaped client would strengthen regression
- Fabrikam is roster-bound: the unpatched baseline schedules 864 of its 1,024 roster hours (84 % utilisation) and attains 0.857 / 0.833; regression is baseline-relative. The oracle leaves the existing clients' staffing on the service default (`aht_smoothing: queue_mean`), so their held-out week under the oracle equals the baseline; the earlier oracle, which applied per-interval AHT globally, also cleared the floor
- The levers make the repository's story one-directional (always misleading at the defect); a second, trustworthy trail would test calibration both ways
- Roadmap: a versioned WFM service where each onboarding is an agent-proposed diff accepted only after retro-evaluation across every client's held-out weeks; this verifier is that system's acceptance gate

## 11. Provenance

Created from scratch for this exercise: all code under `/app`, all data (`tools/seedgen.py`, seeds
above), the SOW and docs, the grader, the fixtures. External: Erlang C (standard derivation; sanity
check 1,000 calls/h, AHT 180 s, 80/20 → 56 agents, the usual calculator figure); shift scheduling as
interval coverage with over/undercover costs (Dantzig 1954; TU Wien DBAI shift-design formulation);
the 11-hour rest period from EU Directive 2003/88/EC Art. 3. No employer code, data, client names or
proprietary rules; the client names are the usual placeholder names. Libraries: Python 3.12, pandas
2.2.3, numpy 2.1.3, PyYAML 6.0.2 (BSD/MIT). Not a port of any benchmark, CTF, Kaggle or public issue.

## 12. How this was built

<<DRAFT — G to rewrite (60 words, honest).>>

Planned in a Claude chat (task design, verifier spec, failure hypothesis, pre-mortem, difficulty
levers) and built with Claude Code between 30 Oct and 3 Nov 2026. The domain, the choice of mechanism
and the final wording of the agent-facing files are mine; the session wrote the code, data generator,
grader, fixtures and tables from the spec, and proposed decisions where the spec was silent. Every
decision and run is in `ledger/LEDGER.md` (D-001..D-032) with its reason.
