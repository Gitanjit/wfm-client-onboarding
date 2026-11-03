# litware 2027-W11 — reconciliation

| key | value |
|---|---|
| intervals_in_week | 504 |
| sla_attainment_priority | 0.959 |
| sla_attainment_standard | 0.973 |
| sla_attainment_email | 0.990 |
| scheduled_hours_total | 736.0 |
| required_hours_total | 527.0 |
| understaffed_interval_hours | 10.3 |
| agents_scheduled | 24 |
| exception_intervals | 42 |
| files_changed | configs/litware.yaml,configs/defaults.yaml,wfm/config.py,wfm/constraints.py,wfm/ingest/loader.py,wfm/scheduler/greedy.py,wfm/evaluate/metrics.py,wfm/sow.py,clients/registry.yaml,tests_unit/test_litware.py,tests_unit/test_cli_subcommands.py,tests_unit/test_registry.py,docs/ARCHITECTURE.md,docs/CHANGELOG.md,docs/handover/litware-2027-W11.md |

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

## Handover

### Handover — Litware 2027-W11 (go-live)

**What changed and why**

- **Client configuration** (`configs/litware.yaml`, schema 2). Each SOW term is set in one place, with its
  section: 20-minute grain and Europe/London (§1.4, §1.5); operating hours 07:00–21:00, email 07:00–19:00;
  90/30, 80/30 and 80/300 (§1.2); 0.95 weekly attainment on operating intervals (§1.6); occupancy cap 0.85
  applied (§1.3); each interval's own AHT (§1.2); 40 h FT and 24 h PT, five consecutive days (§2.9); surplus
  breaks (§2.3); two agents on priority in every operating interval (§2.4); 11 h rest (§2.1); split shifts for
  PT only (§2.2); net-of-break coverage, one agent counted once (§1.2).
- **Export ingest** (`wfm/ingest/loader.py`). Litware's export stamps each row with the end of its interval
  (`interval_end_local`, per its README). The loader reads that stamp, takes the row's `utc_offset` as
  authoritative, and starts each interval one grain before the stamp. The week is the full local week
  (504 intervals for 2027-W11).
- **Email start** (`wfm/constraints.py`, `wfm/scheduler/greedy.py`; key `queue_start_hours`). No agent is
  scheduled on email before 09:00 local (§2.5). Templates whose first segment starts earlier are not offered on
  email, the repair loop does not chase those intervals, and the evaluator audits the rule as `queue_start`.
- **Email planned first** (`plan_first: [email]`, same planner as `floor_first`). Email has five skilled
  agents. The greedy placed two of them on standard and left 17:00–19:00 email short (email attainment 0.905).
  Planning email for the whole week first holds 0.990.
- **Exceptions** (§2.6). The 07:00–09:00 email intervals cannot be staffed under §2.5, so each is listed under
  `## Exceptions` in the RUNBOOK. They are left out of §1.6 attainment and of understaffed hours, and they stay in
  the week and in required hours. 42 intervals (six per day, seven days).
- **Five-day rule** (`wfm/scheduler/greedy.py`, `_would_exceed_run`). The check counted only the worked days before a
  new shift. A queue planned for the whole week first can hold shifts on later days, so a run could pass five
  consecutive days unseen. The check now counts both sides. It changes no schedule for the existing clients.
- **Evaluator** (`wfm/evaluate/metrics.py`). `eval.json` gains `exception_intervals` and `exceptions`, and the
  audit gains `queue_start`. Attainment and understaffed hours leave out §2.6 intervals (§1.6, §3).
- **Reporting** (`wfm/sow.py`, `wfm sow`). The RUNBOOK carries every §3 key, including `exception_intervals`, and
  the `## Exceptions` list. `exceptions.md` (§2.7) is written as before.
