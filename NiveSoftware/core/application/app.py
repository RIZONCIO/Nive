"""
app.py - Inicialização e ciclo de vida da aplicação ScriptNive GUI.
"""

import sys
import ctypes
from pathlib import Path


def _preload_fonts():
    if sys.platform != "win32":
        return

    current = Path(__file__).resolve()
    fonts_dir = None
    for parent in current.parents:
        cand = parent / "assets" / "font"
        if cand.exists():
            fonts_dir = cand
            break
        cand2 = parent / "assets" / "fonts"
        if cand2.exists():
            fonts_dir = cand2
            break

    if not fonts_dir or not fonts_dir.exists():
        print(f"[preload] AVISO: pasta de fontes não encontrada")
        return

    FA_FILES = [
        "fa-solid-900.ttf",
        "fa-regular-400.ttf",
        "fa-brands-400.ttf",
    ]

    for fname in FA_FILES:
        fpath = fonts_dir / fname
        if fpath.exists():
            result = ctypes.windll.gdi32.AddFontResourceExW(str(fpath), 0, 0)
            if result:
                print(f"[preload] ✓ {fname}")
            else:
                print(f"[preload] ✗ Falha: {fname}")
        else:
            print(f"[preload] ✗ Não encontrado: {fpath}")


_preload_fonts()

import customtkinter as ctk
from tkinter import messagebox

try:
    from interface.gui.app_ui import ScriptNiveInterface
except ImportError:
    try:
        from NiveSoftware.interface.gui.app_ui import ScriptNiveInterface
    except ImportError:
        from app_ui import ScriptNiveInterface

try:
    from core.task_queue.commands import SystemCommands
except ImportError:
    try:
        from NiveSoftware.core.task_queue.commands import SystemCommands
    except ImportError:
        from core.commands import SystemCommands

try:
    from audit.logging.logger import Logger
except ImportError:
    try:
        from NiveSoftware.audit.logging.logger import Logger
    except ImportError:
        from utils.logger import Logger

try:
    from shared.config.config import Config
except ImportError:
    try:
        from NiveSoftware.shared.config.config import Config
    except ImportError:
        from utils.config import Config

try:
    from shared.utilities.tray import TrayIconManager
except ImportError:
    try:
        from NiveSoftware.shared.utilities.tray import TrayIconManager
    except ImportError:
        from utils.tray import TrayIconManager

try:
    from shared.utilities import icons
except ImportError:
    try:
        from NiveSoftware.shared.utilities import icons
    except ImportError:
        from utils import icons

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ScriptNiveGUI:
    """Aplicação principal ScriptNive GUI — versão modernizada."""

    def __init__(self):
        try:
            icons.load_all()
            self.config = Config()
            self.logger = Logger()
            self.root = ctk.CTk()
            self.logger.set_ui_root(self.root)
            self.system_commands = SystemCommands(self.logger)
            self._setup_window()

            self.interface = ScriptNiveInterface(
                self.root, self.system_commands, self.logger, self.config
            )

            self.tray_manager = TrayIconManager(
                self.root,
                self._restore_window,
                self._exit_from_tray,
                self.logger.run_on_ui,
            )
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        except Exception as e:
            messagebox.showerror("Erro de Inicialização", f"Erro ao inicializar:\n{e}")
            raise

    def _setup_window(self):
        w = getattr(self.config, "window_width", 1050)
        h = getattr(self.config, "window_height", 700)
        self.root.title(
            f"ScriptNive {getattr(self.config, 'version', '2.0')} — Interface Gráfica"
        )
        self.root.geometry(f"{w}x{h}")
        self.root.resizable(True, True)
        self.root.minsize(820, 540)
        self._center_window(w, h)
        try:
            self.root.state("zoomed")
        except Exception:
            pass
        try:
            self.root.iconbitmap(self.config.icon_path)
        except Exception:
            pass

    def _center_window(self, w, h):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _on_closing(self):
        try:
            self.logger.log_info("Aplicação minimizada para bandeja")
            if hasattr(self, "interface"):
                self.interface.update_status("Minimizado para bandeja")
        except Exception:
            pass
        self.root.withdraw()
        self.tray_manager.start()

    def _restore_window(self):
        try:
            self.root.deiconify()
            self.root.lift()
            self.tray_manager.stop()
            self.logger.log_info("Aplicação restaurada da bandeja")
            if hasattr(self, "interface"):
                self.interface.update_status("Restaurado")
        except Exception:
            pass

    def _exit_from_tray(self):
        try:
            self.tray_manager.stop()
        except Exception:
            pass
        if hasattr(self, "interface"):
            self.interface.main_tab.stop_monitor()
        try:
            self.logger.log_info("Aplicação encerrada pelo usuário")
        except Exception:
            pass
        self.logger.stop_ui_dispatch()
        self.root.destroy()

    def run(self):
        self.logger.log("ScriptNive GUI iniciado")
        self.root.mainloop()


def main():
    try:
        ScriptNiveGUI().run()
    except ImportError as e:
        messagebox.showerror(
            "Dependência não encontrada",
            f"Instale com:\npip install customtkinter\n\nDetalhe: {e}",
        )
    except Exception as e:
        messagebox.showerror("Erro Crítico", f"Erro ao iniciar:\n{e}")


if __name__ == "__main__":
    main()
