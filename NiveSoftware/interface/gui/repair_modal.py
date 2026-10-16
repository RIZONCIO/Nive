"""
repair_modal.py - Diálogo de reparo completo do Windows (customtkinter)
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

COLORS = {
    "content_bg": "#1e1e2e",
    "card_bg": "#252537",
    "accent": "#4f9cf9",
    "text_primary": "#e2e8f0",
    "text_muted": "#8892a4",
    "success": "#22c55e",
    "danger": "#ef4444",
}


class RepairDialog:
    """Diálogo de reparo completo do Windows — modernizado."""

    def __init__(self, parent_interface):
        self.parent = parent_interface
        self.system_commands = parent_interface.system_commands
        self.config = parent_interface.config
        self.logger = parent_interface.logger

        self.progress_window = None
        self.progress_var = None
        self.progress_label_var = None
        self.progress_close_btn = None

    def complete_repair_placeholder(self):
        """Executar Reparo Completo do Windows."""
        try:
            confirm = messagebox.askyesno(
                "ATENÇÃO - Reparo Completo do Windows",
                "Esta operação irá:\n\n"
                "• Executar reparos profundos no sistema\n"
                "• Resetar configurações de rede\n"
                "• Limpar arquivos do Windows Update\n"
                "• Remover software pirata (se encontrado)\n"
                "• Re-registrar DLLs críticas\n"
                "• Agendar verificação de disco\n\n"
                "ESTE PROCESSO PODE DEMORAR MUITO TEMPO!\n"
                "Deseja continuar?",
            )

            if not confirm:
                self.parent.update_status("Reparo completo cancelado pelo usuário")
                return

            self.create_progress_window("Reparo Completo do Windows")

            def progress_callback(percentage, step_description):
                self.logger.run_on_ui(
                    lambda value=percentage, description=step_description: (
                        self._update_repair_progress(value, description)
                    )
                )

            def success_callback_wrapper(_message):
                self.logger.run_on_ui(self._handle_repair_success)

            def error_callback_wrapper(error):
                self.logger.run_on_ui(
                    lambda message=error: self._handle_repair_error(message)
                )

            self.system_commands.complete_windows_repair(
                progress_callback, success_callback_wrapper, error_callback_wrapper
            )

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao iniciar reparo completo:\n{e}")
            self.close_progress_window()

    def _handle_repair_success(self):
        if self.progress_close_btn:
            self.progress_close_btn.configure(state="normal")
            self.progress_label_var.set("Reparo concluído com sucesso!")
            self.progress_var.set(1.0)
        if messagebox.askyesno("Reiniciar", "Reiniciar o computador agora?"):
            self.system_commands.schedule_reboot_async(
                lambda error: messagebox.showerror(
                    "Erro",
                    f"Não foi possível agendar a reinicialização:\n{error}",
                )
            )
        self.close_progress_window()

    def _handle_repair_error(self, error):
        if self.progress_close_btn:
            self.progress_close_btn.configure(state="normal")
            self.progress_label_var.set("Erro durante o reparo!")
        messagebox.showerror(
            "Erro no Reparo",
            f"Ocorreu um erro durante o reparo completo:\n\n{error}\n\n"
            "Verifique o log para mais detalhes.",
        )
        self.close_progress_window()

    def _update_repair_progress(self, percentage, step_description):
        if self.progress_var and self.progress_window:
            self.progress_var.set(percentage / 100.0)
            self.progress_label_var.set(step_description)

    def create_progress_window(self, title: str):
        """Janela de progresso modernizada."""
        self.progress_window = ctk.CTkToplevel(self.parent.root)
        self.progress_window.title(title)
        self.progress_window.geometry("460x160")
        self.progress_window.resizable(False, False)
        self.progress_window.configure(fg_color=COLORS["content_bg"])
        self.progress_window.transient(self.parent.root)
        self.progress_window.grab_set()

        x = self.parent.root.winfo_rootx() + 50
        y = self.parent.root.winfo_rooty() + 50
        self.progress_window.geometry(f"+{x}+{y}")

        container = ctk.CTkFrame(self.progress_window, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=16)

        self.progress_label_var = tk.StringVar(value="Iniciando...")
        ctk.CTkLabel(
            container,
            textvariable=self.progress_label_var,
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_primary"],
            anchor="w",
        ).pack(fill="x", pady=(0, 8))

        self.progress_var = tk.DoubleVar(value=0.0)
        progress_bar = ctk.CTkProgressBar(
            container,
            variable=self.progress_var,
            width=400,
            progress_color=COLORS["accent"],
        )
        progress_bar.pack(fill="x", pady=(0, 12))

        self.progress_close_btn = ctk.CTkButton(
            container,
            text="Fechar",
            state="disabled",
            command=self.close_progress_window,
            width=100,
            fg_color=COLORS["card_bg"],
            hover_color="#2e2e45",
            border_width=1,
            border_color="#3d3d5c",
        )
        self.progress_close_btn.pack(anchor="e")

    def close_progress_window(self):
        """Fecha a janela de progresso."""
        try:
            if self.progress_window and self.progress_window.winfo_exists():
                self.progress_window.grab_release()
                self.progress_window.destroy()
                self.progress_window = None
        except Exception:
            pass
