"""Text files for tools/volume/gen_world.py: client configs, the client registry and its README, and
the service docs. Every date, number and name here agrees with tools/volume/WORLD.md and with the
data gen_world.py writes."""
from __future__ import annotations

# --------------------------------------------------------------------------------------------------
# configs
# --------------------------------------------------------------------------------------------------

CONFIGS = {
    "configs/tailspin.yaml": """\
# Tailspin Toys — canonical 30-minute files, Irish time.
name: Tailspin Toys
interval_minutes: 30
tz: Europe/Dublin
operating_hours: [7, 21]
sla:
  priority: {target: 0.80, seconds: 20}
  standard: {target: 0.80, seconds: 30}
""",
    "configs/adatum.yaml": """\
# Adatum — canonical hourly files, US Mountain time. Operating hours and targets: service defaults.
name: Adatum
interval_minutes: 60
tz: America/Denver
""",
    "configs/woodgrove.yaml": """\
# Woodgrove Bank — canonical 30-minute files, US Pacific time.
name: Woodgrove Bank
interval_minutes: 30
tz: America/Los_Angeles
operating_hours: [6, 21]
sla:
  priority: {target: 0.90, seconds: 30}
  standard: {target: 0.80, seconds: 20}
""",
    "configs/proseware.yaml": """\
# Proseware — canonical 30-minute files, German time. Config schema 2 (docs/adr/0007-config-schema-v2.md).
schema: 2
name: Proseware
service:
  interval_minutes: 30
  tz: Europe/Berlin
  operating_hours: [7, 21]
targets:
  sla:
    priority: {target: 0.85, seconds: 20}
    standard: {target: 0.80, seconds: 30}
scheduling:
  weekly_hours: {FT: 39, PT: 20}     # Proseware's works agreement
  max_consecutive_days: 5
""",
    "configs/wingtip.yaml": """\
# Wingtip Toys — canonical 30-minute files, Arizona time (no DST). Config schema 2.
schema: 2
name: Wingtip Toys
service:
  interval_minutes: 30
  tz: America/Phoenix
  operating_hours: [6, 24]
targets:
  sla:
    priority: {target: 0.80, seconds: 20}
    standard: {target: 0.80, seconds: 20}
scheduling:
  weekly_hours: {FT: 40, PT: 30}
""",
}

# --------------------------------------------------------------------------------------------------
# clients/
# --------------------------------------------------------------------------------------------------

REGISTRY_ROWS = [
    # key, name, status, onboarded, ended / paused, grain, tz, queues, schema
    ("contoso", "Contoso", "live", "2024-12-02", "—", 15, "UTC",
     "priority, standard (chat 2025-07-21 to 2025-09-01)", "1 (flat)"),
    ("tailspin", "Tailspin Toys", "retired", "2025-01-13", "ended 2025-10-31", 30, "Europe/Dublin",
     "priority, standard", "1 (flat)"),
    ("adatum", "Adatum", "retired", "2025-03-10", "ended 2026-03-27", 60, "America/Denver",
     "priority, standard", "1 (flat)"),
    ("woodgrove", "Woodgrove Bank", "retired", "2025-05-12", "ended 2026-01-16", 30, "America/Los_Angeles",
     "priority, standard", "1 (flat)"),
    ("fabrikam", "Fabrikam", "live", "2025-08-11 (pilot); renewed 2025-10-06", "—", 60, "America/New_York",
     "priority, standard", "1 (flat)"),
    ("proseware", "Proseware", "paused", "2025-11-17", "paused 2026-08-14", 30, "Europe/Berlin",
     "priority, standard", "2 (nested)"),
    ("wingtip", "Wingtip Toys", "live", "2026-02-09", "—", 30, "America/Phoenix", "priority, standard",
     "2 (nested)"),
    ("northwind", "Northwind Traders", "onboarding (go-live 2026-W44)", "—", "—", 30, "America/Chicago",
     "priority, standard, vip", "pending"),
]


def clients_readme() -> str:
    head = ("| client | name | status | onboarded | ended / paused | grain (min) | timezone | queues | config schema |\n"
            "|---|---|---|---|---|---|---|---|---|\n")
    rows = "".join(f"| {k} | {n} | {s} | {o} | {e} | {g} | {tz} | {q} | {sc} |\n"
                   for k, n, s, o, e, g, tz, q, sc in REGISTRY_ROWS)
    return f"""\
# Clients

Every client the service has planned for, oldest first. `clients/registry.yaml` holds the same facts
in machine-readable form: `python -m wfm clients` lists them and `python -m wfm clients --check`
compares them with `configs/`, `data/` and the rosters in `data/agents/`.

{head}{rows}
Status

- **live** — weekly data drop, run, archive, export and digest (`docs/OPERATIONS.md`).
- **paused** — no weekly runs. Config, roster and data stay as they were so that the client can
  restart without re-onboarding.
- **retired** — contract ended. Config, roster, data and unit tests are kept: past weeks can still be
  re-run and compared, and the tests keep the older configs loading.
- **onboarding** — signed, not yet live. The registry entry carries the go-live week; the config and
  roster land with the go-live change.

Client notes: `docs/clients/<client>.md`. Lifecycle rules: `docs/adr/0008-client-lifecycle.md`.
Weekly cycle: `docs/OPERATIONS.md`.
"""


