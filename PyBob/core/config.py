from __future__ import annotations

import os
from pathlib import Path

import yaml


def _read_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_user_config_path(app_name: str = "PyBob") -> Path:
    appdata = os.getenv("APPDATA")
    root = Path(appdata) if appdata else Path.home() / ".config"
    cfg_dir = root / app_name
    cfg_dir.mkdir(parents=True, exist_ok=True)
    return cfg_dir / "config.yaml"


def load_or_create_user_config(default_config_path: Path, app_name: str = "PyBob") -> tuple[dict, Path]:
    user_cfg_path = get_user_config_path(app_name)

    default_cfg = _read_yaml(default_config_path)
    if not user_cfg_path.exists():
        save_config(user_cfg_path, default_cfg)
        return default_cfg, user_cfg_path

    cfg = _read_yaml(user_cfg_path)
    if not isinstance(cfg, dict) or not cfg:
        save_config(user_cfg_path, default_cfg)
        return default_cfg, user_cfg_path

    return cfg, user_cfg_path


def save_config(path: Path, config: dict) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, allow_unicode=True, sort_keys=False)
