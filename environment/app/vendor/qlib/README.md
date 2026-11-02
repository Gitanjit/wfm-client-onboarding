# qlib (vendored)

Version 1.3.0. Small queueing library: Erlang B, Erlang C and an Erlang A approximation with
caller abandonment. Pure Python, no dependencies. MIT licence (see LICENSE).

Kept in-tree for Fabrikam's abandonment model (`queueing: qlib` in `configs/fabrikam.yaml`). The
service's own Erlang C is `wfm/staffing/erlang.py`.

Tests: `python -m pytest -q vendor/qlib/tests` from the service root.
