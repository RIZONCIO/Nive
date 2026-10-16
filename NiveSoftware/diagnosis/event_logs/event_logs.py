"""
event_logs.py - Leitura e diagnóstico de logs de eventos do Windows e Monitor de Confiabilidade.
"""

import subprocess
import os


class EventLogs:
    """Gerenciador e visualizador de logs de eventos do Windows."""

    @staticmethod
    def open_reliability_monitor() -> bool:
        """Inicia o Monitor de Confiabilidade do Windows (perfmon /rel)."""
        try:
            subprocess.Popen("perfmon /rel", shell=True)
            return True
        except Exception:
            return False

    @staticmethod
    def open_event_viewer() -> bool:
        """Inicia o Visualizador de Eventos (eventvwr.msc)."""
        try:
            subprocess.Popen("eventvwr.msc", shell=True)
            return True
        except Exception:
            return False
