# Clients

Every client the service has planned for, oldest first. `clients/registry.yaml` holds the same facts
in machine-readable form: `python -m wfm clients` lists them and `python -m wfm clients --check`
compares them with `configs/`, `data/` and the rosters in `data/agents/`.

| client | name | status | onboarded | ended / paused | grain (min) | timezone | queues | config schema |
|---|---|---|---|---|---|---|---|---|
| contoso | Contoso | live | 2024-12-02 | — | 15 | UTC | priority, standard (chat 2025-07-21 to 2025-09-01) | 1 (flat) |
| tailspin | Tailspin Toys | retired | 2025-01-13 | ended 2025-10-31 | 30 | Europe/Dublin | priority, standard | 1 (flat) |
| adatum | Adatum | retired | 2025-03-10 | ended 2026-03-27 | 60 | America/Denver | priority, standard | 1 (flat) |
| woodgrove | Woodgrove Bank | retired | 2025-05-12 | ended 2026-01-16 | 30 | America/Los_Angeles | priority, standard | 1 (flat) |
| fabrikam | Fabrikam | live | 2025-08-11 (pilot); renewed 2025-10-06 | — | 60 | America/New_York | priority, standard | 1 (flat) |
| proseware | Proseware | paused | 2025-11-17 | paused 2026-08-14 | 30 | Europe/Berlin | priority, standard | 2 (nested) |
| wingtip | Wingtip Toys | live | 2026-02-09 | — | 30 | America/Phoenix | priority, standard | 2 (nested) |
| northwind | Northwind Traders | onboarding (go-live 2026-W44) | — | — | 30 | America/Chicago | priority, standard, vip | pending |

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
