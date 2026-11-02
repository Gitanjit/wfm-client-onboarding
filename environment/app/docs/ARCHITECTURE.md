# WFM service — architecture notes

A small workforce-management service. It takes a client's interval demand and writes a weekly agent
schedule and an evaluation.

## Pipeline

    data/<client>/*.csv  →  wfm.ingest    →  canonical intervals (UTC, client grain)
                         →  wfm.staffing  →  required agents per queue per interval (Erlang C)
                         →  wfm.constraints → per-queue minimum cover (floors), where a client has them
                         →  wfm.scheduler →  out/<client>/schedule.csv (greedy template placement)
                         →  wfm.evaluate  →  out/<client>/eval.json

Run: `python -m wfm run --client <name> --week <YYYY-Www>` from `/app`.

Modules: `wfm/config.py` (config loading), `wfm/ingest/loader.py`, `wfm/staffing/erlang.py` and
`required.py`, `wfm/constraints.py` (minimum cover), `wfm/roster.py` (agents), `wfm/scheduler/templates.py`
and `greedy.py`, `wfm/evaluate/metrics.py`, `wfm/cli.py`. Anything else under `wfm/scheduler/` is a draft;
see `CHANGELOG.md`.

Queueing. `wfm/staffing/erlang.py` is the service's Erlang C and the method of record. `vendor/qlib`
(a vendored queueing library with an abandonment model) is kept for Fabrikam's abandonment model;
`queueing: qlib` in a client config routes that client's staffing through it.

History and tickets: `git log` in `/app`. Tickets are WFM-nnn.
<!-- G: your call — keep this line? It points at the history without saying what is in it -->

## Configuration

`configs/defaults.yaml` holds the service-wide settings: planning grain, timezone, operating hours,
occupancy cap, handle-time smoothing, SLA targets, break rules, hour caps. `configs/<client>.yaml`
overrides any top-level key for that client. To add a client, add its config file and its data
directory; the CLI refuses a client without a config file. Do not change `defaults.yaml` to suit one
client. Every client without an override inherits it.

## Canonical intervals (output of ingest)

| column | notes |
|---|---|
| client, queue | queues are `priority` and `standard` |
| interval_start_utc | ISO 8601, `Z` |
| interval_minutes | 15 / 30 / 60 per client |
| volume | contacts arriving in the interval |
| aht_sec | average handle time for the interval |

Existing clients deliver canonical files (`data/<client>/week_<ISO>.csv`). The loader also reads a
client's own local-time export (`data/<client>/export_<ISO>.csv`), kept from Fabrikam's first
onboarding. Ingest resamples to the client's configured grain and gives one row per queue per
interval of the ISO week in the client's timezone. A week has as many intervals as its elapsed length
requires. A DST transition changes the count.

## Agents and templates

`data/agents/<client>.csv`: `agent_id, contract (FT|PT), skills (semicolon-separated)`.

Templates (`wfm/scheduler/templates.py`) are local wall-clock segments. None crosses local midnight.
Only templates that fit inside the client's operating hours are used.

| id | segments (local) | hours |
|---|---|---|
| E8 | 06:00–14:00 | 8 |
| D8 | 09:00–17:00 | 8 |
| L8 | 13:00–21:00 | 8 |
| N8 | 16:00–24:00 | 8 |
| P6a | 07:00–13:00 | 6 |
| P6b | 15:00–21:00 | 6 |
| P4 | 10:00–14:00 | 4 |
| S44 | 08:00–12:00 + 16:00–20:00 | 4+4 (split) |

Shift durations, weekly-hour caps and rest periods are elapsed time (UTC). An agent takes at most one
template per local day.
<!-- G: your call — one worked example of "elapsed" across the DST night? (I would not; the SOW says it) -->

## schedule.csv

`agent_id, queue, segment_start_utc, segment_end_utc, template_id, segment_idx, break_start_utc, break_minutes`.
One row per segment. The break row is the segment that contains it. `break_minutes` is 20 or 0.
`break_start_utc` is empty when the segment has no break. Times are ISO 8601 `Z`.

## eval.json

`intervals`, attainment per queue (`sla`, on the client's `attainment_basis`: `service_level` by
default), `meets_target` (attainment at or above the configured `sla_target`), `scheduled_hours`, `understaffed_interval_hours`, `overstaffed_interval_hours`,
`agents_scheduled`, and `violations` keyed by rule name. The evaluator is a convenience for engineers.
Contractual evaluation is done independently against each client's SOW.

## Tests

`python -m pytest -q tests_unit` from `/app`. Run it before committing. The suite pins current behaviour.
<!-- G: your call — "pins current behaviour" is the honest hint that the tests can be wrong; keep or drop -->

## Known issues

See `CHANGELOG.md`.
