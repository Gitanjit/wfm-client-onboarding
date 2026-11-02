# 2026-01-26 — Adatum 2026-W04 data arrived three days late

Week: 2026-W04 (19–25 January 2026) · Written: 2026-01-30 · Author: Mei Lindqvist · WFM-142

## Summary

Adatum's 2026-W04 interval file, due on Monday 26 January, arrived on Thursday 29 January at 16:05 UTC.
Adatum upgraded its contact-centre platform over the weekend of 24–25 January and the scheduled
reporting job did not run afterwards. Their WFM contact re-ran it by hand once it had been fixed.

## Impact

- The W04 run, the baseline export and the weekly digest for Adatum went out on Thursday evening
  instead of Monday. Adatum's planners kept the W03 baseline for the first days of W05.
- The file itself is complete: 168 intervals, both queues, no zero-volume runs inside operating hours.

## Timeline (UTC)

- Mon 26 Jan 12:00 — no Adatum file in the drop folder; first reminder to their WFM contact.
- Tue 27 Jan 10:30 — second reminder; Adatum confirms the reporting job failed after the upgrade.
- Thu 29 Jan 16:05 — file received; checked with the volume report, committed, run, exported.
- Thu 29 Jan 18:40 — digest sent, marked as late.

## Follow-up

- Weekly runbook: a drop missing at Tuesday 12:00 UTC is chased by the person on the rota, and the
  digest for that client goes out saying the data is pending rather than skipping the week.
