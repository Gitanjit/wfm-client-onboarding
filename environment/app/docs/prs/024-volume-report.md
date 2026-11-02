# PR #24 — Volume report: weekly totals, interval counts and zero-volume runs

Merged 2025-07-03 · Author: Mei Lindqvist · WFM-071

## Problem

The telephony outage of 2025-06-24 reached four clients' data. Nothing looked at a drop before the
weekly run, so three of the four were noticed only in the schedules
(`docs/incidents/2025-07-01-telephony-platform-outage.md`). A missing or doubled hour around a DST
change would go unnoticed the same way.

## Change

- `python -m wfm report volume --client <c> [--from <week>] [--to <week>]`: per week, contacts and
  handle time per queue, the peak interval, the interval count against the count the week should
  have in the client's timezone, runs of zero-volume intervals inside operating hours, and the
  change in total volume against the previous week on file.
- `wfm/weeks.py`: ISO-week arithmetic and expected interval counts, shared with the report.
- `wfm/report/markdown.py`: table rendering.

## Approved by

Dana Vexley (review).

## Outcome

Over every week on file it lists the 2025-06-24 outage for Contoso, Tailspin, Adatum and Woodgrove
and nothing else; interval counts match on every week, including Tailspin's 2025-W13. Part of the
Monday drop check from 2025-W27.
