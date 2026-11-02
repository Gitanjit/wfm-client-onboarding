"""Text files for tools/volume/gen_world.py: client configs, the client registry and its README, and
the service docs. Every date, number and name here agrees with tools/volume/WORLD.md and with the
data gen_world.py writes."""
from __future__ import annotations

# --------------------------------------------------------------------------------------------------
# configs
# --------------------------------------------------------------------------------------------------

CONFIGS = {
    "configs/tailspin.yaml": """\
# Tailspin Toys — canonical 30-minute files, Irish time. Retired 2025-10-31; kept for re-runs.
name: Tailspin Toys
interval_minutes: 30
tz: Europe/Dublin
operating_hours: [7, 21]
sla:
  priority: {target: 0.80, seconds: 20}
  standard: {target: 0.80, seconds: 30}
""",
    "configs/adatum.yaml": """\
# Adatum — canonical hourly files, US Mountain time. Retired 2026-03-27; kept for re-runs.
name: Adatum
interval_minutes: 60
tz: America/Denver
sla_target: 0.85
""",
    "configs/woodgrove.yaml": """\
# Woodgrove Bank — canonical 30-minute files, US Pacific time. Retired 2026-01-16; kept for re-runs.
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
# Paused at the client's request from 2026-08-14.
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
  sla_target: 0.90
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
  sla_target: 0.90
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

Client notes: `docs/clients/<client>.md`. Northwind: `docs/NORTHWIND_SOW.md` and
`data/northwind/README.txt`. Lifecycle rules: `docs/adr/0008-client-lifecycle.md`.
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
    notes: Contract not renewed; last week served 2025-W44.
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
    notes: Statement of work in docs/NORTHWIND_SOW.md; demand export format in data/northwind/README.txt.
"""


def files(clients: dict, weeks_for) -> dict[str, str]:
    out = dict(CONFIGS)
    out["clients/registry.yaml"] = REGISTRY
    out["clients/README.md"] = clients_readme()
    return out
