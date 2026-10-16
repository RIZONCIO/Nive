"""
boost_ui.py - Interface de otimização com ícones Font Awesome
"""

import customtkinter as ctk
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
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "info": "#3b82f6",
    "purple": "#a855f7",
}

STYLE_COLORS = {
    "warning": COLORS["warning"],
    "danger": COLORS["danger"],
    "info": COLORS["info"],
    "success": COLORS["success"],
    "primary": COLORS["accent"],
}


def _darken(hex_color: str, factor: float = 0.75) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}"


class OptimizationUI:
    def __init__(self, optimization_tab):
        self.parent = optimization_tab

    def create_optimization_tab(self, notebook):
        page = ctk.CTkScrollableFrame(
            notebook,
            fg_color=COLORS["content_bg"],
            scrollbar_fg_color=COLORS["content_bg"],
            scrollbar_button_color="#2d2d44",
            corner_radius=0,
        )

        container = ctk.CTkFrame(page, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=24, pady=16)

        # Título
        ctk.CTkLabel(
            container,
            text="NiveBoost — Ferramentas de Otimização",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS["accent"],
        ).pack(pady=(0, 4))
        ctk.CTkLabel(
            container,
            text="Versão 1.1.0",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"],
        ).pack(pady=(0, 16))

        self._section(container, "Menu de Otimização")
        self._create_optimization_buttons(container)
        self._create_warning_section(container)

        return page

    def _section(self, parent, text):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(
            f,
            text=text,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left")
        ctk.CTkFrame(f, height=2, fg_color="#3d3d5c", corner_radius=1).pack(
            side="left", fill="x", expand=True, padx=(10, 0), pady=10
        )

    def _create_optimization_buttons(self, parent):
        # (icon_key, texto, command, style, descrição)
        OPTIONS = [
            (
                "wrench",
                "Desabilitar Alguns Serviços do Windows",
                self.parent.disable_windows_services,
                "warning",
                "Altera somente serviços legados ou opcionais selecionados",
            ),
            (
                "calendar",
                "Desabilitar Tweaks de Tarefas Agendadas",
                self.parent.disable_scheduled_tasks,
                "warning",
                "Desabilita tarefas selecionadas de telemetria e diagnóstico",
            ),
            (
                "box",
                "Desabilitar Alguns Softwares do Windows",
                self.parent.disable_windows_software,
                "warning",
                "Desabilita aplicativos e recursos desnecessários",
            ),
            (
                "user_secret",
                "Remover Telemetria e Coleta de Dados",
                self.parent.remove_telemetry,
                "danger",
                "Remove sistemas de coleta de dados e telemetria",
            ),
            (
                "trash",
                "Remover Features Não Usadas",
                self.parent.remove_unused_features,
                "warning",
                "Remove recursos e funcionalidades não utilizadas",
            ),
            (
                "paintbrush",
                "Remover Animações Inúteis",
                self.parent.remove_animations,
                "info",
                "Altera preferências visuais do usuário atual",
            ),
            (
                "search",
                "Desabilitar Busca Web na Barra",
                self.parent.disable_web_search,
                "info",
                "Desabilita busca online na barra de pesquisa do Windows",
            ),
            (
                "globe",
                "Cache de Navegadores",
                self.parent.disable_browser_cache,
                "warning",
                "Indisponível: nenhuma alteração de cache será aplicada",
            ),
            (
                "lock",
                "Desabilitar Propagandas na Tela Bloqueio",
                self.parent.disable_lock_screen_ads,
                "success",
                "Remove propagandas e sugestões da tela de bloqueio",
            ),
            (
                "network",
                "Otimizar o Edge",
                self.parent.optimize_edge,
                "primary",
                "Aplica otimizações específicas para o Microsoft Edge",
            ),
            (
                "bolt",
                "Aplicar Ajustes do Windows",
                self.parent.accelerate_windows,
                "success",
                "Aplica ajustes predefinidos de Registro e configuração",
            ),
        ]

        for icon_key, text, command, style, description in OPTIONS:
            color = STYLE_COLORS.get(style, COLORS["accent"])

            row = ctk.CTkFrame(
                parent,
                fg_color=COLORS["card_bg"],
                corner_radius=10,
                border_width=1,
                border_color="#2d2d44",
            )
            row.pack(fill="x", pady=4)

            # Botão com ícone FA
            btn_frame = ctk.CTkFrame(
                row, fg_color=color, corner_radius=8, height=36, width=340
            )
            btn_frame.pack_propagate(False)
            btn_frame.pack(side="left", padx=12, pady=10)

            inner = ctk.CTkFrame(btn_frame, fg_color="transparent")
            inner.place(relx=0.5, rely=0.5, anchor="center")

            ico_lbl = ctk.CTkLabel(
                inner,
                text=ic.get(icon_key),
                font=ctk.CTkFont(
                    family=ic.family(icon_key), size=13, weight=ic.weight(icon_key)
                ),
                text_color="#ffffff",
            )
            ico_lbl.pack(side="left")

            txt_lbl = ctk.CTkLabel(
                inner,
                text=f"  {text}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#ffffff",
            )
            txt_lbl.pack(side="left")

            # Hover & clique
            hover_color = _darken(color)
            for w in (btn_frame, inner, ico_lbl, txt_lbl):
                w.bind(
                    "<Enter>",
                    lambda e, f=btn_frame, hc=hover_color: f.configure(fg_color=hc),
                )
                w.bind(
                    "<Leave>", lambda e, f=btn_frame, nc=color: f.configure(fg_color=nc)
                )
                w.bind("<Button-1>", lambda e, cmd=command: cmd())

            # Descrição
            description_label = ctk.CTkLabel(
                row,
                text=description,
                font=ctk.CTkFont(size=11),
                text_color=COLORS["text_muted"],
                anchor="w",
                wraplength=320,
                justify="left",
            )
            description_label.pack(
                side="left", padx=(0, 12), fill="x", expand=True
            )

            def update_description_wrap(
                event, label=description_label, button=btn_frame
            ):
                available_width = event.width - button.winfo_width() - 36
                wraplength = max(120, min(320, available_width))
                if label.cget("wraplength") != wraplength:
                    label.configure(wraplength=wraplength)

            row.bind("<Configure>", update_description_wrap)

    def _create_warning_section(self, parent):
        warn = ctk.CTkFrame(
            parent,
            fg_color="#2a1a1a",
            corner_radius=10,
            border_width=1,
            border_color=COLORS["danger"],
        )
        warn.pack(fill="x", pady=(20, 8))

        # Cabeçalho do aviso com ícone FA
        header = ctk.CTkFrame(warn, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 4))

        ctk.CTkLabel(
            header,
            text=ic.get("times"),
            font=ctk.CTkFont(
                family=ic.family("times"), size=14, weight=ic.weight("times")
            ),
            text_color=COLORS["danger"],
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text="  IMPORTANTE — LEIA ANTES DE USAR",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["danger"],
        ).pack(side="left")

        ctk.CTkLabel(
            warn,
            text=(
                "ATENÇÃO: algumas alterações não têm restauração automática.\n\n"
                "  •  Crie um ponto de restauração antes de alterações de sistema\n"
                "  •  Leia as informações sobre cada otimização antes de aplicar\n"
                "  •  Não execute mais de uma otimização por vez\n"
                "  •  O UAC será solicitado somente nas operações administrativas\n"
                "  •  Reinicie apenas se o resultado da operação recomendar\n\n"
                "Nenhum ganho de desempenho é garantido; os efeitos variam conforme o sistema."
            ),
            font=ctk.CTkFont(size=11),
            text_color="#f87171",
            justify="left",
            anchor="w",
            wraplength=620,
        ).pack(anchor="w", padx=16, pady=(0, 14))

    def show_progress_dialog(self, title: str = "Executando Otimização"):
        import tkinter as tk

        win = ctk.CTkToplevel(self.parent.parent.root)
        win.title(title)
        win.geometry("460x260")
        win.configure(fg_color=COLORS["content_bg"])
        win.resizable(False, False)
        win.transient(self.parent.parent.root)
        win.grab_set()
        win.update_idletasks()
        x = win.winfo_screenwidth() // 2 - 230
        y = win.winfo_screenheight() // 2 - 130
        win.geometry(f"460x260+{x}+{y}")

        status_label = ctk.CTkLabel(
            win,
            text="Executando otimizações...",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_primary"],
        )
        status_label.pack(pady=(20, 8))

        progress_bar = ctk.CTkProgressBar(
            win, width=380, mode="indeterminate", progress_color=COLORS["accent"]
        )
        progress_bar.pack(pady=(0, 12))
        progress_bar.start()

        log_frame = ctk.CTkFrame(win, fg_color=COLORS["card_bg"], corner_radius=8)
        log_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        log_text = tk.Text(
            log_frame,
            bg="#1a1a2e",
            fg="#94a3b8",
            relief="flat",
            borderwidth=0,
            font=("Consolas", 10),
            wrap="word",
            padx=8,
            pady=6,
            height=6,
        )
        sb = ctk.CTkScrollbar(log_frame, command=log_text.yview)
        log_text.configure(yscrollcommand=sb.set)
        log_text.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        return win, status_label, progress_bar, log_text
