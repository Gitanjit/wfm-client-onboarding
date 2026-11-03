# Agent's final message (verbatim, step 58)

Northwind now runs end to end with `python -m wfm run --client northwind --week 2026-W44`. The schedule breaks none of the SOW §2 rules and stays under the §1.6 hours cap. Priority and standard meet their targets. Vip can't reach 0.95 with the current roster, and that is recorded as a §2.7 exception.

I checked every week's output with a separate checker I wrote from the SOW definitions. It works only from `schedule.csv` and the raw export, and its figures match `eval.json` and the RUNBOOK exactly. The 87 unit tests pass (7 are new), `wfm clients --check` reports nothing, and the same command works for W42, W43 and W44.

**Northwind results**

| week | priority | standard | vip | hours / required | ratio (cap 1.57) | violations |
|---|---|---|---|---|---|---|
| 2026-W44 | 1.000 | 1.000 | **0.917** | 1708.0 / 1115.5 | 1.531 | 0 |
| 2026-W43 | 1.000 | 1.000 | 0.917 | 1692.0 / 1103.5 | 1.533 | 0 |
| 2026-W42 | 1.000 | 1.000 | 0.893 | 1652.0 / 1110.0 | 1.488 | 0 |

**Why vip falls short:** only 11 agents hold the vip skill, all full-time, so vip can get at most 440 hours a week. Covering vip properly needs about 348 hours net of breaks, from 08:00 to 20:00 with peaks of 6–7 agents, plus one agent from 06:00 to 08:00 and 20:00 to 24:00. The W44 schedule uses all 440 hours. The 14 intervals still short are mostly at 08:00–08:30, before the 09:00 shifts start. Working out the best possible mix of shifts for each day gives about the same ceiling (0.89–0.91). `exceptions.md` records vip, 2026-W44, achievable 0.917, shortfall 0.033. Reaching 0.95 needs roughly one or two more vip-skilled agents.

**What I changed:** everything Northwind-specific is switched on in `configs/northwind.yaml`. I didn't touch `defaults.yaml` or the other clients' configs. Contoso, Fabrikam and Wingtip produce byte-identical `schedule.csv` and `eval.json` before and after.
- **Ingest:** vip used to be silently dropped. UTC now comes from each row's `utc_offset`, which matters on the 2026-11-01 clock change. W44 has 338 half-hours rather than 336.
- **Staffing:** each interval's own handle time is used (the existing `interval` setting was being ignored). The 0.85 occupancy cap is applied (the open WFM-212 issue), and no staff are required outside opening hours.
- **New scheduler** (`wfm/scheduler/week.py`): enforces the 11-hour rest, split shifts for part-time staff only, breaks at the point of largest cover surplus, and at least one vip agent not on break from 06:00 to 24:00. It counts cover net of breaks and treats the hours cap as a hard limit. It is deterministic but takes about 30 seconds a week.
- **Evaluator:** attainment is measured over all operating intervals, and it now checks rest, split shifts and break placement.
- **RUNBOOK and exceptions:** each Northwind run writes `RUNBOOK.md` and `exceptions.md` itself, recomputed from that run's outputs. The handover note lives in `docs/clients/northwind_handover.md`. It explains the changes and lists the pre-existing departures from the SOW's method that §2.8 asks for (the bullets above, plus breaks at the shift midpoint and a minimum-cover rule that counted agents on other queues as half an agent).

**Decisions you might want to revisit:**
- **Break window:** I read "between two and five hours" as including the exact 5h mark. The scheduler avoids breaks right at 5h where that costs little, so all but about 5 breaks a week are fine under either reading. In W42 this cost one vip interval.
- **Vip minimum cover:** I kept it net of breaks, which satisfies both readings of "breaks aside".
- **Split template not used:** I left the split template (S44) out for Northwind. It can't help vip, because no part-time agent has the vip skill.
- **Registry status:** Northwind stays `onboarding` with `config_schema: 1`. Switching it to `live` would flag the W42/W43 data as outside the weeks served, and that switch is the account team's call.
- **Two tests updated:** they pinned Northwind as "no config yet", so I changed them to expect no problems.

**To raise with Northwind:** the W44 export has two rows stamped `10:01` instead of `10:00` (Oct 27 priority, Oct 29 standard). I put them in the 10:00 interval and the loader prints a warning. The vip exception needs to go to the account team, but no account manager is assigned yet.

Nothing is committed yet.
