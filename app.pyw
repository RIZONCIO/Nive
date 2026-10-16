"""Ponto de entrada gráfico sem console para o ScriptNive GUI."""

import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
SOFTWARE_DIR = APP_DIR / "NiveSoftware"

for p in (str(APP_DIR), str(SOFTWARE_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

os.chdir(APP_DIR)
log_dir = APP_DIR / "logs"
log_dir.mkdir(exist_ok=True)
log_path = log_dir / f"scriptnive_{datetime.now().strftime('%Y%m%d')}.log"
startup_log = open(log_path, "a", encoding="utf-8", buffering=1)
sys.stdout = startup_log
sys.stderr = startup_log

try:
    from NiveSoftware.core.application.app import main

    main()
except Exception:
    traceback.print_exc()
    try:
        from tkinter import messagebox

        messagebox.showerror(
            "Erro de Inicialização",
            f"Ocorreu um erro ao iniciar. Consulte o log:\n{log_path}",
        )
    except Exception:
        pass
finally:
    startup_log.close()
