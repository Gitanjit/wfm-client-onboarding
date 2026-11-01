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
