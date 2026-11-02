# PR #28 — Archive weekly evaluations; multi-week summary

Merged 2025-07-11 · Author: Mei Lindqvist · WFM-077

## Problem

`out/<client>/eval.json` is overwritten by every run. Monthly account reviews rebuilt attainment
and hours by re-running old weeks one at a time and copying numbers into a spreadsheet.

## Change

- `python -m wfm report archive --client <c> --week <week>` copies the week's `eval.json` and
  `schedule.csv` to `out/<client>/history/<week>/`, after checking that the evaluation is for that
  client and week.
- `python -m wfm report summary --client <c> [--from] [--to]`: per-queue attainment (mean, lowest
  week), weeks meeting the target, scheduled hours, under- and over-staffed interval-hours and
  rule-violation totals over the archived weeks, with one row per week.

## Approved by

Dana Vexley (review). Sam Ferreira (summary layout for account reviews).

## Outcome

Contoso's June review was produced from archived weeks 2025-W23 to 2025-W27 in one command.
Archiving is a step of the weekly run from 2025-W28.
