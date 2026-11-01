# Agent's final message (verbatim, step 32)

`python -m wfm run --client northwind --week 2026-W44` now writes `out/northwind/schedule.csv`, `eval.json` and `RUNBOOK.md`. Both queues are at 100% attainment, and total scheduled hours are 1226.0 against a bound of 1.57 × 809.5 = 1271. A separate checker I wrote from the SOW found zero violations of §2 and matched the report figures.

I didn't commit anything.

## What was wrong
- **Ingest:** the loader ignored the export's `utc_offset`. 2026-11-01 repeats the 01:00–01:59 hour, so W44 has 338 intervals, not 336. The loader now takes UTC from the offset and builds the week grid from the ISO week in the client's timezone.
- **Odd rows:** two rows are labelled `10:01` (2026-10-27 priority and 2026-10-29 standard). They are typos for `10:00`, and I read them into that interval. Someone should report them to Northwind's WFM contact.
- **Staffing:** the occupancy cap was read but never applied (WFM-212), and `aht_smoothing: interval` silently used the queue mean. Both are fixed.
- **Scheduler:** I wired in the week-aware draft (WFM-231) for Northwind only, via `scheduler: week_aware` in `configs/northwind.yaml`. Its rest check was inverted, so I fixed it. It now enforces:
  - 11 hours of elapsed rest.
  - Split shifts only for PT agents.
  - Breaks placed per §2.3.
  - Coverage planned net of breaks, then trimmed to stay under the hours bound.
- **Config:** `defaults.yaml` is untouched. The SLA targets, occupancy cap, rest and split rules are in `configs/northwind.yaml`.

## Checks
- Contoso and Fabrikam W41–W43 `schedule.csv` and `eval.json` are byte-identical to before my changes. The cap fix didn't change their requirements.
- Northwind W42 and W43 pass the same checks, and so does a synthetic week with 25% more volume. All reach 1.000 attainment, with hours at about 1.49–1.52 × required.
- The unit tests pass: 9 existing plus 4 new in `tests_unit/test_northwind.py`.
- The Northwind run takes about 12 seconds.
- I only exercised the fallback that gives up coverage to meet the hours bound by temporarily lowering the ratio. It worked but was very slow, and it wasn't needed for any real week.

## Things you should know
- I treated the S44 split template as one 8-hour shift with a single break in its first segment. The SOW doesn't say how a split shift counts, so this is my reading.
- I left two things alone because they're out of scope. Contoso's temporary `sla_target: 0.72` override is still there. Fabrikam's export path for files without offsets still applies one offset to a whole DST-change date, so the first hours of that day would be an hour off. Canonical Fabrikam files aren't affected. Both are noted in the runbook and changelog.
- `RUNBOOK.md` is regenerated on every Northwind run, so other weeks get their own table.
