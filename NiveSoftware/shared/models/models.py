"""
models.py - Modelos de dados estruturados utilizados no NiveSoftware.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class OperationResult:
    """Resultado estruturado de uma operação do sistema."""
    success: bool
    returncode: int = 0
    stdout: str = ""
    stderr: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SoftwareItem:
    """Representação de um software instalado."""
    display_name: str
    uninstall_string: str
    install_location: Optional[str] = None
    display_version: Optional[str] = None
    publisher: Optional[str] = None
    chocolatey_package: Optional[str] = None
