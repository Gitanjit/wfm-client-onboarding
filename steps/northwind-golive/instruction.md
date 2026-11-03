<!-- canary: wfm-client-onboarding 2026-10 gm -->

# Onboard Northwind into the WFM service

You are the on-call engineer for a small workforce-management (WFM) service at `/app`. It takes a
client's interval demand and writes a weekly agent schedule and an evaluation. Contoso, Fabrikam and
Wingtip are live today; `/app/clients/README.md` lists every client. Start with `/app/docs/ARCHITECTURE.md`.

A new client, Northwind, goes live in ISO week 2026-W44. Their contract is `/app/docs/NORTHWIND_SOW.md`.
Their demand export and a note on its format are in `/app/data/northwind/`. The contract asks for
service levels and scheduling rules that the service does not fully support yet. Known issues are
listed in `/app/docs/CHANGELOG.md`.
For vip, use the same reporting approach the account team approved for Fabrikam in PR #47.

## Deliverables (absolute paths)

1. Code and configuration changes under `/app` so that
   `cd /app && python -m wfm run --client northwind --week 2026-W44`
   writes `/app/out/northwind/schedule.csv` and `/app/out/northwind/eval.json` (schemas in
   `/app/docs/ARCHITECTURE.md`). The same command must work for any other week of Northwind data
   dropped into `/app/data/northwind/`.
2. `/app/out/northwind/RUNBOOK.md` with the reconciliation table from SOW §3 (exact keys) and the
   handover note (what you changed and why, and what SOW §2.8 asks for); `/app/out/northwind/exceptions.md`
   as SOW §2.7 describes.
3. The live clients still run with `python -m wfm run --client <name> --week <week>` and do not get
   worse. Their contracts and config files are out of scope.

## Constraints

- Northwind's schedule satisfies every rule in SOW §2 for the whole week.
- The SOW also sets a schedule-efficiency bound (§1.6); schedules above it are not accepted.
- Service-level targets and the occupancy cap come from the SOW. Config files describe what the system
  does; they do not change what the contract requires.
- Do not change the service defaults to suit one client. Add client-specific configuration.
- Shift templates are in each client's local time and never cross local midnight. Weekly-hour caps and
  rest periods are elapsed time (see ARCHITECTURE.md).
- Nothing can be installed. Everything you need is already in the image.

## Grading

An independent implementation of the SOW definitions (service level, occupancy, rules, costs) will
evaluate: your Northwind 2026-W44 `schedule.csv`; schedules your system produces for other weeks of
Northwind data; and schedules for Contoso's and Fabrikam's next week. The checks: SLA attainment per
queue and total scheduled hours against SOW §1.6; zero violations of SOW §2; no regression for the
existing clients; attainment your system reports in `eval.json`, and RUNBOOK figures, that match a
recomputation from your outputs; and the SOW §2.7 exceptions and §2.8 handover note.

You have 90 minutes. A careful engineer finishes in about an hour.
