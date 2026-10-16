"""
sfc_repair.py - Verificação e reparo de integridade com System File Checker (SFC).
"""

from typing import List


class SfcRepair:
    """Comandos e utilitários para SFC."""

    COMMANDS = [
        "sfc /scannow",
    ]

    @classmethod
    def get_commands(cls) -> List[str]:
        return list(cls.COMMANDS)
