"""Client registry: clients/registry.yaml -> one ClientRecord per client.

The registry holds lifecycle and planning facts: status, onboarded / ended / paused dates, grain,
timezone, queues, config schema, data format, export layout and account manager. The pipeline reads
configs, not the registry; `check()` reports where the two disagree, and where a client's data
files fall outside the weeks it was served (docs/adr/0008-client-lifecycle.md).

Statuses
  live        served every week since `onboarded`
  paused      served from `onboarded` up to (not including) `paused_from`; config, roster and data kept
  retired     served from `onboarded` to `ended` (last day served); config, roster, data and tests kept
  onboarding  not served yet; `golive_week` is the first week planned
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import yaml

from wfm import config, weeks
from wfm.report import history, volume
from wfm.report import markdown as md

REGISTRY_PATH = config.APP_DIR / "clients" / "registry.yaml"
STATUSES = ("live", "paused", "retired", "onboarding")
DATA_FORMATS = ("canonical", "export")
FIELDS = ("name", "status", "onboarded", "ended", "paused_from", "golive_week", "grain", "tz", "queues",
          "config_schema", "data_format", "export_layout", "account_manager", "notes")
DATA_FILE = re.compile(r"^(week|export)_(\d{4}-W\d{2})\.csv$")

ERROR, WARNING, PENDING = "error", "warning", "pending"


class RegistryError(ValueError):
    pass


@dataclass(frozen=True)
class ClientRecord:
    key: str
    name: str
    status: str
    onboarded: date | None
    ended: date | None
    paused_from: date | None
    golive_week: str | None
    grain: int
    tz: str
    queues: tuple[str, ...]
    config_schema: int | None
    data_format: str
    export_layout: str | None
    account_manager: str | None
    notes: str = ""

    @property
    def last_day(self) -> date | None:
        """Last day served: `ended` for a retired client, the day before `paused_from` for a paused one."""
        if self.status == "retired":
            return self.ended
        if self.status == "paused":
            return self.paused_from - timedelta(days=1)
        return None

    def active_on(self, d: date) -> bool:
        if self.status == "onboarding" or self.onboarded is None or d < self.onboarded:
            return False
        return self.last_day is None or d <= self.last_day

    def weeks_served(self, today: date | None = None) -> list[str]:
        """ISO weeks from the onboarding week to the week of the last day served (live: `today`)."""
        if self.status == "onboarding":
            return []
        end = self.last_day or today or date.today()
        if end < self.onboarded:
            return []
        return weeks.week_range(weeks.week_of(self.onboarded), weeks.week_of(end))


@dataclass(frozen=True)
class Problem:
    level: str        # error | warning | pending
    client: str
    text: str

    def __str__(self) -> str:
        return f"{self.client}: {self.level}: {self.text}"


def _date(key: str, field: str, v) -> date | None:
    if v is None or isinstance(v, date):
        return v
    try:
        return date.fromisoformat(str(v))
    except ValueError:
        raise RegistryError(f"{key}.{field}: not a date: {v!r}") from None


def _record(key: str, raw: dict) -> ClientRecord:
    unknown = sorted(set(raw) - set(FIELDS))
    if unknown:
        raise RegistryError(f"{key}: unknown field(s) {', '.join(unknown)}")
    missing = [f for f in ("name", "status", "grain", "tz", "queues", "data_format") if raw.get(f) is None]
    if missing:
        raise RegistryError(f"{key}: missing {', '.join(missing)}")
    rec = ClientRecord(
        key=key, name=str(raw["name"]), status=raw["status"],
        onboarded=_date(key, "onboarded", raw.get("onboarded")), ended=_date(key, "ended", raw.get("ended")),
        paused_from=_date(key, "paused_from", raw.get("paused_from")), golive_week=raw.get("golive_week"),
        grain=int(raw["grain"]), tz=str(raw["tz"]), queues=tuple(raw["queues"]),
        config_schema=raw.get("config_schema"), data_format=raw["data_format"],
        export_layout=raw.get("export_layout"), account_manager=raw.get("account_manager"),
        notes=raw.get("notes") or "")
    validate(rec)
    return rec


def validate(r: ClientRecord) -> None:
    """Field rules per status; raises RegistryError on the first problem."""
    if r.status not in STATUSES:
        raise RegistryError(f"{r.key}: status {r.status!r} is not one of {', '.join(STATUSES)}")
    if r.data_format not in DATA_FORMATS:
        raise RegistryError(f"{r.key}: data_format {r.data_format!r} is not one of {', '.join(DATA_FORMATS)}")
    if r.grain <= 0 or 60 % r.grain:
        raise RegistryError(f"{r.key}: grain {r.grain} does not divide an hour")
    try:
        ZoneInfo(r.tz)
    except (ZoneInfoNotFoundError, ValueError):
        raise RegistryError(f"{r.key}: unknown timezone {r.tz!r}") from None
    if not r.queues:
        raise RegistryError(f"{r.key}: no queues")
    if r.config_schema not in (None, 1, 2):
        raise RegistryError(f"{r.key}: config_schema {r.config_schema!r} is not 1 or 2")
    if r.status == "onboarding":
        if r.golive_week is None:
            raise RegistryError(f"{r.key}: an onboarding client needs golive_week")
        weeks.parse(r.golive_week)
        if r.onboarded or r.ended or r.paused_from:
            raise RegistryError(f"{r.key}: an onboarding client has no onboarded/ended/paused_from dates yet")
        return
    if r.onboarded is None:
        raise RegistryError(f"{r.key}: a {r.status} client needs onboarded")
    if r.config_schema is None:
        raise RegistryError(f"{r.key}: a {r.status} client needs config_schema")
    need = {"retired": "ended", "paused": "paused_from"}.get(r.status)
    for f in ("ended", "paused_from"):
        v = getattr(r, f)
        if f == need and v is None:
            raise RegistryError(f"{r.key}: a {r.status} client needs {f}")
        if f != need and v is not None:
            raise RegistryError(f"{r.key}: {f} is set but status is {r.status}")
        if v is not None and v <= r.onboarded:
            raise RegistryError(f"{r.key}: {f} {v} is not after onboarded {r.onboarded}")


def load_registry(path: Path | None = None) -> dict[str, ClientRecord]:
    """{client key: record} in file order."""
    path = path or REGISTRY_PATH
    try:
        doc = yaml.safe_load(path.read_text()) or {}
    except FileNotFoundError:
        raise SystemExit(f"no client registry at {path}") from None
    clients = doc.get("clients")
    if not isinstance(clients, dict) or not clients:
        raise RegistryError(f"{path}: expected a non-empty 'clients' mapping")
    return {k: _record(k, v or {}) for k, v in clients.items()}


def get(client: str, path: Path | None = None) -> ClientRecord:
    reg = load_registry(path)
    if client not in reg:
        raise SystemExit(f"client {client!r} is not in the registry ({', '.join(reg)})")
    return reg[client]


def by_status(records: dict[str, ClientRecord], status: str) -> list[ClientRecord]:
    if status not in STATUSES:
        raise SystemExit(f"unknown status {status!r}; one of {', '.join(STATUSES)}")
    return [r for r in records.values() if r.status == status]


def active_on(records: dict[str, ClientRecord], d: date) -> list[ClientRecord]:
    return [r for r in records.values() if r.active_on(d)]


def _file_schema(path: Path) -> int:
    doc = yaml.safe_load(path.read_text()) or {}
    return int(doc.get("schema", 1))


def _data_weeks(r: ClientRecord) -> dict[str, list[str]]:
    """{'week': [...], 'export': [...]} ISO weeks of the client's data files by layout."""
    found: dict[str, list[str]] = {"week": [], "export": []}
    d = config.DATA_DIR / r.key
    if d.is_dir():
        for p in sorted(d.iterdir()):
            m = DATA_FILE.match(p.name)
            if m:
                found[m.group(1)].append(m.group(2))
    return found


