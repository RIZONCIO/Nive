"""
hasher.py - Verificação de integridade e criptografia/hashing de arquivos.
"""

import hashlib
from pathlib import Path
from typing import Optional


class Hasher:
    """Calcula e valida hashes de integridade para arquivos e scripts."""

    @staticmethod
    def calculate_file_sha256(file_path: Path) -> Optional[str]:
        """Calcula o hash SHA-256 de um arquivo."""
        p = Path(file_path)
        if not p.is_file():
            return None
        sha = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha.update(chunk)
        return sha.hexdigest()

    @staticmethod
    def verify_file_sha256(file_path: Path, expected_hash: str) -> bool:
        """Verifica se o arquivo corresponde ao hash esperado."""
        computed = Hasher.calculate_file_sha256(file_path)
        if computed is None:
            return False
        return computed.lower() == expected_hash.strip().lower()
