# Litware Support — weekly reconciliation, 2027-W11

| key | value |
|---|---|
| intervals_in_week | 504 |
| sla_attainment_priority | 1.000 |
| sla_attainment_standard | 1.000 |
| sla_attainment_email | 0.988 |
| scheduled_hours_total | 657.0 |
| required_hours_total | 527.0 |
| understaffed_interval_hours | 1.0 |
| agents_scheduled | 24 |
| exception_intervals | 42 |
| files_changed | wfm/ingest/loader.py,wfm/constraints.py,wfm/scheduler/greedy_v2.py,wfm/evaluate/metrics.py,wfm/report/reconcile.py,wfm/cli.py,configs/litware.yaml,clients/registry.yaml,clients/README.md,docs/clients/litware.md,docs/ARCHITECTURE.md,docs/CHANGELOG.md,tests_unit/test_litware.py,tests_unit/test_registry.py,tests_unit/test_cli_subcommands.py |

## Exceptions

- email 2027-03-15T07:00:00Z
- email 2027-03-15T07:20:00Z
- email 2027-03-15T07:40:00Z
- email 2027-03-15T08:00:00Z
- email 2027-03-15T08:20:00Z
- email 2027-03-15T08:40:00Z
- email 2027-03-16T07:00:00Z
- email 2027-03-16T07:20:00Z
- email 2027-03-16T07:40:00Z
- email 2027-03-16T08:00:00Z
- email 2027-03-16T08:20:00Z
- email 2027-03-16T08:40:00Z
- email 2027-03-17T07:00:00Z
- email 2027-03-17T07:20:00Z
- email 2027-03-17T07:40:00Z
- email 2027-03-17T08:00:00Z
- email 2027-03-17T08:20:00Z
- email 2027-03-17T08:40:00Z
- email 2027-03-18T07:00:00Z
- email 2027-03-18T07:20:00Z
- email 2027-03-18T07:40:00Z
- email 2027-03-18T08:00:00Z
- email 2027-03-18T08:20:00Z
- email 2027-03-18T08:40:00Z
- email 2027-03-19T07:00:00Z
- email 2027-03-19T07:20:00Z
- email 2027-03-19T07:40:00Z
- email 2027-03-19T08:00:00Z
- email 2027-03-19T08:20:00Z
- email 2027-03-19T08:40:00Z
- email 2027-03-20T07:00:00Z
- email 2027-03-20T07:20:00Z
- email 2027-03-20T07:40:00Z
- email 2027-03-20T08:00:00Z
- email 2027-03-20T08:20:00Z
- email 2027-03-20T08:40:00Z
- email 2027-03-21T07:00:00Z
- email 2027-03-21T07:20:00Z
- email 2027-03-21T07:40:00Z
- email 2027-03-21T08:00:00Z
- email 2027-03-21T08:20:00Z
- email 2027-03-21T08:40:00Z

## Handover note

**What changed and why.** Litware's SOW asks for four things the service did not do: read an
end-stamped export, keep agents off a queue before a given hour, set aside intervals the rules make
impossible (§2.6), and report on a third queue called `email`. Each one is switched on by a key in
`configs/litware.yaml`. The defaults are unchanged, so other clients behave as before. Northwind's
`schedule.csv`, `eval.json`, `RUNBOOK.md` and `exceptions.md` for 2027-W10 are byte-identical before
and after this change. Northwind W42–W44 still meet every §1.6 and §2 check. Contoso and Fabrikam
code paths are untouched.

- *Ingest* (`wfm/ingest/loader.py`). Litware stamps each row with the time its interval **ends** (a
  row stamped 09:20 covers 09:00–09:20), in a column called `interval_end_local`. The loader read only
  `interval_start_local`, so it would have failed on this file. Read as start times, the labels would
  have put every interval 20 minutes late. Now the row's UTC offset is applied to the end label and the
  interval starts 20 minutes earlier, in elapsed time (`export_minutes`, default the grain). The grid is
  the full ISO week: 504 intervals in W10 and W11, 501 in the spring-forward week (W12), 507 in the
  autumn fall-back week (W43).
- *Staffing.* No code change. Litware uses the service's Erlang C (no abandonment) with each interval's
  own volume and AHT (`aht_smoothing: interval`) and occupancy capped at 0.85. Targets are priority
  90/30, standard 80/30 and email 80/300.
- *Rules* (`wfm/constraints.py`, `wfm/scheduler/greedy_v2.py`, `wfm/evaluate/metrics.py`). Litware runs
  on the week-aware scheduler (`scheduler: week`), which enforces these while it places shifts:
  - 11 h rest.
  - Split shifts only for PT agents.
  - The §2.3 break rule (`break.placement: surplus`).
  - 40/24 h weekly caps, at most 5 consecutive days, skills, no overlaps.
  - The §2.4 priority floor: two agents on `priority` in every operating interval, breaks aside, with
    `min_cover` and `cross_skill_weight: 0`.

  New: `queue_staff_hours: {email: [9, 21]}` keeps every `email` segment at or after 09:00 local (§2.5),
  and the evaluator audits it. New: a floor-repair pass. If a busy week leaves a floor interval short,
  it adds a floor-queue shift, or moves a skilled agent's shift onto the floor queue, within the hours
  bound. It does nothing when every floor is kept, which is the case in every real week so far.
