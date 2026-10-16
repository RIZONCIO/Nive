"""
run.py - Ponto de entrada com console para execução e depuração do ScriptNive GUI.
"""

import sys
from pathlib import Path

# Configuração de caminhos raiz
ROOT_DIR = Path(__file__).resolve().parent
SOFTWARE_DIR = ROOT_DIR / "NiveSoftware"

for p in (str(ROOT_DIR), str(SOFTWARE_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from NiveSoftware.core.application.app import ScriptNiveGUI, main

if __name__ == "__main__":
    main()
