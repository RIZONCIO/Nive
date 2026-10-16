"""
Custom exceptions module.
"""

from .exceptions import (
    NiveError,
    AdminPrivilegeError,
    CommandExecutionError,
    ValidationError,
)

__all__ = [
    "NiveError",
    "AdminPrivilegeError",
    "CommandExecutionError",
    "ValidationError",
]
