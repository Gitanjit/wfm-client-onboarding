import json
from datetime import date

import pytest
import yaml

from wfm import config, registry
from wfm.export import LAYOUTS

GOOD = {"name": "NewCo", "status": "live", "onboarded": "2026-01-05", "grain": 30, "tz": "Europe/Dublin",
        "queues": ["priority", "standard"], "config_schema": 1, "data_format": "canonical",
        "export_layout": "activity_csv"}


def _registry(tmp_path, **clients):
    p = tmp_path / "registry.yaml"
    p.write_text(yaml.safe_dump({"clients": clients}))
    return p


def test_registry_lists_every_client_in_file_order():
    reg = registry.load_registry()
    assert list(reg) == ["contoso", "tailspin", "adatum", "woodgrove", "fabrikam", "proseware", "wingtip", "northwind"]
    assert [r.key for r in registry.by_status(reg, "retired")] == ["tailspin", "adatum", "woodgrove"]
    assert [r.key for r in registry.by_status(reg, "live")] == ["contoso", "fabrikam", "wingtip"]


def test_retired_client_was_served_up_to_its_last_day_only():
    t = registry.get("tailspin")
    assert t.ended == date(2025, 10, 31) and t.active_on(date(2025, 10, 31)) and not t.active_on(date(2025, 11, 3))
    served = t.weeks_served()
    assert served[0] == "2025-W03" and served[-1] == "2025-W44" and len(served) == 42


def test_paused_client_stops_the_day_it_paused():
    p = registry.get("proseware")
    assert p.active_on(date(2026, 8, 13)) and not p.active_on(date(2026, 8, 14))
    assert p.weeks_served(today=date(2026, 10, 24))[-1] == "2026-W33"


def test_clients_active_on_a_date():
    reg = registry.load_registry()
    assert [r.key for r in registry.active_on(reg, date(2025, 6, 24))] == ["contoso", "tailspin", "adatum", "woodgrove"]
    assert [r.key for r in registry.active_on(reg, date(2026, 10, 24))] == ["contoso", "fabrikam", "wingtip"]
    assert registry.get("northwind").weeks_served() == []


def test_registry_agrees_with_configs_rosters_and_data():
    problems = [p for r in registry.load_registry().values() for p in registry.check(r, layouts=LAYOUTS, data=True)]
    assert [str(p) for p in problems] == []


RULES = [
    ({"status": "retired"}, "a retired client needs ended"),
    ({"status": "paused", "paused_from": "2026-03-02", "ended": "2026-03-01"}, "ended is set but status is paused"),
    ({"status": "dormant"}, "status 'dormant'"),
    ({"status": "onboarding", "onboarded": None}, "needs golive_week"),
    ({"tz": "Europe/Atlantis"}, "unknown timezone"),
    ({"grain": 45}, "does not divide an hour"),
    ({"retired": True}, "unknown field(s) retired"),
    ({"status": "retired", "ended": "2025-12-01"}, "is not after onboarded"),
]


def test_record_rules(tmp_path):
    assert registry.load_registry(_registry(tmp_path, newco=GOOD))["newco"].onboarded == date(2026, 1, 5)
    for change, message in RULES:
        with pytest.raises(registry.RegistryError) as e:
            registry.load_registry(_registry(tmp_path, newco={**GOOD, **change}))
        assert message in str(e.value)


def test_check_reports_disagreements(tmp_path, monkeypatch):
    (tmp_path / "configs").mkdir()
    (tmp_path / "configs" / "defaults.yaml").write_text((config.CONFIG_DIR / "defaults.yaml").read_text())
    (tmp_path / "configs" / "newco.yaml").write_text("name: NewCo\ninterval_minutes: 60\ntz: Europe/Dublin\n")
    (tmp_path / "data" / "agents").mkdir(parents=True)
    (tmp_path / "data" / "agents" / "newco.csv").write_text("agent_id,contract,skills\nN-1,FT,priority;email\n")
    (tmp_path / "data" / "newco").mkdir()
    for name in ("week_2025-W52.csv", "week_2026-W02.csv", "export_2026-W03.csv"):
        (tmp_path / "data" / "newco" / name).write_text("")
    monkeypatch.setattr(config, "CONFIG_DIR", tmp_path / "configs")
    monkeypatch.setattr(config, "DATA_DIR", tmp_path / "data")
    rec = registry.load_registry(_registry(tmp_path, newco={**GOOD, "export_layout": "fixed_width"}))["newco"]
    assert [(p.level, p.text) for p in registry.check(rec, layouts=LAYOUTS)] == [
        ("error", "grain 30 in the registry, interval_minutes 60 in the config"),
        ("warning", "roster skills not among the registry queues: email"),
        ("warning", "1 export_*.csv file(s) for a canonical client"),
        ("error", "data for 2025-W52 is outside the weeks served (2026-W02 to now)"),
        ("error", "unknown export_layout 'fixed_width'")]


def test_timeline_marks_each_clients_months():
    reg = registry.load_registry()
    lines = registry.timeline(list(reg.values()), until=date(2026, 11, 2)).splitlines()
    rows = {line.split()[0]: line for line in lines[2:] if line[:4].isdigit()}
    cols = {k: lines[0].index(k) for k in reg}
    mark = lambda month, client: rows[month][cols[client]:cols[client] + 1].strip()   # noqa: E731
    assert list(rows)[0] == "2024-12" and list(rows)[-1] == "2026-11"
    assert (mark("2024-12", "contoso"), mark("2025-01", "tailspin"), mark("2025-10", "tailspin")) == ("+", "+", "x")
    assert mark("2025-11", "tailspin") == "" and mark("2026-01", "woodgrove") == "x"
    assert (mark("2026-08", "proseware"), mark("2026-10", "proseware")) == ("|", "-")
    assert mark("2026-10", "northwind") == ">" and mark("2026-11", "wingtip") == "#"
    assert registry.month_mark(reg["proseware"], date(2026, 8, 1), until=date(2026, 8, 1)) == "#"
    (tailspin,) = [line.split() for line in lines if line.startswith("tailspin ")]   # data on file
    assert tailspin == ["tailspin", "retired", "42", "33", "2025-W03", "2025-W43", "0"]


def test_markdown_table_has_a_row_per_client():
    text = registry.render_markdown(list(registry.load_registry().values()))
    lines = text.splitlines()
    assert lines[0].startswith("| client") and len(lines) == 2 + 8
    assert "| northwind | Northwind Traders | onboarding | go-live 2026-W44 |" in text
    assert "2025-10-31 (retired)" in text and "2026-08-14 (paused)" in text


def test_accounts_table_groups_by_account_manager(tmp_path):
    reg = registry.load_registry()
    d = tmp_path / "fabrikam" / "history" / "2026-W43"
    d.mkdir(parents=True)
    (d / "eval.json").write_text(json.dumps({"client": "fabrikam", "week": "2026-W43", "meets_target": True,
                                             "sla": {"priority": 0.937, "standard": 0.958}, "scheduled_hours": 696.0,
                                             "agents_scheduled": 28}))
    text = registry.accounts_table([reg[k] for k in ("tailspin", "contoso", "fabrikam")], tmp_path)
    rows = [line for line in text.splitlines() if line.startswith("| ") and "client" not in line]
    assert [r.split("|")[2].strip() for r in rows] == ["fabrikam", "contoso", "tailspin"]
    assert "priority 0.937" in rows[0] and "696.0" in rows[0]
