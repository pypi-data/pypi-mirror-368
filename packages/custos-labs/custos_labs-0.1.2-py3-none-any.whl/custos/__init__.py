### custos/__init__.py

__version__ = "0.1.a"

from .guardian import CustosGuardian
from .exceptions import AlignmentViolation
from .config import CustosConfig
from .ethics import EthicsRegistry
from .training import FeedbackTrainer

__all__ = ["CustosGuardian", "AlignmentViolation", "CustosConfig", "EthicsRegistry", "FeedbackTrainer"]

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
                "👉 Use `custos.set_api_key('<your-api-key>')` before calling Custos functions.\n\n"
                "📚 Docs:\n"
                "   - Custos SDK: https://custos.dev/docs/setup\n"
                "   - PyPI: https://pypi.org/project/custos-guardian/\n"
            )
        if not _import_initialized:
            raise ImportError(
                "\n❌ Custos module not properly initialized.\n"
                "👉 You must import `custos` and set your API key like this:\n\n"
                "   import custos\n"
                "   custos.set_api_key('<your-api-key>')\n\n"
                "📚 Docs:\n"
                "   - Custos SDK: https://custos.dev/docs/setup\n"
                "   - PyPI: https://pypi.org/project/custos-guardian/\n"
            )
        return _CustosGuardian(api_key=_custos_api_key)
