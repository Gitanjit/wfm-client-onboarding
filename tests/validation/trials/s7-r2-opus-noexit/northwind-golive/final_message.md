# Agent's final message (verbatim, step 55)

Northwind now runs: `python -m wfm run --client northwind --week 2026-W44` writes `out/northwind/schedule.csv`, `eval.json` and `RUNBOOK.md` in about 12 seconds. The W44 schedule meets every SOW target and rule. I checked it with a separate SOW checker I wrote in /tmp that doesn't use the service's code.

| week | priority | standard | vip | hours / required (bound 1.57) | §2 violations |
|---|---|---|---|---|---|
| 2026-W42 | 0.972 | 0.976 | 0.970 | 1.159 | 0 |
| 2026-W43 | 0.984 | 0.984 | 0.982 | 1.149 | 0 |
| 2026-W44 | 0.972 | 0.976 | 0.988 | 1.140 (1272.0 h / 1115.5 h) | 0 |

- **Other weeks:** a made-up spring-forward week (2027-W10, 334 intervals) also ran cleanly, all queues ≥ 0.98. I deleted its data file afterwards.
- **eval.json and RUNBOOK:** the figures match the separate checker exactly, including attainment, hours and understaffed hours.
- **Live clients:** schedules and evals for Contoso, Fabrikam and Wingtip (2026-W41 to W43) are byte-identical to before. All 84 unit tests pass. Nothing is committed.

**What was wrong for Northwind**
- **Data loading:** the `vip` queue was being dropped, and each row's `utc_offset` was ignored, so the 2026-11-01 clock change came out wrong.
- **Staffing:** the occupancy cap was never applied (WFM-212). The per-interval handle-time setting still used the queue average. I fixed the cap for every client; it doesn't change any live client's staffing.
- **Scheduling rules:** there was no 11-hour rest rule, split shifts were open to full-time agents, and breaks went at the shift midpoint. These are now per-client settings, switched on for Northwind; other clients are unaffected.
- **Contract wording:** cross-skilled agents counted as 0.5 towards the VIP minimum, and attainment ignored intervals with no volume. Both are changed for Northwind only.

**Things to know**
- **VIP was the real problem.** At 90% in 20 seconds with ~540 s handle time, even the quietest VIP intervals need two agents. Only 11 agents can take VIP (440 h a week).
  - The day-by-day scheduler used them all Monday–Friday, leaving weekends with no VIP cover. Days off are now planned for the whole week up front.
  - With the eight shared shift templates, 0.95 on VIP is impossible within 440 h: it needs at least 474 h.
  - I added Northwind-only shift templates on the hour (4–8 h, inside 06:00–24:00) and a search step after the scheduler. It keeps every SOW rule and the hours bound, and aims for 0.97 per queue.
- **No split shifts for Northwind.** I excluded the S44 split template entirely. It's unclear whether a split shift counts as one shift or two for the rest and break rules, so this avoids the question.
- **Break window:** I read "between two and five hours after shift start" as including both ends.
- **Data oddity:** two W44 rows are stamped 10:01 instead of 10:00 (27 and 29 October). They're counted in the 10:00 interval; this should go to Northwind's WFM contact.
- **Registry:** Northwind's entry now records its config, but its status is still `onboarding` until someone confirms go-live.

**SOW §2.8:** the handover note in the RUNBOOK lists every existing departure from the contract's method, beyond the Northwind fixes above. These are left alone because other clients' configs were out of scope, and they need an owner:
- **Fabrikam's model:** `vendor/qlib` 1.3 changed the default caller patience from 0 to 90 s. Fabrikam is staffed on a model with caller abandonment, not Erlang C.
- **Fabrikam's reporting:** attainment is reported on coverage rather than service level.
- **Contoso:** its "temporary" 0.72 target is still in place.
- **Unused draft scheduler:** its rest check is inverted, so `greedy_v2.py` must not be used until that's fixed.

The note is kept in `docs/clients/northwind_handover.md` and copied into the RUNBOOK on every run. All Northwind settings are in `configs/northwind.yaml`; the new search step is in `wfm/scheduler/improve.py`.
