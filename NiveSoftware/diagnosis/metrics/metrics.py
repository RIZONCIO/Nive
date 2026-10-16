"""
metrics.py - Diagnóstico e coleta de métricas de desempenho em tempo real.
"""

import psutil
from typing import Dict, Any


class SystemMetrics:
    """Coletor de métricas de hardware e uso do sistema."""

    @staticmethod
    def get_cpu_usage() -> float:
        """Percentual de uso da CPU."""
        return psutil.cpu_percent(interval=None)

    @staticmethod
    def get_memory_info() -> Dict[str, Any]:
        """Estatísticas de uso de memória RAM."""
        mem = psutil.virtual_memory()
        return {
            "total_gb": round(mem.total / (1024 ** 3), 2),
            "available_gb": round(mem.available / (1024 ** 3), 2),
            "used_gb": round(mem.used / (1024 ** 3), 2),
            "percent": mem.percent,
        }

    @staticmethod
    def get_disk_usage(path: str = "C:\\") -> Dict[str, Any]:
        """Estatísticas de uso do disco especificado."""
        try:
            disk = psutil.disk_usage(path)
            return {
                "total_gb": round(disk.total / (1024 ** 3), 2),
                "used_gb": round(disk.used / (1024 ** 3), 2),
                "free_gb": round(disk.free / (1024 ** 3), 2),
                "percent": disk.percent,
            }
        except Exception:
            return {"total_gb": 0, "used_gb": 0, "free_gb": 0, "percent": 0}

    @staticmethod
    def get_snapshot() -> Dict[str, Any]:
        """Snapshot completo dos recursos."""
        return {
            "cpu_percent": SystemMetrics.get_cpu_usage(),
            "memory": SystemMetrics.get_memory_info(),
            "disk": SystemMetrics.get_disk_usage(),
        }
