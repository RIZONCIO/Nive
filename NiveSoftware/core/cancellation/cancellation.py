"""
cancellation.py - Gerenciamento e cancelamento de tarefas e processos.
"""

import threading
from typing import Optional, Callable


class CancellationToken:
    """Token para sinalizar e consultar cancelamento de operações em andamento."""

    def __init__(self):
        self._is_cancelled = threading.Event()
        self._on_cancel_callbacks = []
        self._lock = threading.Lock()

    def cancel(self):
        """Sinaliza o cancelamento da operação."""
        self._is_cancelled.set()
        with self._lock:
            callbacks = list(self._on_cancel_callbacks)
        for cb in callbacks:
            try:
                cb()
            except Exception:
                pass

    def is_cancelled(self) -> bool:
        """Retorna True se o cancelamento foi solicitado."""
        return self._is_cancelled.is_set()

    def register_callback(self, callback: Callable[[], None]):
        """Registra um callback a ser executado no cancelamento."""
        with self._lock:
            if self._is_cancelled.is_set():
                callback()
            else:
                self._on_cancel_callbacks.append(callback)

    def reset(self):
        """Redefine o token para novo uso."""
        self._is_cancelled.clear()
        with self._lock:
            self._on_cancel_callbacks.clear()


class CancellationManager:
    """Gerenciador central de tokens de cancelamento ativos."""

    def __init__(self):
        self._tokens = {}
        self._lock = threading.Lock()

    def create_token(self, operation_id: str) -> CancellationToken:
        token = CancellationToken()
        with self._lock:
            self._tokens[operation_id] = token
        return token

    def cancel(self, operation_id: str) -> bool:
        with self._lock:
            token = self._tokens.get(operation_id)
        if token:
            token.cancel()
            return True
        return False

    def remove(self, operation_id: str):
        with self._lock:
            self._tokens.pop(operation_id, None)
