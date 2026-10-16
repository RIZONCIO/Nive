"""
app_ui.py - composição principal da interface do ScriptNive
Conecta a BaseInterface (sidebar) com as páginas (cards)
"""

import customtkinter as ctk
try:
    from .layout import BaseInterface, COLORS
    from .pages.home import MainTab
    from .pages.monitor import MonitoringTab
    from .pages.boost import OptimizationTab
    from .pages.tools import ToolsTab
    from .pages.about import InfoTab
    from .pages.network import NetworkTab
    from .software_modal import SoftwareManagerGUI
    from .repair_modal import RepairDialog
except (ImportError, ValueError):
    try:
        from interface.gui.layout import BaseInterface, COLORS
        from interface.gui.pages.home import MainTab
        from interface.gui.pages.monitor import MonitoringTab
        from interface.gui.pages.boost import OptimizationTab
        from interface.gui.pages.tools import ToolsTab
        from interface.gui.pages.about import InfoTab
        from interface.gui.pages.network import NetworkTab
        from interface.gui.software_modal import SoftwareManagerGUI
        from interface.gui.repair_modal import RepairDialog
    except ImportError:
        from gui.layout import BaseInterface, COLORS
        from pages.home import MainTab
        from pages.monitor import MonitoringTab
        from pages.boost import OptimizationTab
        from pages.tools import ToolsTab
        from pages.about import InfoTab
        from pages.network import NetworkTab
        from gui.software_modal import SoftwareManagerGUI
        from gui.repair_modal import RepairDialog

# (page_key, icon_key, título, subtítulo)
PAGE_META = {
    "main": ("home", "Principal", "Ferramentas mais usadas do Windows"),
    "monitoring": (
        "chart_line",
        "Monitoramento",
        "Sensores e histórico recente do computador",
    ),
    "network": ("network", "Rede", "Diagnóstico e reparo de rede"),
    "optimization": ("bolt", "Otimização", "NiveBoost — acelere o Windows"),
    "tools": ("tools", "Ferramentas", "Diagnóstico e log de atividades"),
    "info": ("info", "Sobre", "ScriptNive — créditos e documentação"),
}


class ScriptNiveInterface:
    """Interface gráfica principal — versão modernizada com sidebar."""

    def __init__(self, root, system_commands, logger, config):
        self.root = root
        self.system_commands = system_commands
        self.logger = logger
        self.config = config

        self.base_interface = BaseInterface(root, system_commands, logger, config)
        self._setup_placeholders()

        self.main_tab = MainTab(self.base_interface)
        self.monitoring_tab = MonitoringTab(self.main_tab)
        self.optimization_tab = OptimizationTab(self.base_interface)
        self.tools_tab = ToolsTab(self.base_interface, self.main_tab)
        self.info_tab = InfoTab(self.base_interface)
        self.network_tab = NetworkTab(self.base_interface)

        self.software_manager = SoftwareManagerGUI(self.base_interface)
        self.repair_dialog = RepairDialog(self.base_interface)

        self._create_widgets()

    def _setup_placeholders(self):
        self.base_interface.reinstall_software_placeholder = self._reinstall
        self.base_interface.complete_repair_placeholder = self._complete_repair

    def _create_widgets(self):
        self.base_interface.setup_base_widgets()
        content = self.base_interface.get_content_area()

        pages = {
            "main": self.main_tab.create_main_tab(content),
            "monitoring": self.monitoring_tab.create_monitoring_tab(content),
            "network": self.network_tab.create_network_tab(content),
            "optimization": self.optimization_tab.create_optimization_tab(content),
            "tools": self.tools_tab.create_tools_tab(content),
            "info": self.info_tab.create_info_tab(content),
        }

        for key, frame in pages.items():
            if frame is not None:
                self.base_interface.register_page(key, frame)

        if hasattr(self.tools_tab, "log_text") and self.tools_tab.log_text:
            self.logger.set_widget(self.tools_tab.log_text)

        # Sobrescreve navigate_to para atualizar o header com ícone FA
        _original_navigate = self.base_interface.navigate_to

        def navigate_with_header(page_key: str):
            previous_page = self.base_interface._active_page
            if previous_page == "monitoring" and page_key != "monitoring":
                self.main_tab.stop_monitor()
            _original_navigate(page_key)
            if page_key == "monitoring" and previous_page != "monitoring":
                self.main_tab.start_monitor()
            if page_key in PAGE_META:
                icon_key, title, subtitle = PAGE_META[page_key]
                self.base_interface.set_header(icon_key, title, subtitle)

        self.base_interface.navigate_to = navigate_with_header
        self.base_interface.navigate_to("main")

    def _reinstall(self):
        return self.software_manager.reinstall_software_placeholder()

    def _complete_repair(self):
        return self.repair_dialog.complete_repair_placeholder()

    def update_status(self, message: str):
        self.base_interface.update_status(message)

    def log_activity(self, message: str):
        self.base_interface.log_activity(message)

    @property
    def status_var(self):
        return self.base_interface.status_var

    @property
    def notebook(self):
        return self.base_interface.notebook

    @property
    def progress(self):
        return self.base_interface.progress