def _roster_skills(path: Path) -> set[str]:
    lines = path.read_text().splitlines()[1:]
    return {s for line in lines if line.strip() for s in line.split(",")[2].split(";")}


def check(r: ClientRecord, layouts=None, data: bool = False) -> list[Problem]:
    """Compare a record with configs/, data/ and data/agents/. An onboarding client without its
    config or roster yet is `pending`, not an error. `layouts`: known export layout names. `data`
    also reads every canonical week file and reports the volume report's file checks."""
    out: list[Problem] = []
    say = lambda level, text: out.append(Problem(level, r.key, text))   # noqa: E731
    cfg_file = config.CONFIG_DIR / f"{r.key}.yaml"
    roster = config.DATA_DIR / "agents" / f"{r.key}.csv"

    if not cfg_file.exists():
        if r.status == "onboarding":
            say(PENDING, f"no configs/{r.key}.yaml yet (go-live {r.golive_week})")
        else:
            say(ERROR, f"no configs/{r.key}.yaml")
    else:
        cfg = config.load_config(r.key)
        if cfg["interval_minutes"] != r.grain:
            say(ERROR, f"grain {r.grain} in the registry, interval_minutes {cfg['interval_minutes']} in the config")
        if cfg["tz"] != r.tz:
            say(ERROR, f"tz {r.tz} in the registry, {cfg['tz']} in the config")
        schema = _file_schema(cfg_file)
        if r.config_schema is not None and schema != r.config_schema:
            say(ERROR, f"config_schema {r.config_schema} in the registry, schema {schema} in the file")

    if not roster.exists():
        say(PENDING if r.status == "onboarding" else ERROR, f"no data/agents/{r.key}.csv")
    else:
        extra = sorted(_roster_skills(roster) - set(r.queues))
        if extra:
            say(WARNING, f"roster skills not among the registry queues: {', '.join(extra)}")

    if not (config.DATA_DIR / r.key).is_dir():
        say(PENDING if r.status == "onboarding" else ERROR, f"no data/{r.key}/ directory")
    files = _data_weeks(r)
    other = "export" if r.data_format == "canonical" else "week"
    if files[other]:
        say(WARNING, f"{len(files[other])} {other}_*.csv file(s) for a {r.data_format} client")
    if r.status != "onboarding":
        first = weeks.week_of(r.onboarded)
        last = weeks.week_of(r.last_day) if r.last_day else None
        for w in sorted(set(files["week"] + files["export"]), key=weeks.key):
            if weeks.key(w) < weeks.key(first) or (last and weeks.key(w) > weeks.key(last)):
                say(ERROR, f"data for {w} is outside the weeks served ({first} to {last or 'now'})")

    if data and cfg_file.exists():
        cfg = config.load_config(r.key)
        for w, path in volume.week_files(r.key).items():
            for issue in volume.file_issues(volume.read_week(path), cfg, w):
                say(ERROR, f"{path.name}: {issue}")

    if r.export_layout is not None and layouts is not None and r.export_layout not in layouts:
        say(ERROR, f"unknown export_layout {r.export_layout!r}")
    return out


