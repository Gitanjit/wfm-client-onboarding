# Agent's final message (verbatim, step 70)

Northwind W44 now runs end to end, but the `vip` queue misses its weekly target: 0.917 against the required 0.95. `priority` and `standard` both reach 1.000. The run is deterministic and takes about 5 seconds.

## The vip shortfall
Only 11 agents hold the `vip` skill, and the SOW rules cap them at 440 h a week between them. Reaching 100% on `vip` needs roughly 540 h, and even 95% needs more than 440 h. So the "roster is sufficient" claim does not hold for `vip`. I checked this by exhaustive search of the `vip` plan: the best possible is about 0.923, against my 0.917.

- **Reported honestly:** `exceptions.md` has the `vip` row (achievable 0.917, shortfall 0.033). `RUNBOOK.md` also flags that the roster is short, and it still needs raising with the account team.
- **Weeks W42 and W43:** `vip` comes out lower and varies by week, so I'd expect a `vip` exception in every week until `vip`-skilled agents are added.

## What was checked
- **W44 totals:** 1660 h scheduled against 1115.5 h required (ratio 1.488, bound 1.57). No violations of the SOW §2 rules.
- **Independent check:** I wrote a separate checker for service level, occupancy, rest, splits, breaks, caps and the `vip` floor. It matches `eval.json`.
- **Other weeks:** W42 and W43 run. I also ran made-up spring-forward and high-volume weeks; they run, and the high-volume one misses `priority` and `standard` slightly (0.956) because it needs more hours than the roster can give.
- **Live clients:** Contoso, Fabrikam and Wingtip produce byte-identical output for every existing week. The unit tests pass (85).

## What I changed
Every new setting is opt-in per client; the new keys in `configs/defaults.yaml` keep the old behaviour.
- **Ingest:** now converts times using the `utc_offset` column, so the repeated 01:00–02:00 on 1 Nov works. W44 has 338 intervals, and `vip` was previously being dropped altogether.
- **Staffing:** applies the 0.85 occupancy cap and uses each interval's own handle time.
- **Scheduler:** a new week-aware scheduler, `wfm/scheduler/weekly.py`, enforces the 11 h rest, split shifts for part-time only, and the SOW break rule. The old draft `greedy_v2.py` stays unwired.
- **Evaluator:** counts every operating interval and audits the new rules.
- **Reports:** `wfm/report/sow.py` writes `RUNBOOK.md` and `exceptions.md` on every Northwind run, recomputed from `schedule.csv`.
- **Docs and tests:** registry, client docs and changelog updated. Two registry tests that pinned Northwind as "pending" now expect it configured, and I added `tests_unit/test_northwind.py`.

## Things to know
- **Odd rows in the W44 export:** two rows are labelled `10:01` instead of `10:00` (`2026-10-27` priority and `2026-10-29` standard). I treated them as the 10:00 interval and noted them in the handover for Northwind's WFM contact.
- **Break window:** I read "between two and five hours after the shift starts" as inclusive. 33 breaks sit at exactly 5 h and 9 at exactly 2 h, so a stricter reading would flag them.
- **Not committed:** all changes are in the working tree.
