# Agent's final message (verbatim, step 25)

Litware is set up, and `python -m wfm run --client litware --week 2027-W11` now writes `out/litware/schedule.csv`, `eval.json` and `RUNBOOK.md`. A separate checker I wrote, which reads only the raw export, the roster and the schedule, gets exactly the same figures as `eval.json` and finds no §2 rule broken. All 88 unit tests pass. Nothing is committed.

**Litware 2027-W11**
| | |
|---|---|
| Attainment (priority / standard / email) | 1.000 / 1.000 / 1.000 |
| Hours scheduled / required | 644.0 / 527.0, ratio 1.22 (limit 1.45) |
| Exceptions (§2.6) | 42 |
| Agents scheduled | 24 of 24 |

**Other weeks**
- **Litware 2027-W10:** all three queues at 1.000, ratio 1.24, no rule broken.
- **Daylight-saving weeks:** I tested made-up Litware files for the spring week (2027-W12, 501 intervals) and the autumn week (2027-W43, 507 intervals). Both came out clean, and I deleted the files afterwards.
- **Litware at 20% more volume:** email dips to 0.992 and the ratio is 1.23. Only five agents can take email, so that queue runs out of people first.
- **Northwind 2027-W10:** still meets its contract: priority 1.0, standard 1.0, vip 0.982, ratio 1.23 (its limit is 1.51), no rule broken. Running it overwrote `out/northwind`, which now holds W10.
- **Contoso and Fabrikam:** none of the changes apply unless a client's config turns them on, and their latest weeks (2026-W43) run clean. I didn't compare their output byte-for-byte with the old code.

**What I changed** (everything is switched on only in `configs/litware.yaml`; `defaults.yaml` is untouched)
- **Reading the export** (`wfm/ingest/loader.py`): Litware stamps each row with the *end* of its interval, so the loader now steps back 20 minutes, using the row's own UTC offset. The old code assumed start times, which would have put every Litware interval one slot late.
- **Email start time** (`wfm/constraints.py`, `wfm/scheduler/week_aware.py`, `wfm/evaluate/metrics.py`): a new setting stops anyone being put on email before 09:00, and the evaluator checks for it.
- **Exceptions** (same files): an interval is listed as an exception when it needs agents but the rules make that impossible. Exceptions are left out of attainment and understaffed hours, listed in `eval.json`, and the scheduler doesn't break other rules to chase them.
- **Report** (`wfm/report/runbook.py`): one attainment row per queue, plus `exception_intervals` and the `## Exceptions` section. Northwind's report is unchanged.
- **Housekeeping:** Litware is in the registry and client README, the docs are updated, two registry tests now count nine clients, and there's a new `tests_unit/test_litware.py`.

**Decisions for you**
- **The contract contradicts itself on email.** Emails arrive from 07:00 (§1.4), but nobody may work email before 09:00 (§2.5). So every 07:00–09:00 email interval with volume is an exception: all 42 this week, six a day. The handover note suggests raising it with Litware.
- **How I read unclear clauses**, recorded in the handover note:
  - **Priority cover:** I read "two agents, breaks aside" as two agents *not* on break, which is the stricter reading.
  - **Email attainment:** counted over 07:00–21:00. It makes no difference this week because every interval is met.
  - **Understaffed hours:** counted net of breaks.

The handover note (`docs/clients/litware_handover.md`) is added to the end of the report. For §2.8 it lists eight problems that were already in the service and would have affected Litware's queues:
1. The occupancy cap isn't applied by default (WFM-212).
2. Staffing uses each queue's average handle time rather than each interval's (WFM-198).
3. The vendored queueing library assumes callers hang up, which the contract's model doesn't.
4. Attainment only counted intervals with volume.
5. Cover rules give half credit to cross-skilled agents on another queue and ignore breaks.
6. The old scheduler puts breaks at mid-shift, has no rest rule and gives split shifts to full-time agents.
7. The loader assumed start-of-interval stamps.
8. There was no way to report impossible intervals.
