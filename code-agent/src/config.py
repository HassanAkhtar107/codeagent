"""
config.py  –  User configuration persistence
Saves/loads the API key and other settings to/from a local JSON file
in the user's home directory. NEVER hardcoded in code or repo.
"""
from __future__ import annotations

import json
import os
from pathlib import Path


CONFIG_FILENAME = ".code_agent_config.json"


def _config_path() -> Path:
    """Return the path to the user config file (~/.code_agent_config.json)."""
    return Path.home() / CONFIG_FILENAME


def load_config() -> dict:
    """Load config from disk. Returns empty dict if file doesn't exist."""
    p = _config_path()
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_config(data: dict) -> None:
    """Save config dict to disk."""
    p = _config_path()
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")
    # Restrict permissions on Unix; no-op on Windows
    try:
        os.chmod(str(p), 0o600)
    except Exception:
        pass


def get_api_key() -> str:
    """Return saved API key or empty string."""
    return load_config().get("api_key", "")


def save_api_key(key: str) -> None:
    """Persist API key to user config file."""
    cfg = load_config()
    cfg["api_key"] = key
    save_config(cfg)


def clear_api_key() -> None:
    """Remove stored API key from config."""
    cfg = load_config()
    cfg.pop("api_key", None)
    save_config(cfg)
