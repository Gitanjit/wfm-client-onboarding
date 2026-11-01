# Real-path rewards (Harbor trials, separate verifier)

Kept so the before/after of the `seed-v1` freeze is on record.

| job | commit | what | overall |
|---|---|---|---|
| p5pre-oracle-1 | 7808bbd (pre-rewrite: docs still in the planning drafts' wording) | oracle | 1.0 |
| p5pre-nop-1 | 7808bbd | nop | 0.25 |

- `p5pre-oracle-2` / `p5pre-nop-2`: commit after the Tier 1 realism levers (git history in the image, greedy_v2, tests_unit, aht_smoothing, mis-typed labels), still before the doc rewrite.

`single-v1` (efficiency bound, held-out 2027-W10, L11): s1-oracle-1 → 1.0 (1 m 24 s incl. forced build), s1-nop-1 → 0.25;
a fresh `git clone` with `--force-build` gave a reward.json byte-identical to s1-oracle-1. No exception on any trial.

`multi-v1` (two steps, `mean`): m1-oracle-1 → 1.0 / 1.0 (22 m 16 s: each verifier phase closed ~10 min after its grader);
m1-nop-1 → 0.25 / 0.114, trial 0.182; m1-oracle-2 (verifier timeout 1800 s) → 1.0 / 1.0, verifiers 37 s / 39 s.
Per-step reward.json + checks.json: `m1-*.<step>.reward.json`.
