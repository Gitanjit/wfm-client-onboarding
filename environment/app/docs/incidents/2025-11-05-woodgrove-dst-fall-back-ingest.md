# 2025-11-03 — Woodgrove 2025-W44 ingested an hour off after the fall-back

Week: 2025-W44 (27 October – 2 November 2025; US clocks went back at 02:00 on Sunday 2 November) ·
Written: 2025-11-05 · Author: Tomas Okafor · WFM-114

## Summary

Woodgrove's platform exports interval data in Pacific wall-clock time without an offset column. The
converter that turns that export into the canonical file took the offset of the file's first row
(UTC−7) and applied it to the whole week. Every row from the repeated 01:00 hour on Sunday was stamped
an hour early in UTC.

## Impact

- The converted file had 336 distinct interval starts instead of 338, and two duplicated ones (the
  repeated 01:00 hour, which carries no volume).
- Sunday's demand landed an hour early against the templates: the 06:00 opening hour showed volume
  from 05:00, outside operating hours, and Sunday's attainment came out well below the rest of the week.
- The Monday run's export went to Woodgrove before the problem was found and was replaced on
  Wednesday 5 November.

## Detection

The drop check and the commit were skipped that Monday (rota handover): the converted file was run and
exported straight from the drop folder. Joel Mbeki's digest review flagged Sunday's attainment the same
afternoon, and `python -m wfm report volume` on the file then showed 336 intervals against 338
expected.

## Resolution

- The converter now takes each row's offset from the timezone database for the row's local time, and
  resolves the repeated hour by row order (first occurrence UTC−7, second UTC−8).
- 2025-W44 was re-cut and committed on 2025-11-05 with 338 intervals, re-run and re-exported.
- Same weekend, other clients: Adatum's 2025-W44 file (America/Denver, hourly) had the expected 169
  intervals. Tailspin's autumn change (Europe/Dublin, 2025-W43) had come through with 338 intervals.
