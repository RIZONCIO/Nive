"""
history_tracker.py - Registro cronológico e histórico de operações do ScriptNive.
"""

from datetime import datetime
from typing import List, Dict, Any
import threading


class HistoryTracker:
    """Rastreia histórico de operações executadas na sessão."""

    def __init__(self):
        self._entries: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    def record_operation(
        self,
        operation_name: str,
        status: str,
        details: str = "",
        user: str = "",
    ):
        """Registra uma operação com timestamp e status."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation_name,
            "status": status,
            "details": details,
            "user": user,
        }
        with self._lock:
            self._entries.append(entry)

    def get_history(self) -> List[Dict[str, Any]]:
        """Retorna uma cópia do histórico de operações."""
        with self._lock:
            return list(self._entries)

    def clear(self):
        """Limpa o histórico em memória."""
        with self._lock:
            self._entries.clear()
