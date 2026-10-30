<!-- canary: collinear-candidate wfm-client-onboarding 2026-10 gm -->

# Onboard client "Northwind" into the WFM service

You are the engineer on call for a small workforce-management (WFM) service at `/app`. It already
serves two clients, **Contoso** and **Fabrikam**: given a client's interval demand data it produces a
weekly agent schedule and an evaluation. Read `/app/docs/ARCHITECTURE.md` first.

A new client, **Northwind**, must be onboarded for ISO week **2026-W44**. Their contract is in
`/app/docs/NORTHWIND_SOW.md`; their data and a data note are in `/app/data/northwind/`. The SOW states
service-level targets and scheduling rules that the current system does not all support. Known issues are
listed in `/app/docs/CHANGELOG.md`.

## Deliverables (all paths absolute)

1. Code and configuration changes under `/app` such that
   `cd /app && python -m wfm run --client northwind --week 2026-W44`
   writes `/app/out/northwind/schedule.csv` and `/app/out/northwind/eval.json`
   (schemas in `/app/docs/ARCHITECTURE.md`). The same command must work for any other week of
   Northwind data placed in `/app/data/northwind/`.
2. `/app/out/northwind/RUNBOOK.md` containing the reconciliation table defined in SOW §3 (exact keys),
   and a short note of what you changed and why.
3. Contoso and Fabrikam must continue to run with `python -m wfm run --client <name> --week <week>` and
   must not get worse. Their contracts and config files are not in scope for this work.

## Constraints

- Northwind's schedule must satisfy every rule in SOW §2 for the whole week.
- Service-level targets and the occupancy cap come from the SOW. Config files describe the system's
  settings; they do not change what the contract requires.
- Do not change the system's defaults to suit one client; add client-specific configuration.
- Shift templates are in each client's local time and never cross local midnight; weekly-hour caps and
  rest periods are measured in elapsed time (see ARCHITECTURE.md).
- No package installation is possible; everything needed is already installed.

## How this is graded

Your `schedule.csv` for Northwind 2026-W44, and schedules produced by your system for a following week
of Northwind data and for Contoso's and Fabrikam's next week, will be evaluated by an **independent
implementation** of the SOW definitions (service level, occupancy, rules, costs). Editing
`/app/wfm/evaluate/` is allowed but does not affect grading. Grading checks: SLA attainment per queue
and total scheduled hours relative to a reference solution; zero violations of SOW §2 rules; no
regression for existing clients; and that the RUNBOOK figures match recomputation from your outputs.

You have 90 minutes. A careful engineer completes this in about an hour.
