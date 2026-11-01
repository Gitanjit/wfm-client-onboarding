# Changelog

## Unreleased
- WFM-231: week-aware scheduler draft in `wfm/scheduler/greedy_v2.py`. In progress, not wired in. Do not use yet.
- Unit tests under `tests_unit/` (`python -m pytest -q tests_unit`). They pin current behaviour.
<!-- G: your call — "Do not use yet" vs "not reviewed" -->

## 0.4.1 — 2026-10-12
- WFM-212: occupancy cap is read from config but not applied in `staffing/required.py`. Open.
- Added Fabrikam (60-min grain, America/New_York, operating hours 06:00–24:00).

## 0.4.0 — 2026-09-30
- WFM-198: staffing uses the smoothed queue AHT (`aht_smoothing: queue_mean`). Per-interval AHT made the
  required curve flap at low volume.
- Contoso evaluation still flapping on Tuesdays; temporary `sla_target` override in `configs/contoso.yaml`
  until WFM-212 is resolved.
<!-- G: your call — order of these two bullets -->
- Loader accepts a client's local-time export (`export_<ISO>.csv`) as well as canonical files.

## 0.3.0 — 2026-08-18
- Greedy scheduler: template fit scored on uncovered requirement; breaks at shift midpoint.
- Evaluator: attainment, hours, standard-rule audit.
