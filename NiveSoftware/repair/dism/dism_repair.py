"""
dism_repair.py - Reparo e limpeza da imagem do Windows com DISM.
"""

from typing import List


class DismRepair:
    """Comandos e utilitários para DISM."""

    SCAN_COMMAND = "Dism /Online /Cleanup-Image /ScanHealth"
    CHECK_COMMAND = "Dism /Online /Cleanup-Image /CheckHealth"
    RESTORE_COMMAND = "Dism /Online /Cleanup-Image /RestoreHealth"
    CLEANUP_COMMAND = "Dism /Online /Cleanup-Image /StartComponentCleanup"

    @classmethod
    def get_repair_commands(cls) -> List[str]:
        return [
            cls.SCAN_COMMAND,
            cls.CHECK_COMMAND,
            cls.RESTORE_COMMAND,
        ]
