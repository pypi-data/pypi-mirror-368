# custos/bootstrap.py
from __future__ import annotations
import threading
from typing import Optional

from .config import CustosConfig
from .client import AutoLoggingGuardian
from . import autocapture

_guardian_lock = threading.Lock()
_guardian_singleton: Optional[AutoLoggingGuardian] = None

def custos_bootstrap() -> Optional[AutoLoggingGuardian]:
    """
    Initialize once, then return the singleton guardian.
    Returns None when no CUSTOS_API_KEY is set.
    """
    global _guardian_singleton
    cfg = CustosConfig()
    if not cfg.api_key:
        return None  # clean no-op if no key

    with _guardian_lock:
        if _guardian_singleton is None:
            _guardian_singleton = AutoLoggingGuardian(cfg)  # starts HRV
            # Optional: auto-capture replies if popular libs are present.
            autocapture.enable(_guardian_singleton)

    return _guardian_singleton
