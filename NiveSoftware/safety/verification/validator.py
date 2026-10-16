"""
validator.py - Validação de entradas, permissões e parâmetros do sistema.
"""

from pathlib import Path
from typing import Tuple


class Validator:
    """Validador de caminhos e parâmetros de operações seguras."""

    @staticmethod
    def validate_absolute_folder(folder_path: str) -> Tuple[bool, str]:
        """Valida se o caminho é absoluto e representa uma pasta válida."""
        if not folder_path or not isinstance(folder_path, str):
            return False, "Caminho inválido ou não fornecido."
        p = Path(folder_path)
        if not p.is_absolute():
            return False, "O caminho deve ser absoluto (ex: C:\\Pasta)."
        if not p.exists():
            return False, "A pasta especificada não existe."
        if not p.is_dir():
            return False, "O caminho especificado não é um diretório."
        return True, "Caminho válido."