REGISTRY = """\
# Client registry: lifecycle and planning facts, one entry per client. `python -m wfm clients` reads it
# and `python -m wfm clients --check` compares it with configs/, data/ and the rosters.
# status: live | paused | retired | onboarding. Retired and paused clients keep their config, roster,
# data and tests (docs/adr/0008-client-lifecycle.md). Human-readable view: clients/README.md.
clients:
  contoso:
    name: Contoso
    status: live
    onboarded: 2024-12-02
    ended: null
    paused_from: null
    golive_week: null
    grain: 15
    tz: UTC
    queues: [priority, standard]
    config_schema: 1
    data_format: canonical
    export_layout: activity_csv
    account_manager: Sam Ferreira
    notes: Evening chat queue from 2025-07-21 to 2025-09-01.
  tailspin:
    name: Tailspin Toys
    status: retired
    onboarded: 2025-01-13
    ended: 2025-10-31
    paused_from: null
    golive_week: null
    grain: 30
    tz: Europe/Dublin
    queues: [priority, standard]
    config_schema: 1
    data_format: canonical
    export_layout: roster_grid_csv
    account_manager: null
    notes: Contract not renewed; last drop 2025-W43.
  adatum:
    name: Adatum
    status: retired
    onboarded: 2025-03-10
    ended: 2026-03-27
    paused_from: null
    golive_week: null
    grain: 60
    tz: America/Denver
    queues: [priority, standard]
    config_schema: 1
    data_format: canonical
    export_layout: activity_csv
    account_manager: null
    notes: Moved planning in-house; last week served 2026-W13.
  woodgrove:
    name: Woodgrove Bank
    status: retired
    onboarded: 2025-05-12
    ended: 2026-01-16
    paused_from: null
    golive_week: null
    grain: 30
    tz: America/Los_Angeles
    queues: [priority, standard]
    config_schema: 1
    data_format: canonical
    export_layout: activity_csv
    account_manager: null
    notes: Contact centre consolidated into another site; last week served 2026-W03.
  fabrikam:
    name: Fabrikam
    status: live
    onboarded: 2025-08-11
    ended: null
    paused_from: null
    golive_week: null
    grain: 60
    tz: America/New_York
    queues: [priority, standard]
    config_schema: 1
    data_format: canonical
    export_layout: activity_csv
    account_manager: Ruth Abara
    notes: Pilot from 2025-08-11; renewed 2025-10-06 for 12 months.
  proseware:
    name: Proseware
    status: paused
    onboarded: 2025-11-17
    ended: null
    paused_from: 2026-08-14
    golive_week: null
    grain: 30
    tz: Europe/Berlin
    queues: [priority, standard]
    config_schema: 2
    data_format: canonical
    export_layout: roster_grid_csv
    account_manager: Sam Ferreira
    notes: Paused at the client's request; config, roster and data kept for a restart.
  wingtip:
    name: Wingtip Toys
    status: live
    onboarded: 2026-02-09
    ended: null
    paused_from: null
    golive_week: null
    grain: 30
    tz: America/Phoenix
    queues: [priority, standard]
    config_schema: 2
    data_format: canonical
    export_layout: segments_json
    account_manager: Ruth Abara
    notes: Arizona time all year (no DST).
  northwind:
    name: Northwind Traders
    status: onboarding
    onboarded: null
    ended: null
    paused_from: null
    golive_week: 2026-W44
    grain: 30
    tz: America/Chicago
    queues: [priority, standard, vip]
    config_schema: null
    data_format: export
    export_layout: null
    account_manager: null
    notes: Signed for go-live in 2026-W44; demand export in local time with a UTC offset per row.
"""




# --------------------------------------------------------------------------------------------------
# docs/adr/
# --------------------------------------------------------------------------------------------------

