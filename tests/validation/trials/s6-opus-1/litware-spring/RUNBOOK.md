# Litware Support — weekly reconciliation, 2027-W11

Produced by `cd /app && python -m wfm run --client litware --week 2027-W11` (`out/litware/schedule.csv`, `out/litware/eval.json`).

| key | value |
|---|---|
| intervals_in_week | 504 |
| sla_attainment_priority | 1.000 |
| sla_attainment_standard | 1.000 |
| sla_attainment_email | 1.000 |
| scheduled_hours_total | 712.0 |
| required_hours_total | 527.0 |
| understaffed_interval_hours | 0.0 |
| agents_scheduled | 24 |
| exception_intervals | 42 |
| files_changed | configs/litware.yaml, wfm/ingest/loader.py, wfm/constraints.py, wfm/scheduler/templates.py, wfm/scheduler/greedy_v2.py, wfm/evaluate/metrics.py, wfm/report/weekly.py, wfm/cli.py, configs/northwind.yaml, clients/registry.yaml, clients/README.md, docs/clients/litware.md, docs/clients/litware-handover.md, docs/ARCHITECTURE.md, docs/CHANGELOG.md, tests_unit/test_litware.py, tests_unit/test_registry.py, tests_unit/test_cli_subcommands.py, out/litware/RUNBOOK.md, out/northwind/RUNBOOK.md |

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

### What changed and why

Litware's behaviour is set by keys in `configs/litware.yaml`. Each new key defaults in code to what the
service already did, and `configs/defaults.yaml` is untouched. Contoso, Fabrikam and Wingtip produce
byte-identical `schedule.csv` and `eval.json` before and after this change.

- **Config** `configs/litware.yaml` (schema 1): 20-minute grain, Europe/London, operating hours 07–21 on
  all three queues, the SOW §1.2 targets (priority 90/30, standard 80/30, email 80/300), Erlang C without
  abandonment, each interval's own AHT, occupancy cap 0.85 applied, no staff required outside operating hours,
  `sla_target: 0.95`, `efficiency_bound: 1.45`, and the §2 rules (11 h rest, split shifts for PT only,
  breaks by gross surplus, 40/24 h, 5 days). Also a priority floor of 2 agents from 07:00 to 21:00
  (§2.4) with `cross_skill_weight: 0` (§1.2).
- **Ingest** (`wfm/ingest/loader.py`): the export reader assumed every row is stamped with the START of its
  interval. Litware stamps the END (`interval_end_local`), so as delivered each row would have landed one
  interval early. An export with `interval_end_local` is now read as end-stamped. UTC comes from the row's own
  `utc_offset` (the offset at the interval end), and the start is the end minus 20 minutes. This handles
  both clock changes: the 01:00–02:00 hole on the last Sunday of March (501 intervals) and the repeated hour
  in October (507). A stamp off the 20-minute grain goes to the nearest interval end. A repeated
  queue/interval row keeps the first one. Both print a warning. A file with no rows inside the week now
  stops with a message instead of failing inside Erlang C.
- **Email start, §2.5** (`queue_staff_hours: {email: [9, 24]}`, `wfm/constraints.py`, `wfm/scheduler/greedy_v2.py`):
  no email segment may start before 09:00 local. Email contacts arrive from 07:00, so email intervals from
  07:00 to 09:00 with volume can't meet their target under the SOW's own rules. With `report_infeasible`
  (`wfm/evaluate/metrics.py`), those intervals are listed under Exceptions (§2.6). They stay in the week
  (`intervals_in_week`, required hours), but attainment and understaffed hours leave them out (§1.6, §3).
  `eval.json` carries them as `exceptions` / `exception_intervals`. Nothing is scheduled on email before
  09:00 to cover them, and the evaluator reports any such segment as a `queue_staff_hours` violation.
- **Priority cover, §2.4**: the floor is met gross. With `min_cover_net: true` it is also met net of
  breaks, so the rule holds whichever way "breaks aside" is read.
- **Templates** (`wfm/scheduler/templates.py`, `extra_templates`): a client may add its own templates. They
  are local wall-clock times and do not cross midnight (§2.10). Litware adds A8 07–15, M8 11–19,
  P6c 09–15, P6d 13–19, P5a 07–12, P5b 16–21, P5c 09–14 and P5d 14–19, next to the service D8, L8, P6a,
  P6b and P4. E8 and N8 fall outside 07–21. The stock templates fit email's 09:00–19:00 day badly, and W10
  email came out at 0.948. The P6a break window ends at 12:00, the lunch dip, which pushed breaks onto
  the last start the window allows. Shifts under 6 h carry no break (§2.3). The split template S44 is not
  used: whether a 4+4 split counts as a "shift of six hours or more" is ambiguous.
