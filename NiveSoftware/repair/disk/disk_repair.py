"""
disk_repair.py - Diagnóstico e reparo de volumes e discos com CHKDSK e WMIC.
"""

from typing import List


class DiskRepair:
    """Comandos para verificação e reparo de unidades de disco."""

    STATUS_CHECK = "WMIC diskdrive get status"
    MODEL_STATUS = "WMIC diskdrive get model,status"
    CHKDSK_REPAIR = "CHKDSK /R"

    @classmethod
    def get_commands(cls) -> List[str]:
        return [
            cls.STATUS_CHECK,
            cls.MODEL_STATUS,
            cls.CHKDSK_REPAIR,
        ]