ADRS = {
    "docs/adr/0001-canonical-interval-format.md": """\
# 0001 — Canonical interval format

Date: 2024-11-08 · Status: accepted · Author: Dana Vexley

## Context

The service plans from interval demand: contacts arriving per queue per planning interval, with their
average handle time. Every contact-centre platform exports this differently: local or UTC stamps,
interval start or interval end, one file per queue, rows missing where nothing arrived. The planning
code should not need to know any of that.

## Decision

Demand enters the service as one canonical file per client per ISO week,
`data/<client>/week_<YYYY>-W<ww>.csv`:

| column | meaning |
|---|---|
| `client` | client key, the same as the config file name (`contoso`) |
| `queue` | queue name |
| `interval_start_utc` | interval start, ISO 8601 with `Z` |
| `interval_minutes` | the client's planning grain: 15, 30 or 60 |
| `volume` | contacts that arrived in the interval, three decimals |
| `aht_sec` | average handle time of those contacts, seconds, three decimals |

- One row per queue per interval for the whole ISO week in the client's timezone, including intervals
  with no volume. A missing row is a data problem, not a quiet interval.
- Rows are ordered by interval, then queue.
- A zero-volume row carries the queue's base handle time, so that the column has no gaps.
- Converting a client's own export into this layout is part of that client's onboarding and happens
  before the file is committed.

## Consequences

- Ingest reads one layout. Resampling to the client's grain is the only transformation it applies.
- The row count of a week follows from the grain and the timezone: 7 × 24 × 60 / grain rows per queue,
  give or take the DST hour (0002).
- A client whose export cannot be converted mechanically needs its converter described in its client
  notes (`docs/clients/<client>.md`).
""",
    "docs/adr/0002-utc-storage-local-templates.md": """\
# 0002 — Store UTC, plan in local wall-clock time

Date: 2024-11-15 · Status: accepted · Author: Dana Vexley

## Context

Clients sit in different timezones and most of them change offset twice a year. Agents work local
shifts ("09:00 to 17:00"), contracts count hours worked, and the platform exports we receive are
stamped in whatever the client's platform uses.

## Decision

- Every timestamp the service stores or writes is UTC (`*_utc` columns, ISO 8601 with `Z`).
- Shift templates are local wall-clock segments on one local day and never cross local midnight. A
  template becomes UTC per day through the client's IANA timezone (`tz`).
- Durations (shift length, weekly hours, rest) are elapsed time, measured in UTC.
- The planning week is the ISO week in the client's local time: local Monday 00:00 to the next local
  Monday 00:00.

## Consequences

- A week that contains a DST change has a different number of intervals: one hour fewer in spring,
  one more in autumn. Code that assumes 7 × 24 hours per week is wrong for those weeks.
- A template that spanned the change night would be an hour shorter or longer in elapsed time. The
  templates in use start at 06:00 local or later, so this does not arise today.
- Reports and exports for people convert back to local time at the edge, per row.
""",
    "docs/adr/0003-deterministic-scheduling.md": """\
# 0003 — Deterministic scheduling

Date: 2024-11-21 · Status: accepted · Author: Dana Vexley

## Context

Weekly schedules are compared with the previous week, re-run after data corrections and reviewed as
diffs. A planner that gives a different answer on every run makes all three useless: a reviewer
cannot tell a change caused by new data from noise.

## Decision

- No randomness in planning code. Template order is fixed; ties between agents are broken by
  `agent_id`; every output is sorted before it is written.
- The same inputs (data file, config, roster, code) give byte-identical `schedule.csv` and `eval.json`.
- Anything outside the service that needs random numbers (synthetic test data, sampling) takes an
  explicit seed.

## Consequences

- Re-running a week after a fix shows exactly what the fix changed; `diff` is the review tool.
- The greedy placement does not search, so it can miss better schedules. A future solver must keep this
  property: fixed seeds, stable sorts, no dependence on dictionary or set iteration order.
""",
    "docs/adr/0004-per-client-config-overlay.md": """\
# 0004 — Per-client configuration overlay

Date: 2025-03-05 · Status: accepted · Author: Tomas Okafor

## Context

Contoso runs on the service defaults. Tailspin, live since January, needs a 30-minute grain,
Europe/Dublin, 07:00–21:00 and its own standard-queue target. Adatum, signed for March, needs an hourly
grain and America/Denver. Client differences need a home that cannot change another client's plan.

## Decision

- `configs/defaults.yaml` holds the service-wide settings.
- `configs/<client>.yaml` overrides top-level keys for that client only. A nested value (`sla`,
  `weekly_hours`, `break`) is replaced whole, not merged key by key.
- The file name is the client key. The CLI refuses a client without a config file.
- The defaults are not changed to suit one client. Every client without an override inherits them.

## Consequences

- Adding a client means a config file, a roster and a data directory.
- A client that overrides one queue's target restates the other queue's too.
- Code reads settings from the merged config only, never from `defaults.yaml` directly.
""",
    "docs/adr/0005-vendoring-policy.md": """\
# 0005 — Vendoring third-party code

Date: 2025-08-08 · Status: accepted · Author: Mei Lindqvist

## Context

The Fabrikam pilot, starting 2025-08-11, plans with a queueing model that includes caller abandonment.
The service's own Erlang C (`wfm/staffing/erlang.py`) has none. qlib, a small MIT-licensed queueing
library, provides one. The service's runtime dependencies are pandas, numpy and pyyaml, pinned, and we
want to keep it that way.

## Decision

- Third-party code the service runs lives under `vendor/<name>/` and is imported as `vendor.<name>`.
- Only pure-Python packages without dependencies of their own are vendored.
- Each vendored package keeps its `LICENSE`, its `README.md` (stating the version), its `CHANGELOG.md`
  and its own tests; `python -m pytest -q vendor/<name>/tests` passes.
- No local edits inside `vendor/`. A change the service needs goes upstream or into a wrapper under
  `wfm/`.
- An upgrade replaces the package directory in one commit whose message names the old and the new
  version.

## Consequences

- The service's Erlang C remains the model every client uses by default; a vendored model is chosen
  per client in its config.
- The runtime dependency list stays at three pinned packages.
""",
    "docs/adr/0006-schedule-export-layouts.md": """\
# 0006 — Schedule export layouts

Date: 2025-08-18 · Status: accepted · Author: Mei Lindqvist

## Context

Clients load the weekly schedule into their own workforce tools as the baseline for the coming week.
Until now each export was produced by hand from `out/<client>/schedule.csv`, in whatever shape the
client's tool imports. The shapes in use reduce to three: one row per activity with local times; one
row per agent with a column per day; and a JSON document for tools that import through an API.

## Decision

- Exporters live in `wfm/export/`, one module per layout, behind `python -m wfm export`.
- They read only `out/<client>/schedule.csv` and the client config (for the timezone). They never call
  the planning code, so an exporter cannot change a schedule.
- Local times are computed per row from the client's timezone. A layout that has room for it carries
  the UTC offset of each row.
- Layouts: `activity_csv`, `roster_grid_csv`, `segments_json`. Output goes to `out/<client>/export/`,
  sorted, so two exports of the same schedule are identical.
- The layout a client uses is agreed at onboarding and recorded in its client notes.

## Consequences

- A new client tool means a new module, not changes to the planner.
- Exports are only as fresh as the last `wfm run` for that week. The exporter checks that
  `eval.json` is for the requested week before writing anything.
""",
    "docs/adr/0007-config-schema-v2.md": """\
# 0007 — Client config schema 2

Date: 2025-11-10 · Status: accepted · Author: Tomas Okafor

## Context

Flat client files (0004) mix planning grain, service targets and contract rules in one list of keys.
Proseware's onboarding sheet arrives in sections (service hours, targets, working-time rules) and maps
onto those keys badly. A typo in a flat file (`operating_hour:`) is silently ignored and the client
gets the default.

## Decision

Schema 2 groups the same keys into four sections. A file declares `schema: 2` at the top:

```yaml
schema: 2
name: Proseware
service:                 # grain, timezone, operating hours
  interval_minutes: 30
  tz: Europe/Berlin
  operating_hours: [7, 21]
targets:                 # service-level targets and the evaluator's settings
  sla:
    priority: {target: 0.85, seconds: 20}
    standard: {target: 0.80, seconds: 30}
staffing: {}             # staffing-model settings
scheduling:              # working-time rules
  weekly_hours: {FT: 39, PT: 20}
```

- Keys inside a section are exactly the flat keys; `V2_SECTIONS` in `wfm/config.py` lists which keys
  each section may hold. `load_config` flattens a schema-2 file (`_flatten_v2`) before the overlay, so
  the rest of the service sees flat keys only.
- An unknown section, or a key in the wrong section, stops the run with an error naming it.
- Schema-1 files load exactly as before. Existing clients are not migrated.
- New clients from Proseware on are written in schema 2.

## Consequences

- One flat namespace underneath: a key cannot mean two things in two sections.
- The overlay rule is unchanged: a nested value such as `sla` replaces the default whole.
- Adding a service key means adding it to its section in `V2_SECTIONS`, or schema-2 clients cannot set it.
""",
    "docs/adr/0008-client-lifecycle.md": """\
# 0008 — Client lifecycle and the registry

Date: 2026-10-14 · Status: accepted · Author: Tomas Okafor

## Context

Three clients have retired (Tailspin 2025-10-31, Woodgrove 2026-01-16, Adatum 2026-03-27), Proseware
paused at its own request on 2026-08-14, and Northwind is signed for 2026-W44. Status lived in
people's heads and in the weekly ops list. The same questions kept coming back: can a retired client's
files go, should a paused client's drops still be committed, when does a new client's config land.

## Decision

- `clients/registry.yaml` records every client with a status: `live`, `paused`, `retired` or
  `onboarding`, the lifecycle dates, grain, timezone, queues, config schema, export layout and account
  manager. `clients/README.md` is the readable view and is kept in step with it.
- **Retired**: config, roster, data and unit tests stay. No weekly runs. `ended` is the last day served.
- **Paused**: everything stays; no weekly runs; `paused_from` is the first day not served. A restart sets
  the status back to `live` and starts with the next data drop.
- **Onboarding**: an entry with `golive_week`. Config and roster land with the go-live change.
- `python -m wfm clients --check` compares the registry with `configs/`, `data/` and the rosters. An
  onboarding client without a config is reported as pending, not as an error.
- Deleting a client's files needs its own decision record.

## Consequences

- The repository keeps growing with retired clients' data, about 1 MB per client-year at a 30-minute
  grain.
- Schema-1 configs stay supported for as long as a retired client uses one.
- `export` takes the client's layout from the registry when `--layout` is not given.
""",
}


# --------------------------------------------------------------------------------------------------
# docs/incidents/
# --------------------------------------------------------------------------------------------------

