# custos/__init__.py

__version__ = "0.2.1"

from .exceptions import AlignmentViolation
from .ethics import EthicsRegistry
from .training import FeedbackTrainer
from .guardian import CustosGuardian

# Programmatic API (optional)
from .config import CustosConfig
from .client import AutoLoggingGuardian

__all__ = [
    "AlignmentViolation",
    "EthicsRegistry",
    "FeedbackTrainer",
    "CustosGuardian",
    "set_api_key",
    "set_backend_url",
    "guardian",
]

# Optional programmatic shim — not required when using AppConfig bootstrap
_cfg = CustosConfig()

def set_api_key(raw_key: str):
    _cfg.api_key = raw_key

def set_backend_url(url: str):
    _cfg.backend_url = url.rstrip("/")

def guardian():
    return AutoLoggingGuardian(_cfg)
