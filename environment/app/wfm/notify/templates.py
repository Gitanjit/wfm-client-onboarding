"""Texts for the weekly notifications. `string.Template` placeholders; the renderers in digest.py and
agents.py fill them. Wording changes go here, not in the renderers."""
from __future__ import annotations

from string import Template

DIGEST = Template("""\
To: $recipients
Subject: $name - schedule for $week_label

$name, week $week. Times are local ($tz).

Attainment against the evaluator target ($target per queue)
$attainment

Scheduled: $hours h across $agents agent(s) ($contracts).
Interval-hours understaffed: $under; overstaffed: $over.

$previous

Shifts per local day
$days

Rule checks
$rules

Files: out/$client/schedule.csv, out/$client/eval.json.
""")

AGENT = Template("""\
$agent_id ($contract) - $name, week $week_label
Times are local ($tz).

$shifts

Total: $hours h of a weekly cap of $cap h.
""")

DAY_SHEET = Template("""\
$name - $day_label. Times are local ($tz).
$shifts shift(s), $hours h.

Shifts in start order
$starts

On shift by hour
$headcount
""")

NO_SHIFTS = "No shifts this week."
NO_SHIFTS_DAY = "No shifts this day."
DAY_OFF = "off"
RULES_CLEAN = "  No rule violations."
WFM_TEAM = "WFM team"
NO_PREVIOUS = "No earlier archived week to compare with."
