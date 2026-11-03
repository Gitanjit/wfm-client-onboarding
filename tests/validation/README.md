# Verifier validation

Each JSON here is the grader's `reward.json` (plus its `checks.json` detail under `checks`) for one variant, produced by applying the variant to a
pristine copy of `environment/app`, running the agent-side steps, and running `tests/grader.py`
against it (local simulation of the Harbor flow; the real-path numbers for oracle/nop are in
`RUN_REPORT.md` §6). Regenerate with `python tools/validate.py . all`.

Revision `single-v1`: Northwind is graded on W44 (seen), W45 and 2027-W10 (held-out; the US spring-forward week, 334 intervals).
FC = 12 checks (per week: interval count, attainment ≥ 0.95 per queue, scheduled hours ≤ 1.57 × the grader's required hours — SOW §1.6), gate 11/12.
CS = the 8 SOW rules on each of the three weeks. REG unchanged. AQ = 9 checks (table, seven numbers, `files_changed`), gate 8/9.

| variant | what it is | overall | FC | CS | REG | AQ | what the grader sees |
|---|---|---|---|---|---|---|---|
| oracle | `solution/oracle.patch` + runbook (efficiency pass on) | **1.000** | 1.000 | 1.000 | 1.000 | 1.000 | sound; hours 1,248 / 1,220 / 1,234 vs bounds 1,270.9 / 1,267.8 / 1,260.7 |
| nop | untouched system | 0.250 | 0.000 | 0.000 | 1.000 | 0.000 | REG rightly passes on an unmodified system; gates fail it |
| oracle-unimproved | oracle without the efficiency pass (correct, rule-clean) | 0.790 | 0.750 | 1.000 | 1.000 | 1.000 | cost on all three weeks: ratio 1.621 / 1.625 / 1.624 > 1.57 (§1.6) |
| unoptimised-correct | Haiku 5.5's own fix from p5-haiku-high-1 (1.0 on the pre-bound revision) replayed on this seed, its own RUNBOOK | 0.790 | 0.750 | 1.000 | 1.000 | 0.778 | cost on all three weeks (1,328 / 1,328 / 1,344 h, ratio 1.64–1.67); `files_changed` lists two docs the replay leaves out; `required_hours_total` absent |
| drop-only-pass | efficiency pass that only drops shifts | 0.790 | 0.750 | 1.000 | 1.000 | 1.000 | recovers nothing (1,312 h): the greedy never places a fully redundant shift; cost on all three weeks |
| drop-shrink-nested | efficiency pass that drops or shrinks to a template inside the span (the basic pass) | 1.000 | 0.917 | 1.000 | 1.000 | 1.000 | **passes**: 1,264 / 1,260 / 1,262 h; misses the W10 bound by 1.3 h, absorbed by the 11/12 FC gate |
| stale-breaks | efficiency pass run after break placement, breaks not re-placed | 0.790 | 1.000 | 0.875 | 1.000 | 1.000 | `break_window_max_surplus` on all weeks (shortened shifts lose their break; dropped coverage moves the surplus) |
| offset-table-loader | Northwind export read through the WFM-204 precedent with a Chicago table on 2026 dates (L11) | 0.790 | 0.917 | 0.958 | 1.000 | 0.889 | W44 count 336 ≠ 338 (the repeated fall-back hour collapses) and one R3 violation on the W10 spring-forward Sunday; FC 11/12 alone would pass, CS fails it |
| shallow-1-no-rest | oracle minus the 11 h rest rule | 0.790 | 1.000 | 0.875 | 1.000 | 1.000 | `rest11h` violations every week |
| shallow-2-defaults-grain | oracle, but `defaults.yaml` set to 30 min / Chicago | 0.790 | 1.000 | 1.000 | 0.700 | 1.000 | Contoso: 336 intervals, segments off the week grid, SLA drop |
| shallow-3-nat-loader | oracle, but the loader drops the ambiguous DST hour | 1.000 | 0.917 | 1.000 | 1.000 | 0.889 | W44 count and RUNBOOK count fail (334 ≠ 338); **passes the gates by design** — the DST element is a count check |
| shallow-4-decoy-d2-only | occupancy cap applied, weekly-mean AHT kept (the CHANGELOG decoy path) | 0.753 | 0.583 | 0.875 | 1.000 | 0.556 | attainment under the 0.95 floor on 5 of 6 queue-weeks; breaks against the wrong surplus curve (R3) |
| shallow-5-midpoint-breaks | oracle with midpoint breaks (R3 skipped) | 0.790 | 0.500 | 0.875 | 1.000 | 1.000 | R3 violations; attainment 0.94 < 0.95 on every queue-week |
| shallow-6-wire-v2 | oracle's loader/config/staffing with the abandoned `greedy_v2.py` wired in as found | 0.762 | 0.500 | 0.750 | 0.800 | 1.000 | inverted rest check: coverage collapses, Contoso/Fabrikam regress; midpoint breaks |
| shallow-6b-wire-v2-fixed-rest | as shallow-6 with the comparison corrected | 0.781 | 0.250 | 0.875 | 1.000 | 1.000 | midpoint breaks, attainment under the floor, and no efficiency pass (cost) |
| shallow-7-knob-only | `aht_smoothing: interval` set for Northwind, staffing plumbing left as shipped | 0.726 | 0.583 | 0.875 | 1.000 | 0.444 | curve did not move: decoy-path failures; `files_changed` names `required.py`, which this variant did not change |
| d1-fixed-d2-not | per-interval AHT fixed, occupancy cap not applied | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | passes: the cap never binds at this load (D2 is a decoy, not a requirement) |
| hack-1-handwritten-outputs | no code change; oracle outputs copied into `out/` | 0.278 | 0.000 | 0.000 | 1.000 | 0.111 | outputs cleared before rerun; CLI crashes on W44 |
| hack-2-cli-copies-w44 | CLI edited to always emit a pre-made W44 schedule | 0.790 | 0.500 | 0.833 | 1.000 | 1.000 | held-out W45 and W10: segments off the grid |
| hack-3-evaluator-lies | `wfm/evaluate` reports 1.0; config targets lowered; DST hour dropped | 0.625 | 0.417 | 0.750 | 1.000 | 0.333 | independent evaluator with SOW targets ignores both |
| hack-4-runbook-padded | oracle, but RUNBOOK lists unchanged files and one stale number | 0.790 | 1.000 | 1.000 | 1.000 | 0.778 | two report checks fail; AQ gate is 8/9, so this fails; one rounding miss would still pass |
| determinism | grader run twice on the oracle output | identical `reward.json` | | | | | byte-deterministic |

How k = 1.57 was set (ledger D-037): the reference is the oracle plus its efficiency pass (drop a shift, give it a shorter
template, or move it to a same-length template when that raises the met count; floor = the greedy's met count per queue-day;
breaks re-placed in every evaluation). Its ratios are 1.5417 (W44), 1.5108 (W45), 1.5367 (W10); k = max × 1.015 = 1.5648,
rounded **up** to two decimals so the reference keeps at least 1.5 % on every week (1.8 % / 3.9 % / 2.2 %). Haiku's W44 schedule
fails by 4.5 %; the unimproved oracle by 3.2 %.

Realism levers L1–L6 (ledger D-025..D-030) and L11 (D-038) leave the oracle at 1.000; the grader never runs `tests_unit`, never reads
git, and floors demand rows to the planning interval. Earlier revisions' tables are in git history (`seed-v0`, commit 81fccf4).

## k = 1.51 variant (branch `abl/k151`, SESSION7_SIDE D-072; not the submitted task)

The only change from `multi-v3` with markers stripped: Northwind SOW §1.6 k 1.57 → 1.51, which is D-037's rule on the multi-v3
reference (max 1.487 × 1.015 = 1.509, rounded up). The grader constant changes with it, and step 2 imports it. Tables run on 3 Nov
2026, 21:05–21:55 IST, with precedents' guarded `tools/validate.py` (c15751b) and `tools/validate_step2.py`. "multi-v3 overall" is the
committed row file on `precedents` (desk 11).

**Result:** every row lands where multi-v3's table says, except three:
- **`oracle-unimproved`, `drop-only-pass` and `drop-shrink-nested`:** they pass at 1.57 because the bound has 5–8 % slack
  once vip is in (D-058). At 1.51 they **fail on cost again**: FC 15/18 or 16/18 against a gate of 17. This is the catch the bound
  was designed to make.
- **`sonnet-replay`:** recorded below; the difference is not caused by k.

Step 2 is unchanged row for row.

Step 1 (grader.py, k = 1.51)

| variant | multi-v3 overall | k = 1.51 overall | FC | CS | REG | AQ | change |
|---|---|---|---|---|---|---|---|
| compose-all-three | 0.6155 | 0.6155 | 0.333 | 0.583 | 1.000 | 0.545 |  |
| d1-fixed-d2-not | 1.0000 | 1.0000 | 1.000 | 1.000 | 1.000 | 1.000 |  |
| determinism-run1 | 1.0000 | 1.0000 | 1.000 | 1.000 | 1.000 | 1.000 |  |
| determinism-run2 | 1.0000 | 1.0000 | 1.000 | 1.000 | 1.000 | 1.000 |  |
| drop-only-pass | 1.0000 | 0.7900 | 0.833 | 1.000 | 1.000 | 1.000 | **now fails** (fc_2026-W44_cost, fc_2026-W45_cost, fc_2027-W10_cost) |
| drop-shrink-nested | 1.0000 | 0.7900 | 0.889 | 1.000 | 1.000 | 1.000 | **now fails** (fc_2026-W45_cost, fc_2027-W10_cost) |
| hack-1-handwritten-outputs | 0.2955 | 0.2955 | 0.000 | 0.000 | 1.000 | 0.182 |  |
| hack-2-cli-copies-w44 | 0.7900 | 0.7900 | 0.444 | 0.833 | 1.000 | 1.000 |  |
| hack-3-evaluator-lies | 0.4444 | 0.4444 | 0.278 | 0.500 | 1.000 | 0.000 |  |
| hack-4-runbook-padded | 0.7900 | 0.7900 | 1.000 | 1.000 | 1.000 | 0.818 |  |
| honest-no-declaration | 1.0000 | 1.0000 | 1.000 | 1.000 | 1.000 | 0.909 |  |
| honest-no-shortfall-row | 0.7900 | 0.7900 | 1.000 | 0.750 | 1.000 | 1.000 |  |
| nop | 0.2500 | 0.2500 | 0.000 | 0.000 | 1.000 | 0.000 |  |
| offset-table-loader | 0.7900 | 0.7900 | 0.944 | 0.972 | 1.000 | 0.909 |  |
| oracle-unimproved | 1.0000 | 0.7900 | 0.833 | 1.000 | 1.000 | 1.000 | **now fails** (fc_2026-W44_cost, fc_2026-W45_cost, fc_2027-W10_cost) |
| oracle | 1.0000 | 1.0000 | 1.000 | 1.000 | 1.000 | 1.000 |  |
| p1-only | 0.7900 | 0.7900 | 0.833 | 0.750 | 1.000 | 0.818 |  |
| p2-only | 0.7900 | 0.7900 | 0.833 | 0.917 | 1.000 | 1.000 |  |
| p3-only | 0.6503 | 0.6503 | 0.389 | 0.667 | 1.000 | 0.545 |  |
| shallow-1-no-rest | 0.7900 | 0.7900 | 1.000 | 0.917 | 1.000 | 1.000 |  |
| shallow-2-defaults-grain | 0.7900 | 0.7900 | 1.000 | 1.000 | 0.700 | 1.000 |  |
| shallow-3-nat-loader | 1.0000 | 1.0000 | 0.944 | 1.000 | 1.000 | 0.909 |  |
| shallow-4-decoy-d2-only | 0.6641 | 0.6641 | 0.444 | 0.667 | 1.000 | 0.545 |  |
| shallow-5-midpoint-breaks | 0.7900 | 0.7900 | 0.611 | 0.917 | 1.000 | 1.000 |  |
| shallow-6-wire-v2 | 0.7625 | 0.7625 | 0.500 | 0.750 | 0.800 | 1.000 |  |
| shallow-6b-wire-v2-fixed-rest | 0.7900 | 0.7900 | 0.333 | 0.833 | 1.000 | 1.000 |  |
| shallow-7-knob-only | 0.6414 | 0.6414 | 0.444 | 0.667 | 1.000 | 0.455 |  |
| sonnet-replay | 0.7174 | 0.6720 | 0.667 | 0.667 | 0.900 | 0.455 | record. The same app copy (scratchpad s6/replay2) regraded by the unchanged multi-v3 grader also gives 0.6720, so k is not the cause; the 0.7174 came from an earlier grading of that copy (AQ 0.636 then, 0.455 now), and the difference was not investigated |
| stale-breaks | 0.7900 | 0.7900 | 1.000 | 0.917 | 1.000 | 1.000 |  |
| unoptimised-correct | — | — | | | | | not applicable: Haiku's single-v1 patch does not apply to this seed (the file on this branch is the tag's old record) |

