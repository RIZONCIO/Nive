"""
Shared package for NiveSoftware.
"""

from .config.config import Config
from .exceptions.exceptions import NiveError, AdminPrivilegeError
from .models.models import OperationResult, SoftwareItem
from .utilities.notifications import Notifications
from .utilities.tray import TrayIconManager
from .utilities.software import SoftwareManager

__all__ = [
    "Config",
    "NiveError",
    "AdminPrivilegeError",
    "OperationResult",
    "SoftwareItem",
    "Notifications",
    "TrayIconManager",
    "SoftwareManager",
]
