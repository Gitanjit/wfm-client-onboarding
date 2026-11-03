# Agent's final message (verbatim, step 47)

Northwind is onboarded. `python -m wfm run --client northwind --week 2026-W44` writes `schedule.csv` and `eval.json` to `/app/out/northwind/`, plus `RUNBOOK.md` and `exceptions.md`. Every run regenerates the runbook and exceptions file from that run's schedule. All 86 unit tests pass, and nothing is committed.

**Northwind results**

| week | priority | standard | vip | hours / required | SOW §2 violations |
|---|---|---|---|---|---|
| 2026-W44 (338 intervals, DST) | 1.000 | 1.000 | 0.988 | 1534 / 1115.5 = 1.375 | 0 |
| 2026-W43 | 1.000 | 1.000 | 0.988 | 1.385 | 0 |
| 2026-W42 | 1.000 | 1.000 | 0.976 | 1.355 | 0 |

- **Checks:** I wrote a separate checker that reads only the raw export, the roster and `schedule.csv`, without the service's code. It gives the same attainment, hours, under-staffing and agent counts as `eval.json` and `RUNBOOK.md`, and finds zero rule violations. Running W44 twice gives byte-identical schedules.
- **Other weeks:** a made-up spring-forward week (2026-W10, 334 intervals) also met every target with no violations. I deleted that test file afterwards.
- **Exceptions:** no target was missed, so `exceptions.md` has the table header and a one-line note saying so.

**Live clients:** Contoso, Fabrikam and Wingtip give byte-identical `schedule.csv` and `eval.json` before and after, across 11 recent client-weeks. Everything new is behind client config keys. The one service-wide change is the occupancy-cap fix (WFM-212), which doesn't bind on their data. Neither `defaults.yaml` nor any live client config was touched.

**What I changed**
- **Loader:** each row's `utc_offset` is now trusted, so the repeated 01:00 hour on 1 November becomes two distinct intervals. The week is built as local Monday to Monday, and clients can list their own queues, so `vip` is no longer dropped.
- **Staffing:** the occupancy cap is actually applied now. The per-interval handle-time setting really uses each interval's own value; before, it silently used the queue average. Vip needs no staff outside 08:00–20:00.
- **Scheduler:** I finished the week-aware draft (WFM-231) and fixed its backwards rest check. It now enforces the 11-hour rest, PT-only split shifts, the vip 06:00–24:00 cover (counting only agents on vip) and the SOW break rule. It stops adding hours at 1.51 × required.
- **Templates (decision for you):** with the service's eight templates, the 11 vip-skilled agents can't reach 0.95 on vip; the best I got was about 0.91. So Northwind has its own 8-hour and 6-hour templates starting on each hour. They are local time and never cross midnight, and the service set is unchanged. If the account team wants only the standard templates, remove `extra_templates` from `configs/northwind.yaml`. Vip then drops to about 0.91 and `exceptions.md` will record the shortfall.
- **Evaluation:** attainment counts every operating interval, as the SOW defines it. `eval.json` adds required hours, the hours ratio, and checks for rest, split shifts and breaks.
- **Registry:** Northwind's config schema is now 1. I left its status as `onboarding` for ops to switch to `live` with the first archived week; the two registry tests now expect no pending items.

**Handover note (SOW §2.8):** it's in `RUNBOOK.md`, sourced from `docs/clients/northwind.md`. It lists the old service behaviours that departed from the SOW method, with W44 figures where they matter:
- handle-time averaging, which understates the W44 requirement by 19.5 agent-hours;
- the occupancy cap not being applied;
- attainment counted only over intervals with volume;
- the 0.5 cross-skill credit toward floors;
- breaks placed at the shift midpoint;
- the loader dropping `vip` and mishandling the repeated hour.

It also warns against copying Fabrikam's abandonment model and coverage scoring, or Contoso's 0.72 target, for Northwind.

**Open items**
- Ask Northwind's WFM contact about two W44 rows stamped `10:01` instead of `10:00` (Tue 27 Oct priority, Thu 29 Oct standard). The loader moves them onto the 10:00 interval.
- No export layout or account manager is set for Northwind in the registry yet.
- Runs now take about 20–30 seconds because of the local search.
