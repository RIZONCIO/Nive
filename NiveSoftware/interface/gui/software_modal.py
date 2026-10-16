"""
software_modal.py - Gerenciador de software (customtkinter)
"""

import threading
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
try:
    from shared.utilities.software import SoftwareManager
except ImportError:
    try:
        from NiveSoftware.shared.utilities.software import SoftwareManager
    except ImportError:
        from core.software import SoftwareManager

try:
    from core.permissions.admin import run_elevated_operation
except ImportError:
    try:
        from NiveSoftware.core.permissions.admin import run_elevated_operation
    except ImportError:
        from core.admin import run_elevated_operation

COLORS = {
    "content_bg": "#1e1e2e",
    "card_bg": "#252537",
    "card_hover": "#2e2e45",
    "accent": "#4f9cf9",
    "text_primary": "#e2e8f0",
    "text_muted": "#8892a4",
    "success": "#22c55e",
    "danger": "#ef4444",
    "info": "#3b82f6",
}


class SoftwareManagerGUI:
    """Interface do gerenciador de software — modernizada."""

    def __init__(self, parent_interface):
        self.parent = parent_interface
        self.system_commands = parent_interface.system_commands
        self.config = parent_interface.config
        self.logger = parent_interface.logger

        self.software_window = None
        self.software_manager = None
        self.software_list = []
        self.software_listbox = None
        self.software_log_text = None

    # ── Entrada principal ────────────────────────────────────────────────────

    def reinstall_software_placeholder(self):
        try:
            manager = SoftwareManager()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir gerenciador de software:\n{e}")
            return

        def check_chocolatey():
            try:
                installed = manager.check_chocolatey_installed()
                self.logger.run_on_ui(
                    lambda: self._continue_opening_manager(manager, installed)
                )
            except Exception as e:
                error = str(e)
                self.logger.log_error(
                    f"Erro ao verificar Chocolatey: {error}"
                )
                self.logger.run_on_ui(
                    lambda: messagebox.showerror(
                        "Erro", f"Erro ao verificar Chocolatey:\n{error}"
                    )
                )

        threading.Thread(target=check_chocolatey, daemon=True).start()

    def _continue_opening_manager(self, manager, chocolatey_installed):
        if not chocolatey_installed:
            if messagebox.askyesno(
                "Chocolatey Não Encontrado",
                "O Chocolatey não está instalado e é necessário.\n\n"
                "Deseja instalá-lo automaticamente?",
            ):
                self.install_chocolatey_with_progress(manager)
            return
        self.create_software_manager_interface(manager)

    # ── Instalação do Chocolatey ─────────────────────────────────────────────

    def install_chocolatey_with_progress(self, manager):
        win = ctk.CTkToplevel(self.parent.root)
        win.title("Instalando Chocolatey")
        win.geometry("400x160")
        win.resizable(False, False)
        win.configure(fg_color=COLORS["content_bg"])
        win.transient(self.parent.root)
        win.grab_set()
        win.geometry(
            f"+{self.parent.root.winfo_rootx() + 50}"
            f"+{self.parent.root.winfo_rooty() + 50}"
        )

        frame = ctk.CTkFrame(win, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=16)

        ctk.CTkLabel(
            frame,
            text="Instalando Chocolatey...",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_primary"],
        ).pack(pady=(0, 10))

        bar = ctk.CTkProgressBar(
            frame, mode="indeterminate", progress_color=COLORS["accent"]
        )
        bar.pack(fill="x", pady=(0, 10))
        bar.start()

        ctk.CTkLabel(
            frame,
            text="Por favor, aguarde...",
            text_color=COLORS["text_muted"],
            font=ctk.CTkFont(size=11),
        ).pack()

        def install_in_thread():
            try:
                if manager.check_admin_privileges():
                    success = manager.install_chocolatey()
                else:
                    elevated, results = run_elevated_operation(
                        "install_chocolatey"
                    )
                    if not elevated:
                        raise RuntimeError(results)
                    success = results[0]["returncode"] == 0

                def show_result():
                    bar.stop()
                    win.destroy()
                    if success:
                        messagebox.showinfo(
                            "Sucesso", "Chocolatey instalado com sucesso!"
                        )
                    else:
                        messagebox.showerror(
                            "Erro", "Falha na instalação do Chocolatey."
                        )

                self.logger.run_on_ui(show_result)
            except Exception as e:
                error = str(e)

                def show_error():
                    bar.stop()
                    win.destroy()
                    messagebox.showerror("Erro", f"Erro durante instalação:\n{error}")

                self.logger.log_error(f"Erro durante instalação do Chocolatey: {error}")
                self.logger.run_on_ui(show_error)

        threading.Thread(target=install_in_thread, daemon=True).start()

    # ── Interface principal do gerenciador ───────────────────────────────────

    def create_software_manager_interface(self, manager):
        self.software_window = ctk.CTkToplevel(self.parent.root)
        self.software_window.title("Gerenciador de Software — ScriptNive")
        self.software_window.geometry("820x620")
        self.software_window.configure(fg_color=COLORS["content_bg"])
        self.software_window.resizable(True, True)
        self.software_window.transient(self.parent.root)
        self.software_window.grab_set()

        self.software_manager = manager
        self.software_list = []
        self.setup_software_interface()
        self.load_software_list()

    def setup_software_interface(self):
        win = self.software_window

        # Layout: topo (lista) + baixo (log)
        win.rowconfigure(0, weight=3)
        win.rowconfigure(1, weight=1)
        win.columnconfigure(0, weight=1)

        # ── Painel superior ──────────────────────────────────────────────────
        top = ctk.CTkFrame(
            win,
            fg_color=COLORS["card_bg"],
            corner_radius=10,
            border_width=1,
            border_color="#2d2d44",
        )
        top.grid(row=0, column=0, sticky="nsew", padx=14, pady=(14, 6))
        top.rowconfigure(1, weight=1)
        top.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            top,
            text="Selecione o software para reinstalar:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_primary"],
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 6))

        # Lista com scrollbar
        list_frame = ctk.CTkFrame(top, fg_color="transparent")
        list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 8))
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        self.software_listbox = tk.Listbox(
            list_frame,
            bg="#1a1a2e",
            fg="#94a3b8",
            selectbackground=COLORS["accent"],
            selectforeground="#ffffff",
            relief="flat",
            borderwidth=0,
            font=("Consolas", 10),
            activestyle="none",
        )
        sb = ctk.CTkScrollbar(list_frame, command=self.software_listbox.yview)
        self.software_listbox.configure(yscrollcommand=sb.set)
        self.software_listbox.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")

        # Botões
        btn_row = ctk.CTkFrame(top, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 12))

        ctk.CTkButton(
            btn_row,
            text="🔄  Atualizar Lista",
            command=self.load_software_list,
            fg_color=COLORS["card_hover"],
            hover_color="#3a3a55",
            border_width=1,
            border_color="#3d3d5c",
            corner_radius=8,
            height=34,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_row,
            text="⬇  Reinstalar Selecionado",
            command=self.reinstall_selected_software,
            fg_color=COLORS["info"],
            hover_color="#2563eb",
            corner_radius=8,
            height=34,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_row,
            text="✕  Fechar",
            command=self.software_window.destroy,
            fg_color=COLORS["card_hover"],
            hover_color="#3a3a55",
            border_width=1,
            border_color="#3d3d5c",
            corner_radius=8,
            height=34,
        ).pack(side="right")

        # ── Painel de log ────────────────────────────────────────────────────
        log_outer = ctk.CTkFrame(
            win,
            fg_color=COLORS["card_bg"],
            corner_radius=10,
            border_width=1,
            border_color="#2d2d44",
        )
        log_outer.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        log_outer.rowconfigure(1, weight=1)
        log_outer.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            log_outer,
            text="Log de Operações",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text_muted"],
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(8, 2))

        log_inner = ctk.CTkFrame(log_outer, fg_color="transparent")
        log_inner.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        log_inner.rowconfigure(0, weight=1)
        log_inner.columnconfigure(0, weight=1)

        self.software_log_text = tk.Text(
            log_inner,
            bg="#1a1a2e",
            fg="#94a3b8",
            relief="flat",
            borderwidth=0,
            font=("Consolas", 10),
            wrap="word",
            padx=8,
            pady=6,
            state="normal",
        )
        log_sb = ctk.CTkScrollbar(log_inner, command=self.software_log_text.yview)
        self.software_log_text.configure(yscrollcommand=log_sb.set)
        self.software_log_text.grid(row=0, column=0, sticky="nsew")
        log_sb.grid(row=0, column=1, sticky="ns")

    # ── Lógica ───────────────────────────────────────────────────────────────

    def log_software_message(self, message):
        if self.software_log_text:
            self.software_log_text.insert(tk.END, f"{message}\n")
            self.software_log_text.see(tk.END)

    def load_software_list(self):
        self.log_software_message("Carregando lista de software instalado...")

        def _run():
            try:
                self.software_list = self.software_manager.get_installed_software()
                self.logger.run_on_ui(self.update_software_listbox)
            except Exception as e:
                error = str(e)
                self.logger.log_error(f"Erro ao carregar lista de software: {error}")
                self.logger.run_on_ui(
                    lambda: self.log_software_message(
                        f"Erro ao carregar software: {error}"
                    )
                )

        threading.Thread(target=_run, daemon=True).start()

    def update_software_listbox(self):
        if self.software_listbox:
            self.software_listbox.delete(0, tk.END)
            for i, sw in enumerate(self.software_list):
                self.software_listbox.insert(tk.END, f"  {i:3d}  {sw['display_name']}")
            self.log_software_message(
                f"Encontrados {len(self.software_list)} softwares instalados."
            )

    def reinstall_selected_software(self):
        if not self.software_listbox:
            return
        sel = self.software_listbox.curselection()
        if not sel:
            messagebox.showwarning(
                "Seleção necessária", "Por favor, selecione um software da lista."
            )
            return

        sw = self.software_list[sel[0]]
        if not messagebox.askyesno(
            "Confirmar Reinstalação",
            f"Deseja desinstalar e reinstalar:\n\n{sw['display_name']}\n\n"
            "1. Desinstala o software atual\n"
            "2. Reinstala via Chocolatey\n\nContinuar?",
        ):
            return

        def _run():
            try:
                self.logger.run_on_ui(
                    lambda: self.log_software_message(
                        f"Iniciando reinstalação de: {sw['display_name']}"
                    )
                )
                if self.software_manager.check_admin_privileges():
                    success, message = (
                        self.software_manager.process_software_reinstall(sw)
                    )
                else:
                    elevated, results = run_elevated_operation(
                        "software_reinstall", arguments={"software": sw}
                    )
                    if not elevated:
                        raise RuntimeError(results)
                    result = results[0]
                    success = result["returncode"] == 0
                    message = result["stdout"] or result["stderr"]
                icon = "✅" if success else "❌"
                self.logger.run_on_ui(
                    lambda: self.log_software_message(f"{icon} {message}")
                )
                if success:
                    self.logger.run_on_ui(
                        lambda: messagebox.showinfo("Sucesso", message)
                    )
                else:
                    self.logger.run_on_ui(
                        lambda: messagebox.showerror("Erro", message)
                    )
                self.logger.run_on_ui(self.load_software_list)
            except Exception as e:
                msg = f"Erro durante reinstalação: {e}"
                self.logger.log_error(msg)
                self.logger.run_on_ui(
                    lambda: self.log_software_message(f"❌ {msg}")
                )
                self.logger.run_on_ui(
                    lambda: messagebox.showerror("Erro", msg)
                )

        threading.Thread(target=_run, daemon=True).start()
