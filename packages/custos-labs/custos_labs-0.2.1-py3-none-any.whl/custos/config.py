### custos/config.py

from __future__ import annotations
from dataclasses import dataclass
import os

def _env_bool(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip() not in ("0", "false", "False", "no", "No")

@dataclass
class CustosConfig:
    # Read-only defaults from env so users can configure without code
    api_key: str | None = os.getenv("CUSTOS_API_KEY") or None
    backend_url: str = (os.getenv("CUSTOS_BACKEND_URL") or "https://custoslabs-backend.onrender.com").rstrip("/")
    timeout_sec: int = int(os.getenv("CUSTOS_TIMEOUT_SEC", "8"))

    # HRV / heartbeat controls
    heartbeat_enabled: bool = _env_bool("CUSTOS_HEARTBEATS", True)
    heartbeat_interval_sec: float = float(os.getenv("CUSTOS_HEARTBEAT_INTERVAL", "2.0"))

