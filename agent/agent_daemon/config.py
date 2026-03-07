from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

DEFAULT_REFRESH_INTERVAL = 60
CONFIG_DIR = Path(os.getenv("AGENT_DAEMON_HOME", "~/.agent_daemon")).expanduser()
CONFIG_PATH = CONFIG_DIR / "config.json"


def load_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {
            "refresh_interval": DEFAULT_REFRESH_INTERVAL,
            "subscribers": {},
            "api_base": "http://localhost:5333",
        }
    data = json.loads(CONFIG_PATH.read_text())
    data.setdefault("refresh_interval", DEFAULT_REFRESH_INTERVAL)
    data.setdefault("subscribers", {})
    data.setdefault("api_base", "http://localhost:5333")
    return data


def save_config(data: Dict[str, Any]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(data, indent=2))
