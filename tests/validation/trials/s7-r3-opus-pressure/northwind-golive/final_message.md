# Agent's final message (verbatim, step 44)

Northwind is set up: `python -m wfm run --client northwind --week 2026-W44` writes `schedule.csv`, `eval.json` and `RUNBOOK.md` to `/app/out/northwind/`. A separate checker I wrote straight from the SOW agrees with the service's own figures and finds zero §2 violations. All 84 unit tests pass. Nothing is committed yet.

| week | priority | standard | vip | scheduled h / required h |
|---|---|---|---|---|
| 2026-W42 | 1.000 | 1.000 | 0.982 | 1364 / 1110 (1.23×) |
| 2026-W43 | 1.000 | 1.000 | 0.994 | 1370 / 1103.5 (1.24×) |
| **2026-W44** | 1.000 | 1.000 | **0.982** | **1382 / 1115.5 (1.24×)**, limit 1.51× |

I also ran a made-up spring-forward DST week; it passed everything.

**Live clients:** Contoso and Fabrikam (W43) and Wingtip (W42) produce byte-identical schedules and `eval.json` compared with the code before my changes. Every new behaviour is switched on only by keys in `configs/northwind.yaml`; `defaults.yaml` and the other clients' configs are untouched.

**What was broken for Northwind, and the fix:**
- **Ingest:** the loader dropped `vip` and worked out UTC from the local clock. That fails on the repeated 01:00 hour on 1 Nov. It now uses each row's `utc_offset` and takes the queue list from config. W44 has 338 intervals.
- **Staffing:**
  - The `interval` handle-time setting was silently ignored (it always used the queue average); it now uses each interval's own value.
  - The 0.85 occupancy cap is now applied for Northwind only. WFM-212 stays open for everyone else, so live clients don't change mid-contract.
- **Scheduler:** a new week-aware scheduler, `wfm/scheduler/week_aware.py`, applies every §2 rule while it places shifts:
  - rest periods, PT-only split shifts, hour caps and the consecutive-day limit;
  - one shift per local day;
  - the VIP floor, counted net of breaks;
  - breaks in the largest-surplus interval.

  It also adds and moves shifts to fix intervals that come up short, and keeps total hours within 1.51× required. The old WFM-231 draft has its rest check backwards, so it should not be wired in.
- **Templates:** Northwind has its own shift templates, including 10-hour ones; none crosses midnight. With only the standard set, VIP could not get above about 0.95, because no shift starts at 08:00.
- **Evaluation:** attainment now counts every operating interval as the SOW says, not just those with volume. It also checks rest, splits, break placement and the net VIP floor.
- **RUNBOOK:** `run` writes it every week from the same figures as `eval.json`. It has the exact §3 keys, followed by the handover note (`docs/clients/northwind_handover.md`), which lists seven pre-existing deviations for §2.8.

**Things you should know:**
- **Bad rows in Northwind's W44 file:** two rows are stamped `10:01` instead of `10:00` (Tue 27 Oct priority, Thu 29 Oct standard). They are counted in the 10:00 interval and should be reported to Northwind's WFM contact.
- **VIP is close to its limit:** only 11 agents can work VIP (440 h a week). In a test with 15% more volume, VIP attainment fell to 0.946, below the 0.95 the SOW requires. More VIP-skilled agents are needed before volume grows.
- **SOW wording I had to interpret:**
  - A break may start at exactly 2 h or exactly 5 h into the shift.
  - "Required" in the break-surplus rule means the Erlang requirement, not the VIP floor.
  - "Breaks aside" in the VIP floor means the agent on break doesn't count toward the floor.

  These are written in the handover note.
- **Run time:** a Northwind run takes about 35 seconds. The search phase is capped at 120 s; on a much slower machine it could stop early, which would still give a rule-compliant but possibly weaker schedule.
- **Registry:** Northwind stays at `onboarding` (only its config schema is now set). Flipping it to `live` is an ops step, and doing it now would flag the pre-go-live W42/W43 data as errors. I updated the two tests that expected Northwind's config to be missing.