INCIDENTS = {
    "docs/incidents/2025-07-01-telephony-platform-outage.md": """\
# 2025-06-24 — Hosted telephony outage (Contoso, Tailspin, Adatum, Woodgrove)

Incident: Tuesday 2025-06-24, 13:40–16:20 UTC · Written: 2025-07-01 · Author: Mei Lindqvist · WFM-068

## Summary

The hosted telephony platform that carries inbound calls for four of our clients rejected calls for
2 h 40 min. No contacts reached those clients' queues in that window. The service itself was not
affected. This note records what the outage looks like in the data and how the week is treated.

## What the 2025-W26 files show

Zero volume on both queues for every interval wholly inside the window; the interval on each side
keeps the share of its contacts that arrived outside it. The files were committed as delivered.

| client | grain | local time of the window | zero-volume intervals (local) |
|---|---|---|---|
| contoso | 15 min | 13:40–16:20 UTC | 13:45–16:15, 10 intervals |
| tailspin | 30 min | 14:40–17:20 Europe/Dublin | 15:00–17:00, 4 intervals |
| adatum | 60 min | 07:40–10:20 America/Denver | 08:00–10:00, 2 intervals |
| woodgrove | 30 min | 06:40–09:20 America/Los_Angeles | 07:00–09:00, 4 intervals |

## Effect on planning and reporting

- The evaluator skips intervals without volume, so 2025-W26 attainment for these clients is computed
  over slightly fewer intervals. The weekly figures were reported as computed, with a line on the
  outage in each digest.
- Schedules built on the W26 files plan less cover inside the window. Each client's planners were
  told to take Tuesday afternoon from the W25 baseline instead.
- When W26 is used as a reference week later, treat Tuesday 24 June as an outage, not as demand.

## Detection and follow-up

Contoso's account team heard about the outage from the client on the day. For the other three clients
it surfaced in Monday's weekly run (30 June), when the reviewer saw Tuesday's schedules thin out in
the afternoon, after the files had been committed. Follow-up: a volume report that lists zero-volume runs inside operating hours at drop
time (PR #24).
""",
    "docs/incidents/2025-11-05-woodgrove-dst-fall-back-ingest.md": """\
# 2025-11-03 — Woodgrove 2025-W44 ingested an hour off after the fall-back

Week: 2025-W44 (27 October – 2 November 2025; US clocks went back at 02:00 on Sunday 2 November) ·
Written: 2025-11-05 · Author: Tomas Okafor · WFM-114

## Summary

Woodgrove's platform exports interval data in Pacific wall-clock time without an offset column. The
converter that turns that export into the canonical file took the offset of the file's first row
(UTC−7) and applied it to the whole week. Every row from the repeated 01:00 hour on Sunday was stamped
an hour early in UTC.

## Impact

- The converted file had 336 distinct interval starts instead of 338, and two duplicated ones (the
  repeated 01:00 hour, which carries no volume).
- Sunday's demand landed an hour early against the templates: the 06:00 opening hour showed volume
  from 05:00, outside operating hours, and Sunday's attainment came out well below the rest of the week.
- The Monday run's export went to Woodgrove before the problem was found and was replaced on
  Wednesday 5 November.

## Detection

The drop check and the commit were skipped that Monday (rota handover): the converted file was run and
exported straight from the drop folder. Joel Mbeki's digest review flagged Sunday's attainment the same
afternoon, and `python -m wfm report volume` on the file then showed 336 intervals against 338
expected.

## Resolution

- The converter now takes each row's offset from the timezone database for the row's local time, and
  resolves the repeated hour by row order (first occurrence UTC−7, second UTC−8).
- 2025-W44 was re-cut and committed on 2025-11-05 with 338 intervals, re-run and re-exported.
- Same weekend, other clients: Adatum's 2025-W44 file (America/Denver, hourly) had the expected 169
  intervals. Tailspin's autumn change (Europe/Dublin, 2025-W43) had come through with 338 intervals.
""",
    "docs/incidents/2026-01-30-adatum-late-data-drop.md": """\
# 2026-01-26 — Adatum 2026-W04 data arrived three days late

Week: 2026-W04 (19–25 January 2026) · Written: 2026-01-30 · Author: Mei Lindqvist · WFM-142

## Summary

Adatum's 2026-W04 interval file, due on Monday 26 January, arrived on Thursday 29 January at 16:05 UTC.
Adatum upgraded its contact-centre platform over the weekend of 24–25 January and the scheduled
reporting job did not run afterwards. Their WFM contact re-ran it by hand once it had been fixed.

## Impact

- The W04 run, the baseline export and the weekly digest for Adatum went out on Thursday evening
  instead of Monday. Adatum's planners kept the W03 baseline for the first days of W05.
- The file itself is complete: 168 intervals, both queues, no zero-volume runs inside operating hours.

## Timeline (UTC)

- Mon 26 Jan 12:00 — no Adatum file in the drop folder; first reminder to their WFM contact.
- Tue 27 Jan 10:30 — second reminder; Adatum confirms the reporting job failed after the upgrade.
- Thu 29 Jan 16:05 — file received; checked with the volume report, committed, run, exported.
- Thu 29 Jan 18:40 — digest sent, marked as late.

## Follow-up

- Weekly runbook: a drop missing at Tuesday 12:00 UTC is chased by the person on the rota, and the
  digest for that client goes out saying the data is pending rather than skipping the week.
""",
    "docs/incidents/2026-04-21-contact-centre-tenant-outage.md": """\
# 2026-04-14 — Contact-centre tenant outage (Fabrikam, Proseware, Wingtip)

Incident: Tuesday 2026-04-14, 13:00–15:30 UTC · Written: 2026-04-21 · Author: Tomas Okafor · WFM-158

## Summary

The cloud contact-centre tenant shared by Fabrikam, Proseware and Wingtip stopped routing contacts for
two and a half hours. Contoso is on a different platform and was not affected. The service was not
affected; the gap shows in the 2026-W16 interval files as zero volume inside operating hours.

## What the 2026-W16 files show

| client | grain | local time of the window | zero-volume intervals (local) |
|---|---|---|---|
| fabrikam | 60 min | 09:00–11:30 America/New_York | 09:00–11:00, 2 intervals; 11:00 at about half volume |
| proseware | 30 min | 15:00–17:30 Europe/Berlin | 15:00–17:30, 5 intervals |
| wingtip | 30 min | 06:00–08:30 America/Phoenix | 06:00–08:30, 5 intervals (from opening) |

## Handling

- Files committed as delivered. The evaluator skips intervals without volume, so W16 attainment for
  the three clients is over slightly fewer intervals; each digest carried a line on the outage.
- `python -m wfm report volume` listed all three runs at drop time on Monday 20 April, before the
  account managers had passed on the clients' own outage notices.
- Schedules built on the W16 files plan less cover inside the window. For Wingtip that is Tuesday's
  first two and a half hours; its planners took that morning from the W15 baseline.
""",
}


# --------------------------------------------------------------------------------------------------
# docs/clients/
# --------------------------------------------------------------------------------------------------

def _table(rows: list[tuple[str, str]]) -> str:
    return "| | |\n|---|---|\n" + "".join(f"| {k} | {v} |\n" for k, v in rows)


def _roster(n: int, pt: int) -> str:
    return f"{n} agents ({pt} part-time)"


