# qlib changelog

## 1.3.0
- `DEFAULT_PATIENCE_SEC` changes from 0 (no abandonment) to 90 s, the median caller patience in the
  2024 industry survey. Callers that do not pass `patience_sec` now get the Erlang A model and a
  higher service level for the same agents. Pass `patience_sec=0` for the 1.2 behaviour.
- `asa()` returns a finite mean wait for overloaded queues when patience is set.

## 1.2.0
- `required_agents()` accepts `occupancy_cap`; occupancy uses carried traffic.
- `achieved()` helper: service level for a given volume, handle time and agent count.

## 1.1.0
- Erlang A approximation (`patience_sec`), off by default.
- `abandon_probability()`.

## 1.0.0
- Erlang B (stable recurrence), Erlang C, service level, ASA, `required_agents()`.