- **Reports** (`wfm/report/weekly.py`, called from `wfm/cli.py`): with `runbook`, each run writes
  `out/<client>/RUNBOOK.md`: the §3 table from `eval.json`, the Exceptions list, and this note. With
  `exceptions_report`, it writes `out/<client>/exceptions.md` (§2.7) for the week just run. Both are off
  for every other client.
- **Northwind** (`configs/northwind.yaml`): the same `extra_templates` mechanism adds B8h 08:30–16:30,
  M8 12–20, P5a 06–11, P5b 19–24 and P5c 08–13, so vip cover can start when vip opens at 08:00. Vip
  attainment rises in every week on file: W42 0.893 → 0.946, W43 0.905 → 0.964, W44 0.911 → 0.970,
  2027-W10 0.905 → 0.958. Priority and standard stay at 1.000, hours go down, and there are no §2
  violations. `exceptions_report: true` writes `out/northwind/exceptions.md` on every run, so a week that
  still misses (W42 vip, 0.004 short) is recorded (§2.7). `out/northwind/RUNBOOK.md` is updated to the
  W44 re-run.
- **Registry and tests**: Litware is in `clients/registry.yaml` and `clients/README.md` as `onboarding`
  (go-live 2027-W11, grain 20, schema 1). `tests_unit/test_litware.py` is new, and the registry tests now
  count nine clients.

Every figure above is recomputed from `schedule.csv` and the raw export by an independent script (its own
Erlang C and break-rule check). It matches `eval.json`, with zero §2 violations. No break sits on the 5-hour
edge of its window, and the priority floor holds net of breaks. 2027-W10 also meets every target
(1.000 / 1.000 / 1.000, 714.0 h against 528.7 required, ratio 1.351).

### SOW §2.8: pre-existing deviations from the §1 method that affect Litware's queues

These service behaviours predate this change and differ from the SOW §1 method. Each one is overridden
for Litware as noted, and each is still the service default for every client that doesn't override it.

1. **Occupancy cap not applied** (WFM-212, open). `occupancy_cap: 0.85` is read but not used in
   required staffing, which breaches §1.3. Litware: `apply_occupancy_cap: true`.
2. **Smoothed handle time** (WFM-198, `aht_smoothing: queue_mean`). Required staffing uses the queue's
   mean AHT, not the interval's own, which breaches §1.2. Litware: `aht_smoothing: interval`.
3. **Attainment counted only on intervals with volume**. §1.6 counts every operating interval.
   Litware: `attainment_intervals: operating`.
4. **Cross-skill credit toward floors** (PR #31, `cross_skill_weight: 0.5`). An agent on another queue
   counts half toward the priority floor, but §1.2 counts a person once, on their scheduled queue.
   Litware: `cross_skill_weight: 0`.
5. **Start-of-interval assumption in ingest**. Before this change, an end-stamped export (§1.5) would have
   shifted every interval 20 minutes early. Fixed in code for any export carrying `interval_end_local`.
6. **No notion of §2.6 intervals in the evaluator**. Email 07:00–09:00 intervals counted as missed
   (W11 email would have read 0.857). Litware: `report_infeasible: true`.
7. **Staff required outside operating hours** when an interval there has volume (service default
   `staff_operating_hours_only: false`). This breaches §1.4. Litware: `true`.
8. **Default per-day greedy scheduler**: breaks at the shift midpoint (§2.3), no rest rule (§2.1), FT
   agents allowed on split shifts (§2.2), and no email start rule (§2.5). Litware: `scheduler: week`.
9. **Not applicable to Litware, listed so nobody copies them**: Fabrikam's `queueing: qlib` (abandonment,
   which §1.2 excludes) and `attainment_basis: coverage` (PR #47), and Contoso's temporary
   `sla_target: 0.72`. Litware runs with `queueing: erlang` and `attainment_basis: service_level`.

### Interpretation choices and data notes

- **Email operating intervals**: 07:00–21:00, like every queue (§1.4). Email volume is zero after 19:00,
  so those intervals need no staff and are met. Counting email only from 07:00 to 19:00 gives the same
  attainment this week (1.000).
- **Exceptions**: an interval is listed when agents are required on a queue at a time the §2 rules forbid
  anyone on it. In Litware's case that means email before 09:00. Email intervals with zero volume before
  09:00 need nobody and are not listed.
- **Break window**: a break may start from 2 h up to and including 5 h after the shift start. No break in
  this schedule starts at exactly 5 h, and no shift has its largest surplus only at 5 h. The schedule is
  valid whether or not the window's end is read as inclusive.
- **Rest across weeks**: §2.1 is enforced within the planning week, as the SOW states. The previous week's
  last shifts are not carried in.
- **Data**: the W10 and W11 exports are complete: 504 rows per queue, no repeated or off-grid rows,
  offsets +00:00 throughout.
