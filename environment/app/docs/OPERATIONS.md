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
