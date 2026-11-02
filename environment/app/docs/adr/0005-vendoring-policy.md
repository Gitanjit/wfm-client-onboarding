# 0005 — Vendoring third-party code

Date: 2025-08-08 · Status: accepted · Author: Mei Lindqvist

## Context

The Fabrikam pilot, starting 2025-08-11, plans with a queueing model that includes caller abandonment.
The service's own Erlang C (`wfm/staffing/erlang.py`) has none. qlib, a small MIT-licensed queueing
library, provides one. The service's runtime dependencies are pandas, numpy and pyyaml, pinned, and we
want to keep it that way.

## Decision

- Third-party code the service runs lives under `vendor/<name>/` and is imported as `vendor.<name>`.
- Only pure-Python packages without dependencies of their own are vendored.
- Each vendored package keeps its `LICENSE`, its `README.md` (stating the version), its `CHANGELOG.md`
  and its own tests; `python -m pytest -q vendor/<name>/tests` passes.
- No local edits inside `vendor/`. A change the service needs goes upstream or into a wrapper under
  `wfm/`.
- An upgrade replaces the package directory in one commit whose message names the old and the new
  version.

## Consequences

- The service's Erlang C remains the model every client uses by default; a vendored model is chosen
  per client in its config.
- The runtime dependency list stays at three pinned packages.
