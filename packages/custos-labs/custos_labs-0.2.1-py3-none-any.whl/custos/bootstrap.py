# custos/bootstrap.py
from __future__ import annotations
import threading
from .config import CustosConfig
from .client import AutoLoggingGuardian
from . import autocapture

_guardian_lock = threading.Lock()
_guardian_singleton: AutoLoggingGuardian | None = None

def custos_bootstrap():
    global _guardian_singleton
    cfg = CustosConfig()
    if not cfg.api_key:
        return  # clean no-op if no key

    with _guardian_lock:
        if _guardian_singleton is None:
            _guardian_singleton = AutoLoggingGuardian(cfg)  # starts HRV
            autocapture.enable(_guardian_singleton)         # <- tie replies automatically
