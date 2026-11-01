# Agent's final message (verbatim, step 50)

Litware now runs end to end: `python -m wfm run --client litware --week 2027-W11` writes `out/litware/schedule.csv`, `eval.json` and `RUNBOOK.md`. I checked the 2027-W11 schedule with a separate script that re-reads the raw export and recomputes Erlang C. It found zero violations of SOW §2.

| Check | 2027-W11 |
|---|---|
| Attainment (priority / standard / email) | 1.000 / 0.997 / 1.000 |
| Scheduled vs required hours | 718.0 vs 527.0, ratio 1.36 (bound 1.45) |
| Exceptions | 42, all email intervals from 07:00 to 09:00 local |

- **Misses:** one standard interval is still short, Tuesday 08:40, which needs 3 agents. Only the 07:00 shifts reach it, and no template starts at 08:40.
- **RUNBOOK:** the table values match my recomputation, and it has the Exceptions section and the change note.
- **Other Litware weeks:** I also ran 2027-W10, a synthetic week with the 2027-03-28 clock change (501 intervals), and a synthetic week with 30% more volume. All had zero violations and attainment of 0.99 or better. The synthetic exports are deleted.
- **Other clients:** Contoso, Fabrikam and Northwind (W42–W44 and 2027-W10) produce schedules identical to before. Northwind 2027-W10 still meets its SOW: 334 intervals across the March DST change, hours ratio 1.559 against the 1.57 bound. `eval.json` for Northwind just gains two audit keys.
- **Tests:** 18 pass.

What changed:
- **Config:** `configs/litware.yaml` carries the SOW values. `defaults.yaml` is untouched.
- **Ingest:** Litware's export stamps the end of each interval, so a row labelled 09:20 covers 09:00–09:20. Reading it as a start would have shifted the demand curve 20 minutes late.
- **Staffing and scheduler:** the priority floor of two is kept separate from the Erlang C requirement. The email 09:00 start applies in scheduling and trimming. Unreachable email intervals are listed as exceptions, not covered. The scheduler can now lengthen an existing shift, and it repeats repair and trim from rebuilt agent state; the old single pass left the end of the week short.
- **Evaluator and runbook:** both are extended for the new rules and the Exceptions section.
- **Docs:** `ARCHITECTURE.md`, `CHANGELOG.md` and `docs/litware_runbook_notes.md` are updated.

Judgment calls to check against your own reading of the SOW:
- **Split shifts:** I excluded the split template (S44) for Litware, because §2.3 doesn't say whether two 4-hour segments count as one shift for the break rule. The plan still meets every target without it, and Northwind keeps it.
- **Break surplus:** it is measured against the plain Erlang requirement, not the priority floor of two.
- **Attainment:** operating intervals are all 07:00–21:00 intervals on every queue, minus exceptions.

I didn't commit anything. The earlier Northwind work was already uncommitted in the tree, so my edits sit on top of it.