- **Service defaults.** `configs/defaults.yaml` gains `queue_start_hours` and `plan_first`, both off by default.
  No default value changed. Existing clients' schedules are byte-identical to the previous code for Contoso
  2025-W05, 2026-W09, 2026-W42 and 2026-W43, Fabrikam 2025-W33 and 2025-W43, Wingtip 2026-W42, and Northwind
  2026-W42 to 2026-W44.

**Result, 2027-W11** (`out/litware/`)

| queue | attainment (SOW §1.6) | target |
|---|---|---|
| priority (90/30) | 0.959 | 0.95 |
| standard (80/30) | 0.973 | 0.95 |
| email (80/300) | 0.990 | 0.95 |

- Scheduled hours 736.0 against required 527.0: ratio 1.397, inside the §1.6 bound of 1.45 (764.2).
- Zero violations in every §2 rule the evaluator audits.
- The 2027-W10 export, the same command for another week, also meets 0.95 on every queue (priority 0.956,
  standard 0.976, email 1.000).

**Pre-existing deviations from the §1 method that affect Litware's queues (§2.8)**

The service defaults in `configs/defaults.yaml` predate Litware. Each one below differs from the SOW. Litware's
config overrides every one of them, so none affects Litware's schedule or figures. The defaults are unchanged for
the existing clients.

1. Occupancy cap not applied in required staffing by default (WFM-212, still open). §1.3 needs it, so Litware
   sets `apply_occupancy_cap: true`.
2. Queue-mean AHT smoothing by default (WFM-198). §1.2 uses each interval's own AHT, so Litware sets
   `aht_smoothing: interval`.
3. Attainment by default counts only intervals with volume (`sla_denominator: volume`). §1.6 counts operating
   intervals, so Litware sets `operating`.
4. Breaks at the shift midpoint by default. §2.3 needs the largest-surplus interval in the 2–5 hour window, so
   Litware sets `placement: surplus`.
5. A floor counts an agent on another queue at 0.5 by default (`cross_skill_weight`). §1.2 and §2.4 count a
   person once, so Litware sets 0.
6. Coverage by default need not hold net of breaks (`net_of_breaks: false`), and there is no rest rule, no split
   contract rule and no email start rule. Litware sets each one.
7. Loader grid and queues by default were the data delivered and the two queues `priority` and `standard`. The
   grid is now the full local week, and the queues come from the SLA targets, so `email` loads.
8. The five-consecutive-day check (§2.9) looked only at earlier days. A queue planned first could place a run
   past five days (see "Five-day rule" above). Fixed in this change for every client.

Not used by Litware, so not a deviation for it: `vendor/qlib` (Fabrikam's abandonment model), and
`wfm/scheduler/greedy_v2.py` (WIP, WFM-231, not wired in; its rest test is inverted and must be fixed before use).

**Data to raise with Litware's WFM contact** (README: report anything odd)

- None found in 2027-W10 or 2027-W11. All volume falls inside 07:00–21:00, email volume falls between 07:00 and 19:00,
  there are no duplicate or negative rows, and every stamp falls on the 20-minute grid.

**Readings I chose, to confirm with the account team**

- Attainment counts operating intervals, and a zero-volume interval counts as met (required 0). §2.6 intervals are
  left out of attainment.
- The §2.6 set is the email intervals before 09:00 local that carry a requirement. It is 42 intervals in 2027-W11.
- `understaffed_interval_hours` is net of breaks, the §1.2 basis. Ignoring breaks would give a higher figure.
- The §2.4 floor counts agents on shift ignoring breaks ("breaks aside").
- The break window is inclusive (2 to 5 hours after the shift start), and a break starts on a planning-interval start.

**Running it**

- `python -m wfm run --client litware --week <W>` writes `out/litware/schedule.csv` and `out/litware/eval.json`
  (about 20 seconds). `python -m wfm sow --client litware --week <W> --changed <files> --handover
  docs/handover/litware-2027-W11.md` writes `RUNBOOK.md` and `exceptions.md`.
