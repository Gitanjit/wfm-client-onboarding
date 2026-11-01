from wfm.config import load_config
from wfm.ingest.loader import load_week


def test_client_file_overrides_top_level_keys_only():
    cfg = load_config("fabrikam")
    assert cfg["interval_minutes"] == 60 and cfg["tz"] == "America/New_York"
    assert cfg["sla"]["priority"]["target"] == 0.80   # inherited from defaults.yaml


def test_canonical_week_has_one_row_per_queue_per_interval():
    df = load_week(load_config("contoso"), "2026-W41")
    assert len(df) == 2 * 7 * 96 and df["interval_minutes"].eq(15).all()


def test_end_stamped_export_rows_start_one_interval_earlier(tmp_path):
    from wfm.ingest.loader import _read_export
    f = tmp_path / "export_2027-W11.csv"
    f.write_text("interval_end_local,utc_offset,queue,volume,aht_sec\n2027-03-15 09:20,+00:00,email,5.0,300.0\n")
    df = _read_export(f, {"client": "x", "tz": "Europe/London", "interval_minutes": 20})
    assert str(df["interval_start_utc"].iloc[0]) == "2027-03-15 09:00:00+00:00"
