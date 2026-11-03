# Agent's final message (verbatim, step 37)

Litware is onboarded. `python -m wfm run --client litware --week 2027-W11` writes `schedule.csv`, `eval.json` and `RUNBOOK.md` under `/app/out/litware/`. It also works for other Litware weeks. The one gap: **Northwind's `vip` queue still misses its SOW (0.893 in 2027-W10, target 0.95), and the roster can't close it.** Details below.

**Litware 2027-W11**

| | value |
|---|---|
| Attainment (priority / standard / email) | 1.000 / 1.000 / 1.000 |
| Scheduled vs required hours | 738.0 h vs 527.0 h → 1.40× (cap 1.45×) |
| §2 rule violations | 0 |
| Exceptions | 42 |

- **Exceptions:** all are email intervals from 07:00 to 09:00. Email has contacts then, but §2.5 bans anyone on email before 09:00, so they're listed under `## Exceptions` and left out of attainment, as §2.6 says.
- **Independent check:** I wrote a separate checker straight from the SOW, sharing no code with the service. It agrees with `eval.json` and the RUNBOOK on every figure. For email it gives 1.000 whether attainment is counted to 19:00 or to 21:00.
- **Other Litware weeks:** W10 also comes out at 1.000 on every queue, at 1.42×. I made test copies of W11's data for the two UK clock-change weeks (2027-W12 and W43). Both ran with the right interval counts (501 and 507) and zero violations; I deleted the copies afterwards.
- **Existing clients:** I re-ran Contoso, Fabrikam and Northwind before and after my changes. Their schedules and `eval.json` are byte-identical (one week each); their behaviour only changes through new config options that only Litware sets. All 87 unit tests pass.

**What I changed**
- **Ingest:** Litware stamps each row with the *end* of its interval. The loader now reads that format and uses the row's own UTC offset.
- **New Litware-only settings:**
  - no email shifts before 09:00 (§2.5);
  - the infeasible-interval list in `eval.json` and the RUNBOOK (§2.6);
  - the scheduler aims to meet every interval, not just 0.95, to leave margin for Litware's own audit.
- **Priority cover:** the two-agent `priority` minimum (§2.4) reuses the existing minimum-cover setting, counted net of breaks.
- **Config and records:** `configs/litware.yaml` holds Litware's SOW values. Litware is added to the client registry, and the three tests that expected eight clients are updated.
- **Docs:** Litware's allowed shift templates (§2.10 points there) are now listed in `ARCHITECTURE.md`. I added an entry to `CHANGELOG.md` and wrote `docs/clients/litware.md`, which the RUNBOOK copies its handover note from.

**For you to decide**
1. **Northwind `vip` can't meet its SOW with the current roster.** Only 11 agents hold `vip`, all full-time, so at most 440 h a week. I worked out the minimum by brute force: covering `vip` fully in 2027-W10 needs at least 528 h, even ignoring breaks. A search run with almost seven times the usual effort still reached only 0.893. Every Northwind §2 rule holds, and priority and standard are at 0.96. Meeting 0.95 needs more `vip`-skilled staff or an agreed temporary target; I've updated the Northwind client note with these figures.
2. **The Northwind go-live work was never committed.** Litware depends on it (several of the §2.8 fixes listed in the handover note came with it). I haven't committed anything; say if you want it committed.
3. **Contoso's config has a "temporary" `sla_target: 0.72`,** marked "revert after WFM-212". WFM-212 is now fixed. I left it alone because there's no Contoso SOW in the repo to check against.
