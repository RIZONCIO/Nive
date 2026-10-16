"""
restore_point.py - Ponto de restauração e ferramentas de recuperação do Windows.
"""

import subprocess
from typing import Tuple


class RestorePoint:
    """Interface para verificação e criação de pontos de restauração do Windows."""

    @staticmethod
    def open_system_restore_gui() -> bool:
        """Abre o assistente gráfico de restauração do sistema (rstrui.exe)."""
        try:
            subprocess.Popen("rstrui.exe", shell=True)
            return True
        except Exception:
            return False

    @staticmethod
    def create_restore_point_cmd(description: str = "ScriptNive Backup") -> str:
        """Retorna comando PowerShell para criar ponto de restauração."""
        return (
            f"powershell.exe -ExecutionPolicy Bypass -Command "
            f"\"Checkpoint-Computer -Description '{description}' -RestorePointType 'MODIFY_SETTINGS'\""
        )
