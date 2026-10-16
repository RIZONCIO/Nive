"""
tools.py - Aba de ferramentas com ícones Font Awesome
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
try:
    from diagnosis.cim.system_info import get_pc_info_formatted
except ImportError:
    try:
        from NiveSoftware.diagnosis.cim.system_info import get_pc_info_formatted
    except ImportError:
        from core.info import get_pc_info_formatted

try:
    from ..widgets import IconButton
except (ImportError, ValueError):
    try:
        from interface.gui.widgets import IconButton
    except ImportError:
        from gui.widgets import IconButton

try:
    from shared.utilities import icons as ic
except ImportError:
    try:
        from NiveSoftware.shared.utilities import icons as ic
    except ImportError:
        from utils import icons as ic

COLORS = {
    "content_bg": "#1e1e2e",
    "card_bg": "#252537",
    "card_hover": "#2e2e45",
    "accent": "#4f9cf9",
    "text_primary": "#e2e8f0",
    "text_muted": "#8892a4",
    "success": "#22c55e",
    "info": "#3b82f6",
    "sidebar_bg": "#1a1a2e",
}


def alpha_blend(hex_color: str, bg: str = "#1e1e2e", alpha: float = 0.25) -> str:
    def parse(h):
        h = h.lstrip("#")
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    r1, g1, b1 = parse(hex_color)
    r2, g2, b2 = parse(bg)
    return "#{:02x}{:02x}{:02x}".format(
        int(r1 * alpha + r2 * (1 - alpha)),
        int(g1 * alpha + g2 * (1 - alpha)),
        int(b1 * alpha + b2 * (1 - alpha)),
    )


class ToolsTab:
    def __init__(self, parent_interface, main_tab):
        self.parent = parent_interface
        self.main_tab = main_tab
        self.system_commands = parent_interface.system_commands
        self.logger = parent_interface.logger
        self.log_text = None

    def create_tools_tab(self, notebook):
        page = ctk.CTkScrollableFrame(
            notebook,
            fg_color=COLORS["content_bg"],
            scrollbar_fg_color=COLORS["content_bg"],
            scrollbar_button_color="#2d2d44",
            corner_radius=0,
        )

        # ── Diagnóstico ───────────────────────────────────────────────────────
        self._section(page, "Diagnóstico")

        diag_frame = ctk.CTkFrame(page, fg_color="transparent")
        diag_frame.pack(fill="x", padx=16, pady=(4, 8))

        IconButton(
            diag_frame,
            icon_name="clipboard",
            text="Abrir Monitor de Confiabilidade",
            command=self.check_diagnostics,
            fg_color=COLORS["info"],
            hover_color="#2563eb",
            height=38,
            font_size=13,
            icon_size=14,
        ).pack(side="left", padx=(0, 10))

        IconButton(
            diag_frame,
            icon_name="desktop",
            text="Informações do PC",
            command=self.show_pc_info,
            fg_color=COLORS["card_bg"],
            hover_color=COLORS["card_hover"],
            border_width=1,
            border_color="#3d3d5c",
            height=38,
            font_size=13,
            icon_size=14,
        ).pack(side="left")

        self.main_tab.create_system_tools_section(page)

        # ── Log de Atividades ─────────────────────────────────────────────────
        self._section(page, "Log de Atividades")

        log_card = ctk.CTkFrame(
            page,
            fg_color=COLORS["card_bg"],
            corner_radius=12,
            border_width=1,
            border_color="#2d2d44",
        )
        log_card.pack(fill="both", expand=True, padx=16, pady=(4, 16))

        self.log_text = tk.Text(
            log_card,
            bg="#1a1a2e",
            fg="#94a3b8",
            insertbackground="white",
            selectbackground="#0f3460",
            relief="flat",
            borderwidth=0,
            font=("Consolas", 11),
            wrap="word",
            padx=12,
            pady=8,
        )
        scrollbar = ctk.CTkScrollbar(log_card, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scrollbar.pack(side="right", fill="y", pady=8, padx=(0, 4))

        # Botões do log
        btn_row = ctk.CTkFrame(page, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(0, 16))

        IconButton(
            btn_row,
            icon_name="trash",
            text="Limpar Log",
            command=self.clear_log,
            fg_color=COLORS["card_bg"],
            hover_color=COLORS["card_hover"],
            border_width=1,
            border_color="#3d3d5c",
            height=34,
            font_size=12,
            icon_size=12,
        ).pack(side="left", padx=(0, 8))

        IconButton(
            btn_row,
            icon_name="save",
            text="Salvar Log",
            command=self.save_log,
            fg_color=COLORS["info"],
            hover_color="#2563eb",
            height=34,
            font_size=12,
            icon_size=12,
        ).pack(side="left")

        return page

    def _section(self, parent, text):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=16, pady=(18, 4))
        ctk.CTkLabel(
            f,
            text=text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left")
        ctk.CTkFrame(
            f,
            height=2,
            fg_color=alpha_blend(COLORS["accent"], COLORS["content_bg"], 0.25),
            corner_radius=1,
        ).pack(side="left", fill="x", expand=True, padx=(10, 0), pady=10)

    def check_diagnostics(self):
        try:
            self.system_commands.open_system_tools()["diagnostics"]()
            self.parent.update_status("Monitor de Confiabilidade aberto")
        except Exception as e:
            self.logger.log_error(f"Erro ao abrir o Monitor de Confiabilidade: {e}")
            messagebox.showerror("Erro", str(e))

    def show_pc_info(self):
        win = ctk.CTkToplevel(self.parent.root)
        win.title("Informações do Sistema")
        win.geometry("820x580")
        win.configure(fg_color="#1e1e2e")
        tb = ctk.CTkTextbox(win, font=ctk.CTkFont(family="Consolas", size=11))
        tb.pack(fill="both", expand=True, padx=14, pady=14)
        tb.insert("end", "Coletando informações...\n")
        win.update()
        try:
            tb.delete("1.0", "end")
            tb.insert("end", get_pc_info_formatted())
        except Exception as e:
            tb.insert("end", f"Erro: {e}")
        tb.configure(state="disabled")
        ctk.CTkButton(win, text="Fechar", command=win.destroy, width=100).pack(
            pady=(0, 12)
        )

    def clear_log(self):
        if self.log_text:
            self.logger.clear_widget()
            self.parent.update_status("Log limpo")

    def save_log(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Texto", "*.txt"), ("Todos", "*.*")],
        )
        if path:
            if self.logger.save_logs_to_file(path):
                messagebox.showinfo("Sucesso", f"Log salvo em:\n{path}")
            else:
                messagebox.showerror("Erro", "Erro ao salvar log.")
