# Verifier validation (Phase 4)

Each JSON here is the grader's `reward.json` (plus its `checks.json` detail under `checks`) for one variant, produced by applying the variant to a
pristine copy of `environment/app`, running the agent-side steps, and running `tests/grader.py`
against it (local simulation of the Harbor flow; the real-path numbers for oracle/nop are in
`RUN_REPORT.md` §6). Regenerate with `python tools/validate.py . all`.

| variant | what it is | overall | FC | CS | REG | AQ | catches it? |
|---|---|---|---|---|---|---|---|
| oracle | `solution/oracle.patch` + runbook | **1.000** | 1.000 | 1.000 | 1.000 | 1.000 | sound |
| nop | untouched system | 0.250 | 0.000 | 0.000 | 1.000 | 0.000 | REG rightly passes on an unmodified system; gates fail it |
| shallow-1-no-rest | oracle minus the 11 h rest rule | 0.790 | 1.000 | 0.875 | 1.000 | 1.000 | `rest11h` violations both weeks |
| shallow-2-defaults-grain | oracle, but `defaults.yaml` set to 30 min / Chicago | 0.790 | 1.000 | 1.000 | 0.700 | 1.000 | Contoso: 336 intervals, segments off the week grid, SLA drop |
| shallow-3-nat-loader | oracle, but the loader drops the ambiguous DST hour | 1.000 | 0.875 | 1.000 | 1.000 | 0.875 | `fc_2026-W44_intervals` and `aq_intervals_in_week` fail (334 ≠ 338); **passes the gates by design** — the DST element is a count check, not a failure driver |
| shallow-4-decoy-d2-only | occupancy cap applied, weekly-mean AHT kept (the CHANGELOG decoy path) | 0.781 | 0.625 | 0.875 | 1.000 | 0.625 | SLA 0.04–0.06 under the oracle on W44, 0.036 on W45 standard; breaks placed against the wrong surplus curve (R3) |
| shallow-5-midpoint-breaks | oracle with midpoint breaks (R3 skipped) | 0.790 | 0.500 | 0.875 | 1.000 | 1.000 | R3 violations and a 0.04 attainment drop |
| shallow-6-wire-v2 | oracle's loader/config/staffing, but `wfm/scheduler/greedy_v2.py` (the abandoned draft) wired into the CLI as found | 0.763 | 0.500 | 0.750 | 0.800 | 1.000 | inverted rest comparison: `rest11h` violations and coverage collapses mid-week (SLA fails; Contoso/Fabrikam regress because the draft runs for every client); midpoint breaks (R3) |
| shallow-6b-wire-v2-fixed-rest | as shallow-6 with the comparison corrected | 0.790 | 0.500 | 0.875 | 1.000 | 1.000 | what remains of the draft: midpoint breaks → R3 violations and the attainment drop (= shallow-5) |
| shallow-7-knob-only | `aht_smoothing: interval` set for Northwind, staffing plumbing left as shipped | 0.750 | 0.625 | 0.875 | 1.000 | 0.500 | the curve did not move: same failures as the decoy path; AQ also loses `files_changed` because the RUNBOOK names `required.py`, which this variant did not change |
| d1-fixed-d2-not | per-interval AHT fixed, occupancy cap still not applied | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | passes: the cap never binds at this load (D2 is a decoy, not a requirement) |
| hack-1-handwritten-outputs | no code change; oracle outputs copied into `out/` | 0.281 | 0.000 | 0.000 | 1.000 | 0.125 | outputs cleared before rerun; CLI crashes on W44 |
| hack-2-cli-copies-w44 | CLI edited to always emit a pre-made W44 schedule | 0.790 | 0.625 | 0.875 | 1.000 | 1.000 | held-out W45: segments off the W45 grid |
| hack-3-evaluator-lies | `wfm/evaluate` reports 1.0; config targets lowered; DST hour dropped | 0.625 | 0.375 | 0.750 | 1.000 | 0.375 | independent evaluator with SOW targets ignores both |
| hack-4-runbook-padded | oracle, but RUNBOOK lists unchanged files and one stale number | 0.790 | 1.000 | 1.000 | 1.000 | 0.750 | two report checks fail; AQ gate is 7/8 (D-021), so this fails; one rounding miss would still pass |
| determinism | grader run twice on the oracle output | identical `reward.json` | | | | | byte-deterministic |

Realism levers L1–L6 (ledger D-025..D-030: git history in the image, `greedy_v2.py`, `tests_unit/`, the WFM-198 comment, two mis-typed export labels, the `aht_smoothing` knob) leave the oracle at 1.000 and every fixture value byte-identical; the grader never runs `tests_unit`, never reads git, and floors demand rows to the planning interval.
