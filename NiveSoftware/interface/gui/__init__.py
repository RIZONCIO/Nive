from .layout import BaseInterface, COLORS
from .software_modal import SoftwareManagerGUI
from .repair_modal import RepairDialog
from .widgets import IconButton, icon_label
from .boost_ui import OptimizationUI
from .boost_handlers import OptimizationHandlers
from .boost_config import OptimizationConfig
from .boost_results import OptimizationResults
from .app_ui import ScriptNiveInterface, PAGE_META

try:
    from .pages.home import MainTab
    from .pages.network import NetworkTab
    from .pages.boost import OptimizationTab
    from .pages.tools import ToolsTab
    from .pages.about import InfoTab
    from .pages.monitor import MonitoringTab
except (ImportError, ValueError):
    from pages.home import MainTab
    from pages.network import NetworkTab
    from pages.boost import OptimizationTab
    from pages.tools import ToolsTab
    from pages.about import InfoTab
    from pages.monitor import MonitoringTab

__all__ = [
    "BaseInterface",
    "COLORS",
    "MainTab",
    "NetworkTab",
    "OptimizationTab",
    "ToolsTab",
    "InfoTab",
    "MonitoringTab",
    "SoftwareManagerGUI",
    "RepairDialog",
    "IconButton",
    "icon_label",
    "OptimizationUI",
    "OptimizationHandlers",
    "OptimizationConfig",
    "OptimizationResults",
    "ScriptNiveInterface",
    "PAGE_META",
]
