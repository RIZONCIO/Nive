"""
Performance optimization module.
"""

from .animations import RemoverAnimacoes
from .edge import OtimizadorEdge
from .telemetry import RemoverTelemetria

__all__ = [
    "RemoverAnimacoes",
    "OtimizadorEdge",
    "RemoverTelemetria",
]
