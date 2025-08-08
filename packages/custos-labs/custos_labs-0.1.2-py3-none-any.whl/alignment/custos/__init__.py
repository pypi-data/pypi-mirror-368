### custos/__init__.py

_version_ = "0.1.2"

from .guardian import CustosGuardian
from .decorators import monitor
from .context import CustosSession
from .exceptions import AlignmentViolation
from .config import CustosConfig
from .ethics import EthicsRegistry
from .training import FeedbackTrainer

_all_ = [
    "CustosGuardian", "monitor", "CustosSession",
    "AlignmentViolation", "CustosConfig", "EthicsRegistry", "FeedbackTrainer",
    "set_api_key", "get_api_key", "Custos"
]

from .guardian import CustosGuardian as _CustosGuardian

_custos_api_key = None
_import_initialized = False

def set_api_key(key: str):
    global _custos_api_key, _import_initialized
    _custos_api_key = key
    _import_initialized = True

def get_api_key():
    return _custos_api_key

class Custos:
    @staticmethod
    def guardian():
        if not _custos_api_key:
            raise ImportError(
                "\n❌ Custos API key not set.\n"
                "👉 Use custos.set_api_key('<your-api-key>') before calling Custos functions."
            )
        if not _import_initialized:
            raise ImportError(
                "\n❌ Custos module not properly initialized.\n"
                "👉 You must import custos and set your API key like this:\n"
                "   import custos\n"
                "   custos.set_api_key('<your-api-key>')"
            )
        return _CustosGuardian(api_key=_custos_api_key)