def client_notes(clients: dict) -> dict[str, str]:
    c = clients
    notes = {}
    notes["docs/clients/contoso.md"] = f"""\
# Contoso

{_table([
    ("Live since", "2024-12-02 (2024-W49)"),
    ("Account manager", "Sam Ferreira"),
    ("Grain / timezone", "15 minutes / UTC"),
    ("Operating hours", "06:00–24:00 UTC, seven days"),
    ("Queues", "priority, standard"),
    ("Config", "`configs/contoso.yaml` (schema 1)"),
    ("Roster", "`data/agents/contoso.csv`, " + _roster(40, 8)),
    ("Data", "`data/contoso/week_<ISO>.csv`, canonical as delivered"),
    ("Export layout", "`activity_csv` (from 2025-W34)"),
])}
## Data drop

Contoso's platform writes the previous week's file to the drop folder on Monday by 07:00 UTC. It is
already in the canonical layout and in UTC, so there is no converter. Contoso was the first client and
the canonical layout (`docs/adr/0001-canonical-interval-format.md`) follows its export closely.

## Queues

Priority and standard throughout. An evening chat queue ran from 2025-07-21 to 2025-09-01: the weeks
2025-W30 to 2025-W35 carry `chat` rows, with volume between 16:00 and 24:00 UTC.

## Weeks worth knowing

- 2024-W52 and 2025-W01: Christmas and New Year. Volume about a quarter (W52) and a fifth (W01)
  below the surrounding weeks.
- 2025-W26: hosted telephony outage on Tuesday 24 June, 13:40–16:20 UTC
  (`docs/incidents/2025-07-01-telephony-platform-outage.md`).

## Contacts

Sam Ferreira (account). Contoso's WFM team owns the drop and imports the baseline export.
"""
    t = c["tailspin"]
    notes["docs/clients/tailspin.md"] = f"""\
# Tailspin Toys

{_table([
    ("Served", "2025-01-13 (2025-W03) to 2025-10-31 (2025-W44); retired"),
    ("Grain / timezone", "30 minutes / Europe/Dublin"),
    ("Operating hours", "07:00–21:00 local, seven days"),
    ("Queues", "priority (80 % in 20 s), standard (80 % in 30 s)"),
    ("Config", "`configs/tailspin.yaml` (schema 1)"),
    ("Roster", "`data/agents/tailspin.csv`, " + _roster(t["n_agents"], t["n_pt"])),
    ("Data", "`data/tailspin/week_<ISO>.csv`, converted from Tailspin's local-time export"),
    ("Export layout", "`roster_grid_csv` (from 2025-W34)"),
])}
## Data

Tailspin's platform exports Irish wall-clock time with the UTC offset on every row. The converter
derives UTC from that offset. Ireland's clocks follow the EU change dates (last Sunday of March and of
October), so the spring week has 334 half-hour intervals and the autumn week 338.

## Weeks worth knowing

- Irish public holidays, each 15–20 % below the surrounding weeks: 2025-W06 (St Brigid's Day),
  2025-W12 (St Patrick's Day), 2025-W17 (Easter Monday), 2025-W19 (May bank holiday), 2025-W23 (June
  bank holiday), 2025-W32 (August bank holiday).
- 2025-W13: spring forward on 30 March, 334 intervals. 2025-W43: fall back on 26 October, 338 intervals.
- 2025-W26: hosted telephony outage on Tuesday 24 June, 15:00–17:00 local without contacts
  (`docs/incidents/2025-07-01-telephony-platform-outage.md`).

## Offboarding

Tailspin did not renew. The contract ended on Friday 31 October 2025. The last drop was 2025-W43,
processed on 27 October; no drop was requested for the final, partial week. Config, roster and data
stay in the repository so that past weeks can be re-run.
"""
    a = c["adatum"]
    notes["docs/clients/adatum.md"] = f"""\
# Adatum

{_table([
    ("Served", "2025-03-10 (2025-W11) to 2026-03-27 (2026-W13); retired"),
    ("Grain / timezone", "60 minutes / America/Denver"),
    ("Operating hours", "06:00–24:00 local (service default)"),
    ("Queues", "priority, standard (service default targets)"),
    ("Config", "`configs/adatum.yaml` (schema 1), the first client written as a config overlay"),
    ("Roster", "`data/agents/adatum.csv`, " + _roster(a["n_agents"], a["n_pt"])),
    ("Data", "`data/adatum/week_<ISO>.csv`, converted from Adatum's hourly report"),
    ("Export layout", "`activity_csv` (from 2025-W34)"),
])}
## Data

Adatum's reporting job writes hourly intervals in Mountain time with the offset per row; the converter
derives UTC from it. US DST weeks have 167 (spring) and 169 (autumn) hourly intervals.

## Weeks worth knowing

- US public holidays: 2025-W22 (Memorial Day), 2025-W27 (Independence Day), 2025-W48 (Thanksgiving),
  2025-W52 and 2026-W01 (Christmas, New Year), 2026-W04 (Martin Luther King Jr. Day).
- 2025-W44: fall back on 2 November, 169 intervals. 2026-W10: spring forward on 8 March, 167 intervals.
- 2025-W26: hosted telephony outage on Tuesday 24 June, 08:00–10:00 local without contacts
  (`docs/incidents/2025-07-01-telephony-platform-outage.md`).
- 2026-W04: the drop arrived three days late (`docs/incidents/2026-01-30-adatum-late-data-drop.md`).

## Offboarding

Adatum moved its planning in-house. The contract ended on Friday 27 March 2026; the last week planned
was 2026-W13. Config, roster and data stay in the repository so that past weeks can be re-run.
"""
    w = c["woodgrove"]
    notes["docs/clients/woodgrove.md"] = f"""\
# Woodgrove Bank

{_table([
    ("Served", "2025-05-12 (2025-W20) to 2026-01-16 (2026-W03); retired"),
    ("Grain / timezone", "30 minutes / America/Los_Angeles"),
    ("Operating hours", "06:00–21:00 local, seven days"),
    ("Queues", "priority (90 % in 30 s), standard (80 % in 20 s)"),
    ("Config", "`configs/woodgrove.yaml` (schema 1)"),
    ("Roster", "`data/agents/woodgrove.csv`, " + _roster(w["n_agents"], w["n_pt"])),
    ("Data", "`data/woodgrove/week_<ISO>.csv`, converted from Woodgrove's local-time export"),
    ("Export layout", "`activity_csv` (from 2025-W34)"),
])}
## Data

Woodgrove's platform exports Pacific wall-clock time without an offset column. The converter takes
each row's offset from the timezone database and resolves the repeated autumn hour by row order (see
the 2025-W44 incident). The autumn DST week has 338 half-hour intervals.

## Weeks worth knowing

- US public holidays: 2025-W22 (Memorial Day), 2025-W27 (Independence Day), 2025-W48 (Thanksgiving),
  2025-W52 and 2026-W01 (Christmas, New Year).
- 2025-W26: hosted telephony outage on Tuesday 24 June, 07:00–09:00 local without contacts
  (`docs/incidents/2025-07-01-telephony-platform-outage.md`).
- 2025-W44: fall back on 2 November. First converted an hour off, re-cut with 338 intervals
  (`docs/incidents/2025-11-05-woodgrove-dst-fall-back-ingest.md`).

## Offboarding

Woodgrove consolidated its contact centre into another site. The contract ended on Friday 16 January
2026; the last week planned was 2026-W03. Config, roster and data stay in the repository so that past
weeks can be re-run.
"""
    notes["docs/clients/fabrikam.md"] = f"""\
# Fabrikam

{_table([
    ("Pilot", "from 2025-08-11 (2025-W33)"),
    ("Renewal", "signed 2025-10-06, for 12 months"),
    ("Account manager", "Ruth Abara"),
    ("Grain / timezone", "60 minutes / America/New_York"),
    ("Operating hours", "06:00–24:00 local, seven days"),
    ("Queues", "priority, standard"),
    ("Config", "`configs/fabrikam.yaml` (schema 1)"),
    ("Roster", "`data/agents/fabrikam.csv`, " + _roster(28, 6)),
    ("Data", "`data/fabrikam/week_<ISO>.csv`, hourly"),
    ("Export layout", "`activity_csv`"),
])}
## Config

Hourly grain and US Eastern time. The config sets `queueing: qlib` (the vendored queueing library,
`vendor/qlib`) and `attainment_basis: coverage`. Operating hours and SLA targets are the service
defaults.

## Timeline

- 2025-08-11: pilot starts with 2025-W33.
- 2025-10-06: renewal signed for 12 months; planning continues without a break.

## Contacts

Ruth Abara (account). Fabrikam's WFM team owns the drop and imports the baseline export.
"""
    p = c["proseware"]
    notes["docs/clients/proseware.md"] = f"""\
# Proseware

{_table([
    ("Onboarded", "2025-11-17 (2025-W47)"),
    ("Paused", "from 2026-08-14 at Proseware's request; last week planned 2026-W33"),
    ("Account manager", "Sam Ferreira"),
    ("Grain / timezone", "30 minutes / Europe/Berlin"),
    ("Operating hours", "07:00–21:00 local, seven days"),
    ("Queues", "priority (85 % in 20 s), standard (80 % in 30 s)"),
    ("Working time", "39 h full-time, 20 h part-time per week; at most 5 consecutive days"),
    ("Config", "`configs/proseware.yaml`, the first schema-2 config"),
    ("Roster", "`data/agents/proseware.csv`, " + _roster(p["n_agents"], p["n_pt"])),
    ("Data", "`data/proseware/week_<ISO>.csv`, canonical as delivered by Proseware's BI team"),
    ("Export layout", "`roster_grid_csv`"),
])}
## Data

Proseware's BI team delivers canonical files in UTC on Monday mornings. Germany follows the EU change
dates; the spring week 2026-W13 has 334 half-hour intervals.

## Weeks worth knowing

- Public holidays (Berlin): 2025-W52 (Christmas), 2026-W01 (New Year), 2026-W14 (Good Friday),
  2026-W15 (Easter Monday), 2026-W18 (1 May), 2026-W20 (Ascension Day), 2026-W22 (Whit Monday).
- 2026-W13: spring forward on 29 March, 334 intervals.
- 2026-W16: contact-centre tenant outage on Tuesday 14 April, 15:00–17:30 local without contacts
  (`docs/incidents/2026-04-21-contact-centre-tenant-outage.md`).

## Pause

Proseware paused the service from Friday 14 August 2026 while it reviews its service model. The last
week planned was 2026-W33. Config, roster and data stay as they are; a restart needs the next data
drop and nothing else from us.
"""
    wt = c["wingtip"]
    notes["docs/clients/wingtip.md"] = f"""\
# Wingtip Toys

{_table([
    ("Onboarded", "2026-02-09 (2026-W07)"),
    ("Account manager", "Ruth Abara"),
    ("Grain / timezone", "30 minutes / America/Phoenix"),
    ("Operating hours", "06:00–24:00 local, seven days"),
    ("Queues", "priority, standard (80 % in 20 s)"),
    ("Working time", "40 h full-time, 30 h part-time per week"),
    ("Config", "`configs/wingtip.yaml` (schema 2)"),
    ("Roster", "`data/agents/wingtip.csv`, " + _roster(wt["n_agents"], wt["n_pt"])),
    ("Data", "`data/wingtip/week_<ISO>.csv`, canonical as delivered"),
    ("Export layout", "`segments_json`, loaded through their workforce tool's import API"),
])}
## Time

Arizona does not observe daylight saving time. Wingtip is on UTC−7 all year, so its clock matches
US Pacific time in summer and US Mountain time in winter, and every week has 336 half-hour intervals.

## Data drop

Wingtip's platform writes the previous week's canonical file on Monday by 09:00 UTC. The
`segments_json` export goes back the same day.

## Contacts

Ruth Abara (account). Wingtip's workforce team owns the drop and the import.
"""
    return notes


