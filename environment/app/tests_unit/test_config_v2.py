import pytest
import yaml

from wfm import config
from wfm.config import CONFIG_DIR, _flatten_v2, load_config


def _defaults():
    return yaml.safe_load((CONFIG_DIR / "defaults.yaml").read_text())


def test_schema_1_files_load_as_defaults_plus_top_level_overrides():
    for client in ("contoso", "fabrikam"):
        expected = {**_defaults(), **yaml.safe_load((CONFIG_DIR / f"{client}.yaml").read_text()), "client": client}
        assert load_config(client) == expected


def test_schema_2_sections_flatten_to_the_service_keys():
    cfg = load_config("proseware")
    assert (cfg["interval_minutes"], cfg["tz"], cfg["operating_hours"]) == (30, "Europe/Berlin", [7, 21])
    assert cfg["sla"]["standard"] == {"target": 0.80, "seconds": 30}
    assert cfg["weekly_hours"] == {"FT": 39, "PT": 20} and cfg["name"] == "Proseware"
    assert not {"schema", "service", "targets", "staffing", "scheduling"} & set(cfg)
    assert cfg["break"] == _defaults()["break"]          # sections not given keep the defaults
    assert load_config("wingtip")["tz"] == "America/Phoenix"


def test_flatten_rejects_unknown_sections_and_misplaced_keys():
    assert _flatten_v2({"schema": 2, "name": "X", "service": {"tz": "UTC"}, "staffing": None}) == {"name": "X", "tz": "UTC"}
    with pytest.raises(SystemExit, match="unknown section 'services'"):
        _flatten_v2({"schema": 2, "services": {"tz": "UTC"}})
    with pytest.raises(SystemExit, match="'tz' does not belong in section 'targets'"):
        _flatten_v2({"schema": 2, "targets": {"tz": "UTC"}})


def test_unsupported_schema_number_is_refused(tmp_path, monkeypatch):
    (tmp_path / "configs").mkdir()
    (tmp_path / "configs" / "defaults.yaml").write_text((CONFIG_DIR / "defaults.yaml").read_text())
    (tmp_path / "configs" / "newco.yaml").write_text("schema: 3\nname: NewCo\n")
    monkeypatch.setattr(config, "APP_DIR", tmp_path)
    monkeypatch.setattr(config, "CONFIG_DIR", tmp_path / "configs")
    with pytest.raises(SystemExit, match="configs/newco.yaml: unsupported config schema 3"):
        load_config("newco")
