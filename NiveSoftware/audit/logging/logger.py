import os
import tkinter as tk
import queue
import threading
from datetime import datetime
from pathlib import Path
try:
    from shared.utilities.notifications import Notifications
except ImportError:
    try:
        from NiveSoftware.shared.utilities.notifications import Notifications
    except ImportError:
        from utils.notifications import Notifications


class Logger:
    """Classe para gerenciar logs da aplicação"""

    def __init__(self, log_widget=None):
        """Inicializar logger"""
        self.log_widget = log_widget
        self.notifications = Notifications()

        def _get_log_dir() -> Path:
            for parent in Path(__file__).resolve().parents:
                cand = parent / "logs"
                if cand.exists():
                    return cand
            return Path("logs")

        log_dir = _get_log_dir()
        log_dir.mkdir(exist_ok=True)
        self.log_file = (
            log_dir / f"scriptnive_{datetime.now().strftime('%Y%m%d')}.log"
        )

        # Lista para armazenar logs na memória
        self.memory_logs = []
        self._lock = threading.Lock()
        self._ui_queue = queue.SimpleQueue()
        self._ui_root = None
        self._ui_thread_id = None
        self._ui_after_id = None
        self._ui_closed = False

    def set_ui_root(self, root):
        """Configure a janela que processa callbacks enfileirados por workers."""
        self._ui_root = root
        self._ui_thread_id = threading.get_ident()
        self._ui_closed = False
        self._schedule_ui_queue()

    def run_on_ui(self, callback):
        """Execute callbacks Tk na thread principal sem chamar Tk a partir de workers."""
        if self._ui_closed:
            self._write_log_file(
                "[WARNING] Callback de interface descartado após o encerramento."
            )
        elif self._ui_thread_id == threading.get_ident():
            callback()
        elif self._ui_root is None:
            callback()
        else:
            self._ui_queue.put(callback)

    def stop_ui_dispatch(self):
        """Pare o despacho antes de destruir a janela principal."""
        self._ui_closed = True
        root = self._ui_root
        after_id = self._ui_after_id
        self._ui_root = None
        self._ui_after_id = None
        if root is not None and after_id is not None:
            try:
                root.after_cancel(after_id)
            except tk.TclError as e:
                self._write_log_file(
                    f"[WARNING] Não foi possível cancelar a fila da interface: {e}"
                )

    def _schedule_ui_queue(self):
        if self._ui_root is not None:
            try:
                self._ui_after_id = self._ui_root.after(25, self._drain_ui_queue)
            except tk.TclError as e:
                self._ui_root = None
                self._ui_closed = True
                self._write_log_file(
                    f"[WARNING] Fila da interface encerrada: {e}"
                )

    def _drain_ui_queue(self):
        self._ui_after_id = None
        while True:
            try:
                callback = self._ui_queue.get_nowait()
            except queue.Empty:
                break

            try:
                callback()
            except Exception as e:
                self.log_error(f"Erro em callback da interface: {e}")

        self._schedule_ui_queue()

    def _append_to_widget(self, widget, log_entry):
        try:
            widget.insert(tk.END, log_entry + "\n")
            widget.see(tk.END)
        except tk.TclError as e:
            self._write_log_file(f"[ERRO] Não foi possível atualizar o widget de log: {e}")

    def set_widget(self, widget):
        """Definir widget de texto para exibir logs"""
        self.log_widget = widget

    def log(self, message, level="INFO"):
        """Adicionar mensagem ao log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"

        with self._lock:
            self.memory_logs.append(log_entry)

        if self.log_widget:
            self.run_on_ui(lambda: self._append_to_widget(self.log_widget, log_entry))

        self._write_log_file(log_entry)

    def _write_log_file(self, log_entry):
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
        except Exception as e:
            print(f"Erro ao salvar log: {e}")

    def log_success(self, message):
        """Log de sucesso com notificação"""
        self.log(f"✅ {message}", "SUCCESS")
        self.notifications.show_notification("ScriptNive - Sucesso", message)

    def log_error(self, message):
        """Log de erro com notificação"""
        self.log(f"❌ {message}", "ERROR")
        self.notifications.show_notification("ScriptNive - Erro", message)

    def log_warning(self, message):
        """Log de aviso"""
        self.log(f"⚠ {message}", "WARNING")

    def log_info(self, message):
        """Log de informação"""
        self.log(f"ℹ {message}", "INFO")

    def clear_widget(self):
        """Limpar widget de log"""
        if self.log_widget:
            def clear():
                try:
                    self.log_widget.delete(1.0, tk.END)
                except tk.TclError as e:
                    self._write_log_file(
                        f"[ERRO] Não foi possível limpar o widget de log: {e}"
                    )

            self.run_on_ui(clear)

    def get_all_logs(self):
        """Obter todos os logs da memória"""
        with self._lock:
            return "\n".join(self.memory_logs)

    def save_logs_to_file(self, file_path):
        """Salvar logs em arquivo específico"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.get_all_logs())
            return True
        except Exception as e:
            self.log_error(f"Erro ao salvar logs: {e}")
            return False
