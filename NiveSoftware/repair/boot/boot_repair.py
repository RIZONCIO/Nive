"""
boot_repair.py - Reparo de inicialização e agendamento de reinicialização do Windows.
"""

from typing import List


class BootRepair:
    """Comandos para reparo de boot e reinicialização."""

    SCHEDULE_REBOOT = "shutdown -r -t 30"
    QUICK_REBOOT = "shutdown -r -t 10"

    @classmethod
    def get_reboot_command(cls, seconds: int = 30) -> str:
        return f"shutdown -r -t {seconds}"
