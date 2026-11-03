# Agent's final message (verbatim, step 44)

Litware's 2027-W11 run is in place and clean. `python -m wfm run --client litware --week 2027-W11` writes `schedule.csv`, `eval.json`, `RUNBOOK.md` and `exceptions.md` to `/app/out/litware/`. Northwind's vip target is still below 0.95 and I have not resolved that (details below).

My own checker, written from the SOW text and not importing `wfm`, finds zero §2 violations for W11. It also finds attainment of 1.000 on all three queues. Scheduled hours are 722.0 against a 1.45× bound of 764.2. Its attainment and required hours match `eval.json` and the RUNBOOK. W10 passes the same way. The full test suite passes (90 tests) and `wfm clients --check` is clean.

What I changed:
- **Ingest:** Litware stamps each row with the end of its interval. The loader now converts the stamp to UTC using the row's offset and steps back one 20-minute interval. Reading the stamps as starts would have put all demand 20 minutes late.
- **Config:** `configs/litware.yaml` holds everything client-specific, including the three queues, email arriving 07:00–19:00, the SOW's targets, the occupancy cap, the two-agent priority minimum, and the 1.45 hours bound. `defaults.yaml` only gained `queue_start: {}`, which changes nothing for other clients.
- **Email start (§2.5/§2.6):** a new `queue_start: {email: 9}` setting stops email shifts starting before 09:00. The 42 email intervals a week before 09:00 are reported under `## Exceptions` in the RUNBOOK. They stay in `intervals_in_week` and required hours but are left out of attainment and understaffed hours.
- **Report:** `wfm/report/sow.py` now writes Litware's RUNBOOK with the §3 table, the Exceptions section, the handover note and the §2.8 list of nine pre-existing deviations.
- **Housekeeping:** I added the registry entry, the clients README row, `docs/clients/litware.md`, the architecture and changelog entries, and `tests_unit/test_litware.py`.

Beyond W10 and W11, I ran Litware on synthetic weeks to check the "any other week" requirement. A 167-hour DST week (W12) and weeks with volume scaled ×1.4 and ×0.6 (W13, W14) all pass the same checks. I deleted those synthetic data files, so only the real W10 and W11 exports remain.

Contoso, Fabrikam and Northwind outputs are byte-identical to the baseline I captured before any edits, for every week of data. My first Litware scheduler change did alter Northwind, so I made that path apply only to clients with `queue_start`.

Northwind's vip attainment is below 0.95 in the baseline: 0.929 in W43, 0.893 in W10 and below target in W44. `exceptions.md` records this as a roster limit, and `docs/clients/northwind.md` says vip would need about 540 hours. My rough lower bound says a 95% vip target needs only about 340 gross hours, against the 440 the eleven vip-skilled agents can work. That bound ignores rest rules, the fixed shift shapes and the five-day limit, so it doesn't prove the target is reachable, but it also doesn't support the "unreachable" claim. I couldn't settle it because no solver is installed. I left Northwind unchanged, as you asked for no regression, but someone should check whether the roster limit is real.

I didn't commit anything; all changes are uncommitted in the working tree.
