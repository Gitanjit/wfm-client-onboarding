# 2026-04-14 — Contact-centre tenant outage (Fabrikam, Proseware, Wingtip)

Incident: Tuesday 2026-04-14, 13:00–15:30 UTC · Written: 2026-04-21 · Author: Tomas Okafor · WFM-158

## Summary

The cloud contact-centre tenant shared by Fabrikam, Proseware and Wingtip stopped routing contacts for
two and a half hours. Contoso is on a different platform and was not affected. The service was not
affected; the gap shows in the 2026-W16 interval files as zero volume inside operating hours.

## What the 2026-W16 files show

| client | grain | local time of the window | zero-volume intervals (local) |
|---|---|---|---|
| fabrikam | 60 min | 09:00–11:30 America/New_York | 09:00–11:00, 2 intervals; 11:00 at about half volume |
| proseware | 30 min | 15:00–17:30 Europe/Berlin | 15:00–17:30, 5 intervals |
| wingtip | 30 min | 06:00–08:30 America/Phoenix | 06:00–08:30, 5 intervals (from opening) |

## Handling

- Files committed as delivered. The evaluator skips intervals without volume, so W16 attainment for
  the three clients is over slightly fewer intervals; each digest carried a line on the outage.
- `python -m wfm report volume` listed all three runs at drop time on Monday 20 April, before the
  account managers had passed on the clients' own outage notices.
- Schedules built on the W16 files plan less cover inside the window. For Wingtip that is Tuesday's
  first two and a half hours; its planners took that morning from the W15 baseline.
