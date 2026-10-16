"""
Permite a execução do pacote via: python -m NiveSoftware
"""

import sys
from pathlib import Path

_PKG_DIR = Path(__file__).resolve().parent
_ROOT_DIR = _PKG_DIR.parent
for _p in (str(_PKG_DIR), str(_ROOT_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from NiveSoftware.core.application.app import main

if __name__ == "__main__":
    main()