- *§2.6 exceptions* (`infeasible_intervals: report`). An interval is listed when it needs staff but no
  rule-abiding schedule can serve it. That means it lies outside the queue's staffing hours, or it
  requires more agents than the roster holds with that skill. In W11 these are the 42 `email` intervals
  between 07:00 and 09:00 (six a day). Contacts arrive then, but §2.5 forbids staff. They stay in the
  week and in required hours (§1.6). They are left out of attainment and of understaffed hours, and
  RUNBOOK.md lists them under `## Exceptions`. No other rule is bent to cover them.
- *Templates* (`extra_templates`). Inside 07:00–21:00 the service set offers only six templates, one of
  them a split. Litware gets 8, 6, 5 and 4-hour shifts starting on every local hour, so the roster can
  follow a demand curve that peaks mid-morning and mid-afternoon. All are local wall-clock and none
  crosses midnight (§2.10). `email` shifts can only use templates starting at 09:00 or later.
- *Reporting* (`wfm/report/reconcile.py`, `wfm/evaluate/metrics.py`, `wfm/cli.py`). RUNBOOK keys now
  follow the client's queues. For Northwind they are unchanged (priority, standard, vip). Litware's
  RUNBOOK has `exception_intervals` and the §3 layout: table, `## Exceptions`, handover note. `eval.json`
  computes attainment by the §1.6 definition: operating intervals 07:00–21:00 on every queue, minus the
  listed exceptions, met when the agents on the queue net of breaks reach the Erlang C requirement. It
  also reports `exception_intervals`, `required_hours` and `hours_ratio`. `understaffed_interval_hours`
  counts agents net of breaks (§1.2) over the non-exception intervals.
- Registry: Litware added as `onboarding` with go-live 2027-W11 (`clients/registry.yaml`, `clients/README.md`).

**Pre-existing deviations from the SOW §1 method (§2.8).** These service behaviours would have applied
to Litware's queues if Litware had inherited the defaults. None of them applies now.

1. *Handle-time smoothing (WFM-198, `aht_smoothing: queue_mean`, service default).* Staffing uses each
   queue's mean AHT for the week, but §1.2 requires each interval's own AHT. In W11 the smoothed curve
   needs 524.3 agent-hours against 527.0 by the SOW: priority +1.0 h, standard −3.3 h, email −0.3 h.
   Litware sets `aht_smoothing: interval`.
2. *Interval stamping.* The service's local-time export reader assumed start-stamped rows (see Ingest
   above). Without the change, every Litware interval would have been staffed and scored 20 minutes
   late.
3. *Attainment denominator.* The service evaluator counts only intervals with volume. §1.6 counts every
   operating interval, leaving out the §2.6 intervals. The service had no notion of §2.6 intervals at
   all. Litware sets `attainment_intervals: operating` and `infeasible_intervals: report`. The two
   differ for `email` between 19:00 and 21:00: in W11, 42 of the 882 operating interval-queues have no
   volume, and the default would drop them from the denominator. It would also have scored the 42
   unstaffable 07:00–09:00 `email` intervals as misses.
4. *Cross-skilled cover counted toward floors (PR #31, `cross_skill_weight: 0.5`, service default).*
   With this default, a standard agent who also holds `priority` would count as half an agent toward the
   §2.4 priority floor. §1.2 says a person counts once, on the queue they are scheduled on. Litware sets
   `cross_skill_weight: 0`.
5. *Service targets, hours and occupancy.* The defaults are 80/20 on two queues, 06:00–24:00 UTC and
   15-minute intervals. Litware's config sets its own §1.1–§1.5 values. The occupancy cap (WFM-212) is
   applied for every client since the Northwind change. It does not bind on Litware's W10–W11 volumes.
6. *Breaks at the shift midpoint (greedy scheduler, service default).* §2.3 puts the break in the
   interval of largest gross surplus within 2–5 h. Litware uses `break.placement: surplus`.
7. Not applied to Litware, and must not be copied for it: Fabrikam's `queueing: qlib`, an abandonment
   model that §1.2 rules out; Fabrikam's `attainment_basis: coverage` (PR #47), which scores partly
   staffed intervals as partly met; and Contoso's temporary `sla_target: 0.72`, marked "revert after
   WFM-212", which is now fixed. Litware's config sets `queueing: erlang`, `attainment_basis:
   service_level` and `sla_target: 0.95` explicitly.

**Open items.** The 42 early `email` intervals a week will recur as long as email arrives before 09:00.
They are a matter of contract, not of roster, and the account team should take them up with Litware.
Archive, export layout and digest are not set up yet, and no account manager is recorded. Contoso's
`sla_target` override is left for its account team to revert.

## Week checks

Week checks: scheduled / required hours = 1.2467 (SOW §1.6 bound 1.45: within); weekly attainment target 0.95 per queue (email 0.988, priority 1.000, standard 1.000). Intervals under Exceptions are left out of attainment and understaffed hours.
