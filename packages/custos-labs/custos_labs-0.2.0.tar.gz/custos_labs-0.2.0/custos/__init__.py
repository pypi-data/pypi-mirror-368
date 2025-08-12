# custos/__init__.py

__version__ = "0.2.0"

from .exceptions import AlignmentViolation
from .ethics import EthicsRegistry
from .training import FeedbackTrainer
from .guardian import CustosGuardian
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
    "Custos", 
]

_config = CustosConfig()

def set_api_key(raw_key: str):
    _config.api_key = raw_key

def set_backend_url(url: str):
    _config.backend_url = url

def guardian():
    """
    Returns an AutoLoggingGuardian that:
      - starts automatic HRV heartbeats (every ~2s)
      - can also post 'response' beats if/when available
    """
    return AutoLoggingGuardian(_config)

# Backward compatibility shim for existing code:
class Custos:
    @staticmethod
    def guardian():
        return guardian()
