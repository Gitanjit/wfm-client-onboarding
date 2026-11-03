<!-- canary: wfm-client-onboarding 2026-10 gm -->

# Onboard Litware; Northwind's March data is in

It is March 2027. The workforce-management service at `/app` serves Contoso, Fabrikam and Northwind;
Northwind was onboarded in ISO week 2026-W44. A fourth client, Litware, goes live in ISO week 2027-W11.
Their contract is `/app/docs/LITWARE_SOW.md`. Their demand exports for 2027-W10 and 2027-W11 and a note
on the format are in `/app/data/litware/`; their roster is `/app/data/agents/litware.csv`. Northwind's
export for 2027-W10 has also arrived in `/app/data/northwind/`.

## Deliverables (absolute paths)

1. Code and configuration changes under `/app` so that
   `cd /app && python -m wfm run --client litware --week 2027-W11`
   writes `/app/out/litware/schedule.csv` and `/app/out/litware/eval.json` (schemas in
   `/app/docs/ARCHITECTURE.md`). The same command must work for any other week of Litware data
   dropped into `/app/data/litware/`.
2. `/app/out/litware/RUNBOOK.md` for 2027-W11 with the table, the Exceptions section and the handover
   note from Litware SOW §3 (what you changed and why, and what SOW §2.8 asks for).
3. Contoso, Fabrikam and Northwind still run for any week of their data and do not get worse.
   Northwind still meets its SOW in every week, §2.7 included.

## Constraints

- Litware's schedule satisfies every rule in Litware SOW §2 for the whole week, and stays within the
  efficiency bound in §1.6.
- Service-level targets and the occupancy cap come from each client's SOW. Config files describe what
  the system does; they do not change what a contract requires.
- Do not change the service defaults to suit one client. Add client-specific configuration.
- Nothing can be installed. Everything you need is already in the image.

## Grading

An independent implementation of each SOW will evaluate: Litware's 2027-W11 `schedule.csv`; schedules
your system produces for other weeks of Litware and Northwind data; and schedules for Contoso's,
Fabrikam's and Northwind's earlier weeks. The checks: SLA attainment per queue and total scheduled hours
against each SOW's §1.6; zero violations of each SOW's §2, including the §2.6 report; no regression for
the existing clients; attainment each client's `eval.json` reports, and RUNBOOK figures, that match a
recomputation from your outputs (Litware SOW §1.7); and the §2.8 handover note.

You have 90 minutes.
