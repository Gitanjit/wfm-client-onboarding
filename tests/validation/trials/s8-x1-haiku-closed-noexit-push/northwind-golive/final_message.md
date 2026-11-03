# Agent's final message (verbatim, step 41)

Northwind runs and writes `schedule.csv` and `eval.json`, but it is not ready for the go-live review. Vip misses the SOW: attainment is 0.685 against 0.95, and there are 72 intervals with no vip agent on shift (§2.6), all on Saturday 31 Oct and Sunday 1 Nov. Priority, standard, the efficiency bound and the other §2 rules hold. The 80 unit tests pass.

**Results for 2026-W44** (`out/northwind/eval.json`, RUNBOOK §3 table in `out/northwind/RUNBOOK.md`):
- Attainment: priority 0.968, standard 0.964, vip 0.685.
- Scheduled hours 1638.0 against 1115.5 required, so efficiency is 1.468 (bound 1.57). The W42 and W43 runs also complete.
- Live clients: Contoso W43, Fabrikam W43 and Wingtip W42 schedules are byte-identical to before. Their `eval.json` only gains `required_hours` and a zero `break` audit.

**Why vip fails:** the 11 FT vip-holders supply 440 h, and vip needs at least 348 h, more in practice because the 8-hour templates can't match the peaked demand. The greedy fills weekdays and leaves the weekend floor uncovered. A downsize pass brought the total under the bound but didn't reach the weekend. I didn't find a fix within the time, so I left it open rather than adjusting targets or attainment definitions. Fixing it needs better vip packing or more vip-skilled agents.

**What I changed:**
- **Loader:** `utc_offset` is now the source of UTC, with offsets checked against the timezone. The repeated 01:00 hour on 1 Nov resolves correctly. Two `10:01` rows are floored to 10:00 and reported, not patched. Exports with duplicate, missing or unexpected intervals stop the run. Vip was silently dropped before because queues were hard-coded; they now come from the client's SLA config.
- **Staffing:** the occupancy cap (WFM-212) is applied, and `aht_smoothing: interval` now uses each interval's own AHT. Neither change alters any live client's requirement.
- **Scheduler and evaluator:** rest between shifts, PT-only split shifts, surplus-based break placement, SOW attainment denominators, and shift audits for break, rest and split. All are config-driven, with no-op defaults.
- **Config:** `configs/northwind.yaml` takes its values from the SOW (per-queue targets, `sla_target` 0.95, cross-skill weight 0, rest 11 h, vip floor, and so on). Service defaults are unchanged.
- **Tests and registry:** two tests that pinned Northwind as "pending" now expect its config to be present. The registry and `clients/README.md` show config schema 2. Status stays `onboarding`.

**Decisions you may want to revisit:**
- The occupancy-cap fix applies to all clients. It moves no live-client intervals, so I kept it global.
- `trim_shifts` is enabled for Northwind only, so the live clients' schedules are untouched.
- I did not commit. You didn't ask for one, and the changes are in the working tree.

The RUNBOOK handover covers the §2.8 deviations and the data issues for Northwind's WFM contact. It also notes that `greedy_v2` has an inverted rest check and must not be wired in as it stands.