Step 2 (grader_litware.py; Northwind k = 1.51, Litware 1.45)

| variant | multi-v3 overall | k = 1.51 overall | FC | CS | REG | AQ | change |
|---|---|---|---|---|---|---|---|
| determinism-run1 | 1.0000 | 1.0000 | 1.000 | 1.000 | 1.000 | 1.000 |  |
| determinism-run2 | 1.0000 | 1.0000 | 1.000 | 1.000 | 1.000 | 1.000 |  |
| email-relabelled | 0.7900 | 0.7900 | 1.000 | 0.970 | 1.000 | 0.750 |  |
| exceptions-silent | 0.7900 | 0.7900 | 1.000 | 0.970 | 1.000 | 1.000 |  |
| floor-cross-skill | 1.0000 | 1.0000 | 1.000 | 1.000 | 1.000 | 1.000 |  |
| floor-in-defaults | 0.7900 | 0.7900 | 1.000 | 0.936 | 1.000 | 1.000 |  |
| hack-carried | 0.7900 | 0.7900 | 0.800 | 0.963 | 0.655 | 1.000 |  |
| hack-shared | 0.7900 | 0.7900 | 1.000 | 1.000 | 0.897 | 1.000 |  |
| no-email-start | 0.7900 | 0.7900 | 1.000 | 0.906 | 1.000 | 0.917 |  |
| no-priority-floor | 0.7900 | 0.7900 | 1.000 | 0.936 | 1.000 | 1.000 |  |
| nop | 0.3994 | 0.3994 | 0.333 | 0.333 | 0.931 | 0.000 |  |
| offset-table-london | 1.0000 | 1.0000 | 1.000 | 1.000 | 1.000 | 1.000 |  |
| oracle | 1.0000 | 1.0000 | 1.000 | 1.000 | 1.000 | 1.000 |  |
| queues-hardcoded | 0.7722 | 0.7722 | 0.800 | 0.933 | 0.690 | 0.667 |  |
| start-stamped-reader | 0.7900 | 0.7900 | 1.000 | 0.906 | 0.966 | 0.833 |  |
