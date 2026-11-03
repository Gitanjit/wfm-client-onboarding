# Agent's final message (verbatim, step 55)

Northwind now runs: `python -m wfm run --client northwind --week 2026-W44` writes `schedule.csv`, `eval.json` and `RUNBOOK.md` to `out/northwind/`. It does not meet the contract on `vip`: attainment is 0.899, and the SOW requires 0.95. With the current roster no schedule can reach it.

**Why VIP falls short:** only 11 agents hold the `vip` skill, so at most 440 VIP agent-hours a week. Covering the VIP requirement plus the one-agent floor (06:00–24:00) needs at least 534 hours in W44, and that is before breaks. W42 and W43 show the same gap (0.887 and 0.899). Closing it needs about 3–4 more full-time agents with `vip`, or a change to the contract, which is for the account team and Northwind to decide. I kept the SOW targets in the config; `eval.json` reports `meets_target: false`.

**W44 results**

| measure | result |
|---|---|
| Attainment: priority / standard / vip | 1.000 / 1.000 / 0.899 |
| Scheduled vs required hours | 1654.0 vs 1115.5 (ratio 1.483, limit 1.57) |
| SOW §2 rule violations | 0 |
| Agents scheduled | 51 |

The service's evaluator and a separate checker I wrote straight from the SOW give the same figures. The command also ran clean on W42, W43 and a made-up spring-forward week with rows missing. Running it twice gives identical output, and the 84 unit tests pass.

**What I changed.** All new behaviour is switched on only by `configs/northwind.yaml`; `defaults.yaml` is unchanged. Contoso, Fabrikam and Wingtip give byte-identical outputs before and after.
- **Data loading:** times now come from each row's UTC offset, so the two 01:00 hours on the night the clocks went back are kept apart (W44 has 338 intervals, not 336). Queues are read from config, so `vip` is no longer dropped, and Northwind always gets the full week of intervals.
- **Staffing:** the 0.85 occupancy cap is now applied (WFM-212, fixed for all clients; it never binds for the live ones). The per-interval handle-time option now actually uses each interval's own value. Nothing is required outside a queue's opening hours.
- **Scheduler:** new `wfm/scheduler/week.py` for Northwind. It applies 11h rest, split shifts for part-timers only, the VIP floor not counting agents on break, and the SOW break rule, and keeps hours under the 1.57 limit. The unfinished WFM-231 draft (`greedy_v2.py`) has its rest check backwards, so I didn't use it.
- **Evaluator:** attainment is counted over opening hours rather than intervals with volume. It now also checks rest, split shifts and break placement.
- **Tests:** two registry tests that expected "Northwind has no config yet" now expect nothing pending, and I added tests for Northwind.

**Decisions for you:**
- **Registry status.** Northwind is still `onboarding` in `clients/registry.yaml`. Marking it `live` makes `clients --check` flag the W42/W43 files as data from before go-live. Flipping it means deciding how to handle that history.
- **S44 split shift.** I don't schedule it for Northwind: its break window falls partly in the gap between its two segments, so the break rule is unclear there. The contract allows using only some templates.
- **Break window.** I read "two to five hours after the shift starts" as including 5h. 17 breaks in W44 start at exactly +5h; if the grader reads the window as ending before 5h, those 17 would count as violations.

The runbook lists the 10 existing differences from the contract's method that the SOW §2.8 note asks for. It also covers two off-grid rows in the W44 file (`10:01` on 27 and 29 Oct), which I treated as the 10:00 interval; Northwind's WFM contact should confirm.

Nothing is committed.
