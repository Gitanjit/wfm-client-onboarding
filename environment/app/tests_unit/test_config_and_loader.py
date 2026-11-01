from wfm.config import load_config
from wfm.ingest.loader import load_week


def test_client_file_overrides_top_level_keys_only():
    cfg = load_config("fabrikam")
    assert cfg["interval_minutes"] == 60 and cfg["tz"] == "America/New_York"
    assert cfg["sla"]["priority"]["target"] == 0.80   # inherited from defaults.yaml


def test_canonical_week_has_one_row_per_queue_per_interval():
    df = load_week(load_config("contoso"), "2026-W41")
    assert len(df) == 2 * 7 * 96 and df["interval_minutes"].eq(15).all()
