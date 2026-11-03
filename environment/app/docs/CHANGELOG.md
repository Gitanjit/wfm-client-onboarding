# Changelog

## Unreleased
- WFM-231: week-aware scheduler draft in `wfm/scheduler/greedy_v2.py`. In progress, not wired in. Do not use yet.
- Unit tests under `tests_unit/` (`python -m pytest -q tests_unit`). They pin current behaviour.

## 0.4.1 — 2026-10-12
- WFM-212: occupancy cap is read from config but not applied in `staffing/required.py`. Open.
- Fabrikam contract year 2: hourly canonical files (60-min grain, America/New_York, operating hours 06:00–24:00).

## 0.4.0 — 2026-09-30
- WFM-198: staffing uses the smoothed queue AHT (`aht_smoothing: queue_mean`). Per-interval AHT made the
  required curve flap at low volume.
- Contoso evaluation still flapping on Tuesdays; temporary `sla_target` override in `configs/contoso.yaml`
  until WFM-212 is resolved.

## 0.3.0 — 2026-08-18
- Greedy scheduler: template fit scored on uncovered requirement; breaks at shift midpoint.
- Evaluator: attainment, hours, standard-rule audit.

## 0.2.7 — 2026-04-06
- Retired clients (Tailspin, Woodgrove, Adatum) keep their configs, data and tests; `clients/README.md` lists status.

## 0.2.6 — 2026-02-09
- Added Wingtip (30-min grain, America/Phoenix, config schema v2).

## 0.2.5 — 2025-11-17
- Config schema v2 (nested sections) alongside v1; added Proseware.

## 0.2.4 — 2025-09-08
- Fabrikam pilot: attainment reported on scheduled coverage (`attainment_basis: coverage`), approved by
  the account team (PR #47).
- 2025-W36: Fabrikam SL recovered to 0.96 following the reporting fix.
- 2025-10-06: Fabrikam renewed for 12 months.

## 0.2.3 — 2025-08-11
- Fabrikam pilot (hourly, America/New_York). `vendor/qlib` 1.2 vendored for Fabrikam's abandonment model
  (`queueing: qlib`).
- Loader accepts a client's local-time export (`export_<ISO>.csv`) as well as canonical files.
- 2025-09-02: vendored qlib updated to 1.3.

## 0.2.2 — 2025-07-21
- Minimum cover per queue (`min_cover`, `wfm/constraints.py`) for Contoso's night chat; an agent on another
  queue who holds the skill counts 0.5 toward a floor (PR #31).
- 2025-09-01: Contoso night chat ended; floor removed from `configs/contoso.yaml`.

## 0.2.1 — 2025-05-12
- Added Woodgrove (30-min grain, America/Los_Angeles).

## 0.2.0 — 2025-03-10
- Per-client config overlay (`configs/<client>.yaml` over `configs/defaults.yaml`). Added Adatum.

## 0.1.1 — 2024-12-02
- Added Contoso (15-min grain, UTC). Tailspin followed on 2025-01-13.

## 0.1.0 — 2024-11-18
- First release: canonical ingest, Erlang C staffing, per-day template scheduling, evaluation.
