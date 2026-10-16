"""
NiveSoftware - Suite de Diagnóstico, Reparo e Otimização para Windows.
"""

__version__ = "2.0.0"
__author__ = "Ryan Vinicius Carvalho Pereira"

import sys
from pathlib import Path

# Garante que NiveSoftware e a raiz do repositório estejam acessíveis no sys.path
_PKG_DIR = Path(__file__).resolve().parent
_ROOT_DIR = _PKG_DIR.parent
for _p in (str(_PKG_DIR), str(_ROOT_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