def period(r: ClientRecord) -> tuple[str, str]:
    if r.status == "onboarding":
        return f"go-live {r.golive_week}", md.DASH
    end = {"retired": r.ended, "paused": r.paused_from}.get(r.status)
    return str(r.onboarded), md.DASH if end is None else f"{end} ({r.status})"


def render_markdown(records: list[ClientRecord]) -> str:
    """The client table: one row per client in the order given."""
    rows = []
    for r in records:
        start, end = period(r)
        rows.append([r.key, r.name, r.status, start, end, f"{r.grain} min", r.tz, ", ".join(r.queues),
                     md.DASH if r.config_schema is None else f"v{r.config_schema}",
                     r.export_layout or md.DASH, r.account_manager or md.DASH])
    return md.table(["client", "name", "status", "onboarded", "ended / paused", "grain", "tz", "queues", "config",
                     "export", "account manager"], rows, align="lllllrlllll")


def latest_eval(r: ClientRecord, out_dir: Path) -> dict | None:
    """The client's most recent archived eval (out/<client>/history/), if any."""
    done = history.archived_weeks(r.key, out_dir)
    return history.read_eval(history.history_dir(r.key, out_dir) / done[-1] / "eval.json") if done else None


def accounts_table(records: list[ClientRecord], out_dir: Path) -> str:
    """One line per client from its latest archived week: the weakest queue, target verdict, hours
    and agents. Grouped by account manager (unassigned last), clients in registry order."""
    body = []
    for r in sorted(records, key=lambda r: (r.account_manager is None, r.account_manager or "")):
        ev = latest_eval(r, out_dir)
        if ev is None:
            body.append([r.account_manager or md.DASH, r.key, r.status, md.DASH, md.DASH, md.DASH, md.DASH, md.DASH])
            continue
        q, v = min(ev["sla"].items(), key=lambda kv: (kv[1], kv[0])) if ev.get("sla") else (md.DASH, None)
        body.append([r.account_manager or md.DASH, r.key, r.status, ev["week"], f"{q} {md.ratio(v)}",
                     md.yes_no(ev.get("meets_target")), md.num(ev.get("scheduled_hours")), ev.get("agents_scheduled")])
    return md.document(md.heading("Accounts - latest archived week per client", 1),
                       md.table(["account manager", "client", "status", "week", "weakest queue", "meets target",
                                 "hours", "agents"], body, align="llllllrr"))
