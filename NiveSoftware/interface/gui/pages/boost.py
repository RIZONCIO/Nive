import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk_bs
from ttkbootstrap.constants import *
import sys
import os

# Adicionar o diretório core ao path para importar o módulo
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "core"))

try:
    from ..boost_handlers import OptimizationHandlers
    from ..boost_ui import OptimizationUI
except (ImportError, ValueError):
    try:
        from interface.gui.boost_handlers import OptimizationHandlers
        from interface.gui.boost_ui import OptimizationUI
    except ImportError:
        from gui.boost_handlers import OptimizationHandlers
        from gui.boost_ui import OptimizationUI


class OptimizationTab:
    """Classe principal responsável pela aba de otimização NiveBoost"""

    def __init__(self, parent_interface):
        """Inicializar aba de otimização"""
        self.parent = parent_interface
        self.system_commands = parent_interface.system_commands
        self.config = parent_interface.config
        self.logger = parent_interface.logger

        # Inicializar componentes
        self.ui = OptimizationUI(self)
        self.handlers = OptimizationHandlers(self)

    def create_optimization_tab(self, notebook):
        """Criar aba de otimização com todas as 11 opções do NiveBoost"""
        return self.ui.create_optimization_tab(notebook)

    def confirm_operation(self, title, message):
        """Método auxiliar para confirmar operações"""
        return messagebox.askyesno(title, message)

    def log_activity(self, message):
        """Registrar atividade no log"""
        if hasattr(self, "logger") and self.logger:
            self.logger.log(message)

    # Delegação dos métodos para os handlers específicos
    def remove_telemetry(self):
        """Remover telemetria - delegado para handlers"""
        return self.handlers.remove_telemetry()

    def remove_unused_features(self):
        """Remover features não usadas - delegado para handlers"""
        return self.handlers.remove_unused_features()

    def remove_animations(self):
        """Remover animações - delegado para handlers"""
        return self.handlers.remove_animations()

    def optimize_edge(self):
        """Otimizar Edge - delegado para handlers"""
        return self.handlers.optimize_edge()

    def accelerate_windows(self):
        """Acelerar Windows - delegado para handlers"""
        return self.handlers.accelerate_windows()

    def disable_scheduled_tasks(self):
        """Desabilitar tarefas agendadas - delegado para handlers"""
        return self.handlers.disable_scheduled_tasks()

    def disable_windows_services(self):
        """Desabilitar serviços - delegado para handlers"""
        return self.handlers.disable_windows_services()

    def disable_windows_software(self):
        """Desabilitar software - delegado para handlers"""
        return self.handlers.disable_windows_software()

    def disable_web_search(self):
        """Desabilitar busca web - delegado para handlers"""
        return self.handlers.disable_web_search()

    def disable_browser_cache(self):
        """Desabilitar cache navegadores - delegado para handlers"""
        return self.handlers.disable_browser_cache()

    def disable_lock_screen_ads(self):
        """Desabilitar ads tela de bloqueio - delegado para handlers"""
        return self.handlers.disable_lock_screen_ads()