# --------------------------------------------------------------------------------------------------
# docs/prs/  (#31 and #47 are written elsewhere)
# --------------------------------------------------------------------------------------------------

def _pr(num: int, title: str, merged: str, author: str, ticket: str, problem: str, change: str,
        approved: str, outcome: str) -> str:
    return (f"# PR #{num} — {title}\n\nMerged {merged} · Author: {author} · {ticket}\n\n"
            f"## Problem\n\n{problem}\n\n## Change\n\n{change}\n\n## Approved by\n\n{approved}\n\n"
            f"## Outcome\n\n{outcome}\n")


PR_NOTES = {
    "docs/prs/004-contoso-onboarding.md": _pr(
        4, "Contoso onboarding", "2024-11-29", "Dana Vexley", "WFM-006",
        "Contoso signed for weekly planning from 2024-W49 (Monday 2 December 2024). Its platform exports\n"
        "15-minute intervals in UTC for two queues, priority and standard, which is the shape the service\n"
        "plans in. Nothing in the service had yet run on a real client's week.",
        "- Contoso runs on the service defaults: 15-minute grain, UTC, 06:00–24:00, 80/20 on both queues.\n"
        "- Roster `data/agents/contoso.csv`: 40 agents, 8 of them part-time, skills as Contoso's team\n"
        "  leads listed them.\n"
        "- Drop folder and naming agreed: `week_<ISO>.csv`, canonical layout (ADR 0001), Mondays by 07:00 UTC.",
        "Dana Vexley (code). Sam Ferreira (Contoso account) for the drop arrangement. Joel Mbeki reviewed\n"
        "the dry-run schedule.",
        "Dry run on Contoso's sample week 2024-W47: all 672 intervals per queue present, 40 agents placed,\n"
        "no rule violations. Live from 2024-W49."),
    "docs/prs/009-tailspin-onboarding.md": _pr(
        9, "Tailspin onboarding", "2025-01-09", "Dana Vexley", "WFM-019",
        "Tailspin Toys starts on 2025-01-13 (2025-W03). It plans in 30-minute intervals on Irish time,\n"
        "opens 07:00–21:00, and contracts a slower answer target on its standard queue (80 % in 30 s).\n"
        "It is the first client that does not fit the service defaults.",
        "- Tailspin's settings: 30-minute grain, Europe/Dublin, operating hours 07:00–21:00, standard queue\n"
        "  at 80/30.\n"
        "- Roster `data/agents/tailspin.csv`: 30 agents, 6 part-time.\n"
        "- Converter for Tailspin's local-time export: UTC from the offset on each row.",
        "Joel Mbeki (schedule review). Tailspin's operations lead confirmed the operating hours.",
        "Dry run on the sample week 2025-W01: 336 intervals per queue, every day staffed 07:00–21:00, no\n"
        "rule violations. Live from 2025-W03. Client-specific settings need a proper home before the next\n"
        "client signs."),
    "docs/prs/014-adatum-onboarding.md": _pr(
        14, "Adatum onboarding", "2025-03-07", "Tomas Okafor", "WFM-034",
        "Adatum starts on 2025-03-10 (2025-W11): hourly intervals, US Mountain time, the service's default\n"
        "hours and targets. Second client off the defaults.",
        "- `configs/adatum.yaml`: `interval_minutes: 60`, `tz: America/Denver`. Everything else inherited\n"
        "  (ADR 0004).\n"
        "- Roster `data/agents/adatum.csv`: 30 agents, 6 part-time.\n"
        "- Converter for Adatum's hourly report (offset per row).",
        "Dana Vexley (review).",
        "Dry run on 2025-W09: 168 intervals per queue, no rule violations. Live from 2025-W11, the week\n"
        "after the US spring-forward."),
    "docs/prs/019-woodgrove-onboarding.md": _pr(
        19, "Woodgrove onboarding", "2025-05-08", "Tomas Okafor", "WFM-052",
        "Woodgrove Bank starts on 2025-05-12 (2025-W20): 30-minute intervals on US Pacific time,\n"
        "06:00–21:00, and a contractual 90 % in 30 s on the priority queue.",
        "- `configs/woodgrove.yaml`: grain, timezone, operating hours, and `sla` with both queues (the\n"
        "  overlay replaces `sla` whole, so the standard queue's 80/20 is restated).\n"
        "- Roster `data/agents/woodgrove.csv`: 40 agents, 8 part-time.\n"
        "- Converter for Woodgrove's export (Pacific wall-clock, no offset column).",
        "Dana Vexley (review). Joel Mbeki (schedule review).",
        "Dry run on 2025-W18: 336 intervals per queue, the 06:00 and 21:00 edges staffed by E8 and L8, no\n"
        "rule violations. Live from 2025-W20."),
    "docs/prs/024-volume-report.md": _pr(
        24, "Volume report: weekly totals, interval counts and zero-volume runs", "2025-07-03",
        "Mei Lindqvist", "WFM-071",
        "The telephony outage of 2025-06-24 reached four clients' data. Nothing looked at a drop before the\n"
        "weekly run, so three of the four were noticed only in the schedules\n"
        "(`docs/incidents/2025-07-01-telephony-platform-outage.md`). A missing or doubled hour around a DST\n"
        "change would go unnoticed the same way.",
        "- `python -m wfm report volume --client <c> [--from <week>] [--to <week>]`: per week, contacts and\n"
        "  handle time per queue, the peak interval, the interval count against the count the week should\n"
        "  have in the client's timezone, runs of zero-volume intervals inside operating hours, and the\n"
        "  change in total volume against the previous week on file.\n"
        "- `wfm/weeks.py`: ISO-week arithmetic and expected interval counts, shared with the report.\n"
        "- `wfm/report/markdown.py`: table rendering.",
        "Dana Vexley (review).",
        "Over every week on file it lists the 2025-06-24 outage for Contoso, Tailspin, Adatum and Woodgrove\n"
        "and nothing else; interval counts match on every week, including Tailspin's 2025-W13. Part of the\n"
        "Monday drop check from 2025-W27."),
    "docs/prs/028-eval-history.md": _pr(
        28, "Archive weekly evaluations; multi-week summary", "2025-07-11", "Mei Lindqvist", "WFM-077",
        "`out/<client>/eval.json` is overwritten by every run. Monthly account reviews rebuilt attainment\n"
        "and hours by re-running old weeks one at a time and copying numbers into a spreadsheet.",
        "- `python -m wfm report archive --client <c> --week <week>` copies the week's `eval.json` and\n"
        "  `schedule.csv` to `out/<client>/history/<week>/`, after checking that the evaluation is for that\n"
        "  client and week.\n"
        "- `python -m wfm report summary --client <c> [--from] [--to]`: per-queue attainment (mean, lowest\n"
        "  week), weeks meeting the target, scheduled hours, under- and over-staffed interval-hours and\n"
        "  rule-violation totals over the archived weeks, with one row per week.",
        "Dana Vexley (review). Sam Ferreira (summary layout for account reviews).",
        "Contoso's June review was produced from archived weeks 2025-W23 to 2025-W27 in one command.\n"
        "Archiving is a step of the weekly run from 2025-W28."),
    "docs/prs/039-schedule-export.md": _pr(
        39, "Schedule exports in the clients' layouts", "2025-08-20", "Mei Lindqvist", "WFM-093",
        "Each client imports the weekly schedule into its own workforce tool as next week's baseline. The\n"
        "files were made by hand from `schedule.csv`, in local time, five times a week.",
        "- `python -m wfm export --client <c> --week <week> --layout <layout>`, writing to\n"
        "  `out/<client>/export/` (ADR 0006).\n"
        "- `wfm/export/`: `activity_csv` (one row per work or break activity, local times and offset),\n"
        "  `roster_grid_csv` (one row per agent, a column per local day), `segments_json` (agents and\n"
        "  segments for tools that import through an API).\n"
        "- Exports read `schedule.csv` and the client config only, and refuse a week whose `eval.json` is\n"
        "  for another week.",
        "Dana Vexley and Tomas Okafor (review).",
        "From 2025-W34, Contoso, Adatum, Woodgrove and Fabrikam get `activity_csv`, Tailspin\n"
        "`roster_grid_csv`. The first exports matched the hand-made files for 2025-W33 apart from row order."),
    "docs/prs/050-config-schema-v2.md": _pr(
        50, "Client config schema 2", "2025-11-13", "Tomas Okafor", "WFM-121",
        "Proseware's onboarding sheet comes in sections that map onto the flat config badly, and a\n"
        "mistyped key in a flat file silently falls back to the default (ADR 0007).",
        "- `wfm/config.py`: a client file with `schema: 2` is flattened on load (`_flatten_v2`), with four\n"
        "  sections: service, targets, staffing, scheduling. Unknown sections and misplaced keys stop the\n"
        "  run with the key named.\n"
        "- Schema-1 files untouched; no client migrated.",
        "Dana Vexley (review). Mei Lindqvist.",
        "Every existing client's loaded config compared key by key before and after: identical. Proseware\n"
        "(PR #51) is the first schema-2 client."),
    "docs/prs/051-proseware-onboarding.md": _pr(
        51, "Proseware onboarding", "2025-11-14", "Tomas Okafor", "WFM-123",
        "Proseware starts on 2025-11-17 (2025-W47): 30-minute intervals on German time, 07:00–21:00, 85/20\n"
        "on priority and 80/30 on standard, and a works agreement of 39 hours full-time and 20 hours\n"
        "part-time.",
        "- `configs/proseware.yaml` in schema 2.\n"
        "- Roster `data/agents/proseware.csv`: 34 agents, 7 part-time.\n"
        "- Proseware's BI team delivers canonical files; no converter. Export layout `roster_grid_csv`.",
        "Sam Ferreira (Proseware account). Dana Vexley (review).",
        "Dry run on 2025-W45: 336 intervals per queue, no agent above the 39- and 20-hour caps, no rule\n"
        "violations. Live from 2025-W47."),
    "docs/prs/053-wingtip-onboarding.md": _pr(
        53, "Wingtip onboarding", "2026-02-05", "Mei Lindqvist", "WFM-146",
        "Wingtip Toys starts on 2026-02-09 (2026-W07): 30-minute intervals on Arizona time (no DST),\n"
        "06:00–24:00, 30-hour part-time contracts, and a workforce tool that imports schedules through an API.",
        "- `configs/wingtip.yaml` in schema 2.\n"
        "- Roster `data/agents/wingtip.csv`: 36 agents, 8 part-time.\n"
        "- Export layout `segments_json`; checked against Wingtip's import on their test tenant.",
        "Ruth Abara (Wingtip account). Tomas Okafor (review).",
        "Dry run on 2026-W05: 336 intervals per queue, no rule violations; Wingtip's test import accepted\n"
        "the file unchanged. Live from 2026-W07."),
    "docs/prs/055-notify-digests.md": _pr(
        55, "Weekly digests and agent shift lists", "2026-06-12", "Mei Lindqvist", "WFM-171",
        "The weekly status mail to each account manager was written by hand from `eval.json`, and team\n"
        "leads copied each agent's shifts out of the export to send round. Both took most of Monday\n"
        "afternoon and both had typos in them.",
        "- `python -m wfm notify --client <c> --week <week>` writes `out/<client>/notify/<week>/digest.txt`\n"
        "  (attainment against target per queue, hours, agents, understaffed hours, any rule violations)\n"
        "  and one shift list per agent in local time under `agents/`.\n"
        "- Nothing is sent from the service. The ops mailbox sends the digest; team leads forward the\n"
        "  shift lists.",
        "Ruth Abara and Sam Ferreira (digest wording). Dana Vexley (review).",
        "Used for every live client from 2026-W24."),
    "docs/prs/060-client-registry.md": _pr(
        60, "Client registry and `wfm clients`", "2026-10-14", "Tomas Okafor", "WFM-219",
        "Three clients have retired, Proseware is paused and Northwind is signed for 2026-W44. Which\n"
        "clients are live was known from the ops rota, not from the repository, and nothing checked that a\n"
        "client's config, roster and data agree with what we think the client is.",
        "- `clients/registry.yaml` and `clients/README.md`: every client, its status and lifecycle dates,\n"
        "  grain, timezone, queues, config schema, export layout and account manager (ADR 0008).\n"
        "- `wfm/registry.py` and `python -m wfm clients [--status <s>] [--markdown] [--check]`.\n"
        "- `export` takes the client's layout from the registry when `--layout` is not given; `notify`\n"
        "  takes the account manager from it.\n"
        "- `docs/OPERATIONS.md`: the weekly runbook, written down with the new commands.",
        "Dana Vexley and Mei Lindqvist (review).",
        "`--check` is clean for the seven configured clients; Northwind is listed as pending until its\n"
        "config lands with the go-live."),
}


