"""
Optimization package for NiveSoftware.
"""

from .performance.animations import RemoverAnimacoes
from .performance.edge import OtimizadorEdge
from .performance.telemetry import RemoverTelemetria
from .startup.boost_windows import AceleradorWindows
from .startup.services import DesabilitadorServicos
from .startup.tasks import DesabilitadorTweaks
from .startup.features import RemoverFeatures
from .startup.apps import DisableSoftware
from .storage.storage_cleaner import StorageCleaner

__all__ = [
    "RemoverAnimacoes",
    "OtimizadorEdge",
    "RemoverTelemetria",
    "AceleradorWindows",
    "DesabilitadorServicos",
    "DesabilitadorTweaks",
    "RemoverFeatures",
    "DisableSoftware",
    "StorageCleaner",
]
