"""
about.py - Aba de informações e créditos modernizada com customtkinter
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path
from tkinter import messagebox
import customtkinter as ctk

COLORS = {
    "content_bg": "#1e1e2e",
    "card_bg": "#252537",
    "card_hover": "#2e2e45",
    "accent": "#4f9cf9",
    "accent2": "#7b61ff",
    "text_primary": "#e2e8f0",
    "text_muted": "#8892a4",
    "success": "#22c55e",
    "info": "#3b82f6",
    "danger": "#ef4444",
}


def _label_frame(parent, title: str, border_color: str = "#3d3d5c") -> tuple:
    """
    Simula um LabelFrame: retorna (container, inner_frame).
    Usar inner_frame para colocar os filhos.
    """
    container = ctk.CTkFrame(
        parent,
        fg_color=COLORS["card_bg"],
        corner_radius=10,
        border_width=1,
        border_color=border_color,
    )
    ctk.CTkLabel(
        container,
        text=f"  {title}  ",
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color=COLORS["text_muted"],
        fg_color=COLORS["card_bg"],
    ).place(x=14, y=-10)
    inner = ctk.CTkFrame(container, fg_color="transparent")
    inner.pack(fill="both", expand=True, padx=14, pady=(18, 12))
    return container, inner


class InfoTab:
    """Aba de informações e créditos — modernizada com customtkinter."""

    def __init__(self, parent_interface):
        self.parent = parent_interface
        self.config = parent_interface.config
        self.logger = parent_interface.logger

    # ── PDF ──────────────────────────────────────────────────────────────────

    def _get_doc_path(self) -> Path:
        current = Path(__file__).resolve()
        for parent in current.parents:
            cand = parent / "DOC" / "usuario" / "Documentação-Técnica-do-ScriptNive.pdf"
            if cand.exists():
                return cand
            cand = parent / "DOC" / "Documentação-Técnica-do-ScriptNive.pdf"
            if cand.exists():
                return cand
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            cand = Path(meipass) / "DOC" / "Documentação-Técnica-do-ScriptNive.pdf"
            if cand.exists():
                return cand
        return Path("C:/Nive/Documentação-Técnica-do-ScriptNive.pdf")

    def _open_local_doc(self):
        pdf = self._get_doc_path()
        if not pdf.exists():
            messagebox.showerror(
                "Arquivo não encontrado", f"Não encontrei a documentação:\n{pdf}"
            )
            self.logger.log_error("Documentação PDF não encontrada")
            return
        try:
            if sys.platform.startswith("win"):
                os.startfile(str(pdf))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(pdf)], check=False)
            else:
                subprocess.run(["xdg-open", str(pdf)], check=False)
            self.logger.log_success("Documentação PDF aberta")
        except Exception:
            webbrowser.open(pdf.as_uri())
            self.logger.log_success("Documentação PDF aberta via navegador")

    # ── Criação da aba ───────────────────────────────────────────────────────

    def create_info_tab(self, notebook):
        """Cria e retorna o frame da aba Sobre — sem notebook.add()."""

        page = ctk.CTkScrollableFrame(
            notebook,
            fg_color=COLORS["content_bg"],
            scrollbar_fg_color=COLORS["content_bg"],
            scrollbar_button_color="#2d2d44",
            corner_radius=0,
        )

        inner = ctk.CTkFrame(page, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=32, pady=24)

        # ── Título ───────────────────────────────────────────────────────────
        ctk.CTkLabel(
            inner,
            text="ScriptNive",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color=COLORS["accent"],
        ).pack(pady=(0, 6))

        ctk.CTkLabel(
            inner,
            text=f"Versão {self.config.version} — Interface Gráfica",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_muted"],
        ).pack(pady=(0, 20))

        # ── Descrição ────────────────────────────────────────────────────────
        desc = (
            "ScriptNive é uma ferramenta completa para manutenção e otimização do Windows.\n"
            "Desenvolvida para facilitar tarefas de manutenção que normalmente requerem\n"
            "conhecimento técnico avançado.\n\n"
            "Características:\n"
            "  •  Interface gráfica moderna e intuitiva\n"
            "  •  Ferramentas de diagnóstico avançado\n"
            "  •  Limpeza automática do sistema\n"
            "  •  Reparos automáticos de erros\n"
            "  •  Otimização de performance\n"
            "  •  Log detalhado de operações"
        )
        ctk.CTkLabel(
            inner,
            text=desc,
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_primary"],
            justify="left",
            anchor="w",
            wraplength=560,
        ).pack(fill="x", pady=(0, 20))

        # ── Créditos ─────────────────────────────────────────────────────────
        cred_box, cred_inner = _label_frame(inner, "Créditos")
        cred_box.pack(fill="x", pady=(0, 14))

        credits = (
            "Criador do ScriptNive:          Ryan Vinicius Carvalho Pereira\n"
            "Criador do Reparo Completo:   Ivo Dias\n"
            "Criador do OtimizadorEdge:     AFaustini\n"
            "Interface Gráfica:                 Python + customtkinter\n"
            "Data de Lançamento:             10/Set./2022"
        )
        ctk.CTkLabel(
            cred_inner,
            text=credits,
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color=COLORS["text_primary"],
            justify="left",
            anchor="w",
        ).pack(fill="x")

        # ── Links ─────────────────────────────────────────────────────────────
        links_box, links_inner = _label_frame(inner, "Links Úteis")
        links_box.pack(fill="x", pady=(0, 24))

        links = [
            ("📄  Documentação (PDF)", self._open_local_doc),
            ("📖  Docs Microsoft", self.config.get_link("microsoft_docs")),
            ("💡  DOS Tips", self.config.get_link("dos_tips")),
            ("🐙  GitHub", self.config.get_link("github")),
        ]

        btn_row = ctk.CTkFrame(links_inner, fg_color="transparent")
        btn_row.pack(fill="x")

        for text, action in links:
            if callable(action):
                cmd = lambda a=action, t=text: self._log_and_call(a, t)
            else:
                cmd = lambda u=action, t=text: self._log_and_open(u, t)
            ctk.CTkButton(
                btn_row,
                text=text,
                command=cmd,
                fg_color="transparent",
                hover_color=COLORS["card_hover"],
                border_width=1,
                border_color="#3d3d5c",
                text_color=COLORS["accent"],
                corner_radius=8,
                height=34,
                font=ctk.CTkFont(size=12),
            ).pack(side="left", padx=(0, 8), pady=4)

        return page

    def _log_and_call(self, action, text):
        try:
            action()
            self.logger.log_success(f"Ação executada: {text}")
        except Exception as e:
            self.logger.log_error(f"Erro ao executar {text}: {e}")

    def _log_and_open(self, url, text):
        try:
            webbrowser.open(url)
            self.logger.log_success(f"Link aberto: {text}")
        except Exception as e:
            self.logger.log_error(f"Erro ao abrir {text}: {e}")
