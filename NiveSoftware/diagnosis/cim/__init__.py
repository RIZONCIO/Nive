"""
CIM/WMI diagnosis module.
"""

from .system_info import SystemInfo, get_pc_info, get_pc_info_formatted

__all__ = ["SystemInfo", "get_pc_info", "get_pc_info_formatted"]
