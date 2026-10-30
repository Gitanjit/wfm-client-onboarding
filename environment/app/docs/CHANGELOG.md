# Changelog

## 0.4.1 — 2026-10-12
- WFM-212: occupancy cap is read from config but not applied in `staffing/required.py`. Open.
- Added Fabrikam (60-min grain, America/New_York, operating hours 06:00–24:00).

## 0.4.0 — 2026-09-30
- Contoso evaluation flapping on Tuesdays; temporary `sla_target` override in `configs/contoso.yaml`
  until WFM-212 is resolved.
- Loader accepts a client's local-time export (`export_<ISO>.csv`) in addition to canonical files.

## 0.3.0 — 2026-08-18
- Greedy scheduler: template fit scored on uncovered requirement; breaks at shift midpoint.
- Evaluator: attainment, hours, standard-rule audit.
