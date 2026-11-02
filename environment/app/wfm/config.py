"""Configuration: configs/defaults.yaml overlaid by configs/<client>.yaml (top-level keys).

Client files come in two schemas (docs/adr/0007-config-schema-v2.md). Schema 1 is flat: every key is
a top-level service key. Schema 2 (`schema: 2`) groups the same keys into sections and is flattened
on load, so the rest of the service only ever sees the flat keys.
"""
from __future__ import annotations

from pathlib import Path

import yaml

APP_DIR = Path(__file__).resolve().parents[1]
CONFIG_DIR = APP_DIR / "configs"
DATA_DIR = APP_DIR / "data"
OUT_DIR = APP_DIR / "out"

# Schema 2: section -> the flat keys it may hold. `name` and `schema` stay at the top level.
V2_SECTIONS = {
    "service": ("interval_minutes", "tz", "operating_hours"),
    "targets": ("sla", "sla_target", "attainment_basis"),
    "staffing": ("queueing", "patience_sec", "occupancy_cap", "aht_smoothing"),
    "scheduling": ("weekly_hours", "max_consecutive_days", "break", "min_cover", "cross_skill_weight"),
}


def _flatten_v2(doc: dict) -> dict:
    """A schema-2 client file -> flat top-level keys. An unknown section or a key in the wrong
    section is an error rather than a silent fall-back to the default."""
    flat = {}
    for key, value in doc.items():
        if key == "schema":
            continue
        if key == "name":
            flat["name"] = value
            continue
        if key not in V2_SECTIONS:
            raise SystemExit(f"config schema 2: unknown section '{key}'")
        for k, v in (value or {}).items():
            if k not in V2_SECTIONS[key]:
                raise SystemExit(f"config schema 2: '{k}' does not belong in section '{key}'")
            flat[k] = v
    return flat


def load_config(client: str) -> dict:
    defaults = yaml.safe_load((CONFIG_DIR / "defaults.yaml").read_text())
    client_file = CONFIG_DIR / f"{client}.yaml"
    if not client_file.exists():
        raise SystemExit(f"unknown client '{client}': no {client_file.relative_to(APP_DIR)}")
    doc = yaml.safe_load(client_file.read_text()) or {}
    if doc.get("schema") == 2:
        doc = _flatten_v2(doc)
    elif "schema" in doc:
        raise SystemExit(f"{client_file.relative_to(APP_DIR)}: unsupported config schema {doc['schema']!r}")
    cfg = dict(defaults)
    cfg.update(doc)
    cfg["client"] = client
    return cfg
