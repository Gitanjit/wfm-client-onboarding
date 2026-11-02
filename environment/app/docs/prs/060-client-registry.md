# PR #60 — Client registry and `wfm clients`

Merged 2026-10-14 · Author: Tomas Okafor · WFM-219

## Problem

Three clients have retired, Proseware is paused and Northwind is signed for 2026-W44. Which
clients are live was known from the ops rota, not from the repository, and nothing checked that a
client's config, roster and data agree with what we think the client is.

## Change

- `clients/registry.yaml` and `clients/README.md`: every client, its status and lifecycle dates,
  grain, timezone, queues, config schema, export layout and account manager (ADR 0008).
- `wfm/registry.py` and `python -m wfm clients [--status <s>] [--markdown] [--check]`.
- `python -m wfm report accounts`: the latest archived week of every live and paused client, by
  account manager, for the Monday account call.
- `python -m wfm clients --board --week <week>`: one row per client served that week with the
  next open step of the weekly cycle (data, run, archive, export, digest).
  `python -m wfm clients --timeline`: every client's lifecycle month by month.
- `export` takes the client's layout from the registry when `--layout` is not given; `notify`
  takes the account manager from it.
- `docs/OPERATIONS.md`: the weekly runbook, written down with the new commands.

## Approved by

Dana Vexley and Mei Lindqvist (review).

## Outcome

`--check` is clean for the seven configured clients; Northwind is listed as pending until its
config lands with the go-live.
