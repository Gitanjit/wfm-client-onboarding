# Northwind — SOW §2.7 exceptions

Targets in `docs/NORTHWIND_SOW.md` that the roster in `data/agents/northwind.csv` cannot meet. Attainment
as defined in SOW §1 (operating intervals meeting §1.2, Erlang C at the interval's own volume and AHT,
occupancy cap 0.85, agents on the queue net of breaks). Raise with the Northwind account team.

| queue | week | achievable | shortfall |
|---|---|---|---|
| vip | 2026-W44 | 0.911 | 0.039 |

- Target: weekly attainment ≥ 0.950 on `vip` (SOW §1.6). Achieved 153 of 168 vip operating intervals
  (08:00–20:00 local); 15 intervals short, mostly weekdays 08:00–09:00 and the 10:30 / 15:00 peaks.
- Cause: only 11 agents hold the `vip` skill (7 vip-only and 4 priority;vip, all FT, 440 agent-hours a
  week at most). In the schedule the vip-skilled agents work 438 h, all of it on `vip`. VIP needs ~306 required agent-hours plus the
  §2.6 cover from 06:00 to 08:00 and 20:00 to 24:00 (42 h). The 8-hour templates don't fit a 08:00–20:00
  demand curve (nothing starts at 08:00), each long shift carries a §2.3 break, and the 11-hour rest rule
  stops an evening shift being followed by an early one. Full weekday cover would take ~11 vip shifts a day
  against ~8 available.
- What would close it: about 2–3 more vip-skilled agents (or vip skill for some of the 13 FT
  priority;standard agents), or a template starting at 08:00. Priority and standard both reach 1.000 with
  room to spare, so cross-training is the cheaper option.
- Other targets met: priority 1.000, standard 1.000 (≥ 0.950); scheduled hours 1682.0 ≤ 1.57 × 1115.5 =
  1751.3 (ratio 1.508); §2 rules: no violations.