# --------------------------------------------------------------------------------------------------
# docs/OPERATIONS.md
# --------------------------------------------------------------------------------------------------

OPERATIONS = """\
# Weekly operations

The weekly cycle for live clients: data drops, runs, exports, digests and the monthly summary. Times
are UTC. Commands run from the service root.

## The week

| when | what |
|---|---|
| Monday, 07:00–09:00 | clients drop the previous week's interval file (exact times in `docs/clients/<client>.md`) |
| Monday | check, commit, run and archive each drop |
| Monday, by 17:00 | exports to the clients' WFM teams, digests to the account managers |
| Tuesday, 12:00 | missing drops chased; the digest goes out marked "data pending" |
| first Monday of the month | multi-week summary for the account reviews |

The rota (Dana Vexley, Tomas Okafor, Mei Lindqvist) changes on Mondays. Account managers: Sam Ferreira
(Contoso, Proseware), Ruth Abara (Fabrikam, Wingtip). Joel Mbeki reads every digest before it goes.

## Which clients

`python -m wfm clients --status live` lists this week's clients. Paused and retired clients get no
weekly run (`docs/adr/0008-client-lifecycle.md`). `python -m wfm clients --check` once a week; it
should report nothing.

## Per client

`<c>` is the client key and `<week>` the week just ended, e.g. `2026-W42`; `<prev>` is the week before.

1. **Drop.** Put the file at `data/<c>/week_<week>.csv`. Clients with a converter (see their notes) are
   converted first; what is committed is always the canonical layout (`docs/adr/0001-canonical-interval-format.md`).
2. **Check.** `python -m wfm report volume --client <c> --from <prev> --to <week>`. Look at:
   - the interval count against the expected count for the week (DST weeks differ, see below);
   - zero-volume runs inside operating hours. Ask the client's WFM contact before running. A
     confirmed outage gets a note in `docs/incidents/`; the file is committed as delivered, never
     patched;
   - the change in total volume against `<prev>`.
3. **Commit.** `git add data/<c>/week_<week>.csv` and commit as `<Client> <week> data`.
4. **Run.** `python -m wfm run --client <c> --week <week>` writes `out/<c>/schedule.csv` and
   `out/<c>/eval.json`.
5. **Archive.** `python -m wfm report archive --client <c> --week <week>` keeps both files under
   `out/<c>/history/<week>/`.
6. **Export.** `python -m wfm export --client <c> --week <week>` writes the client's layout (from the
   registry) to `out/<c>/export/`. Send it to the client's WFM contact.
7. **Digest.** `python -m wfm notify --client <c> --week <week>` writes
   `out/<c>/notify/<week>/digest.txt` for the account manager (sent from the ops mailbox) and one shift
   list per agent under `out/<c>/notify/<week>/agents/` for the team leads.

## Late drops

A drop that is not there by Tuesday 12:00 is chased by the person on the rota, and the client's digest
goes out saying the data is pending. When the file arrives, the steps above run as normal and the
digest says it is late (`docs/incidents/2026-01-30-adatum-late-data-drop.md`).

## DST weeks

A week with a clock change has one hour more or fewer than 168. The volume report prints the count
the week should have in the client's timezone; a mismatch means the conversion is wrong, not that the
client sent a short week (`docs/incidents/2025-11-05-woodgrove-dst-fall-back-ingest.md`). Contoso
(UTC) and Wingtip (Arizona) never change; the European clients change on the last Sundays of March and
October, the US clients on the second Sunday of March and the first Sunday of November.

## Corrections and re-runs

A corrected file replaces the committed one in its own commit. Re-run, re-archive and re-export the
week and send the export again with a line saying what changed. Runs are deterministic
(`docs/adr/0003-deterministic-scheduling.md`), so a `diff` of the two `schedule.csv` files shows the
whole effect of the correction.

## Monthly summary

`python -m wfm report summary --client <c> --from <first week> --to <last week>` over the archived
weeks, for the account review. Archive first; a week that was never archived is not in the summary.

## Paused and retired clients

No drops and no weekly runs. Past weeks still run like any other: config, roster and data are kept.
"""


def files(clients: dict, weeks_for) -> dict[str, str]:
    out = dict(CONFIGS)
    out["clients/registry.yaml"] = REGISTRY
    out["clients/README.md"] = clients_readme()
    out.update(ADRS)
    out.update(INCIDENTS)
    out.update(client_notes(clients))
    out.update(PR_NOTES)
    out["docs/OPERATIONS.md"] = OPERATIONS
    return out
