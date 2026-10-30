"""Configuration: configs/defaults.yaml overlaid by configs/<client>.yaml (top-level keys)."""
from __future__ import annotations

from pathlib import Path

import yaml

APP_DIR = Path(__file__).resolve().parents[1]
CONFIG_DIR = APP_DIR / "configs"
DATA_DIR = APP_DIR / "data"
OUT_DIR = APP_DIR / "out"


def load_config(client: str) -> dict:
    defaults = yaml.safe_load((CONFIG_DIR / "defaults.yaml").read_text())
    client_file = CONFIG_DIR / f"{client}.yaml"
    if not client_file.exists():
        raise SystemExit(f"unknown client '{client}': no {client_file.relative_to(APP_DIR)}")
    cfg = dict(defaults)
    cfg.update(yaml.safe_load(client_file.read_text()) or {})
    cfg["client"] = client
    return cfg
