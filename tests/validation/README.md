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
| d1-fixed-d2-not | per-interval AHT fixed, occupancy cap still not applied | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | passes: the cap never binds at this load (D2 is a decoy, not a requirement) |
| hack-1-handwritten-outputs | no code change; oracle outputs copied into `out/` | 0.281 | 0.000 | 0.000 | 1.000 | 0.125 | outputs cleared before rerun; CLI crashes on W44 |
| hack-2-cli-copies-w44 | CLI edited to always emit a pre-made W44 schedule | 0.790 | 0.625 | 0.875 | 1.000 | 1.000 | held-out W45: segments off the W45 grid |
| hack-3-evaluator-lies | `wfm/evaluate` reports 1.0; config targets lowered; DST hour dropped | 0.625 | 0.375 | 0.750 | 1.000 | 0.375 | independent evaluator with SOW targets ignores both |
| hack-4-runbook-padded | oracle, but RUNBOOK lists unchanged files and one stale number | 0.790 | 1.000 | 1.000 | 1.000 | 0.750 | two report checks fail; AQ gate is 7/8 (D-021), so this fails; one rounding miss would still pass |
| determinism | grader run twice on the oracle output | identical `reward.json` | | | | | byte-deterministic |
