"""
ps_diag.py - Diagnóstico de sistema executando consultas PowerShell.
"""

import subprocess
from typing import Tuple


class PowerShellDiagnostics:
    """Executa consultas de diagnóstico via PowerShell sem alterar configurações do sistema."""

    @staticmethod
    def run_query(script_block: str, timeout: int = 60) -> Tuple[bool, str]:
        """Executa um comando somente-leitura em PowerShell e retorna (sucesso, saída)."""
        cmd = f'powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "{script_block}"'
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            return (res.returncode == 0, res.stdout.strip() or res.stderr.strip())
        except Exception as e:
            return (False, str(e))
