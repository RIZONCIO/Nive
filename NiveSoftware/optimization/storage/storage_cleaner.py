"""
storage_cleaner.py - Limpeza de arquivos temporários e armazenamento.
"""

from typing import List


class StorageCleaner:
    """Comandos para higienização e liberação de espaço em disco."""

    RECYCLE_BIN = "rd /S /Q c:\\$Recycle.bin"
    CLEANMGR = "start cleanmgr.exe"
    TEMP_CLEANUP = [
        'del /q /f /s "%temp%\\*"',
        'del /q/f/s "C:\\Windows\\Temp\\*"',
        'del /q /f /s "%windir%\\Prefetch\\*"',
        'del /q /f /s "%appdata%\\Microsoft\\Windows\\Recent\\*"',
    ]

    @classmethod
    def get_cleanup_commands(cls) -> List[str]:
        return list(cls.TEMP_CLEANUP)
