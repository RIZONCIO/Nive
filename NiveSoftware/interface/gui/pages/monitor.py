"""Página dedicada ao monitoramento técnico do computador."""

import customtkinter as ctk

try:
    from .home import COLORS
except (ImportError, ValueError):
    try:
        from interface.gui.pages.home import COLORS
    except ImportError:
        from pages.home import COLORS


class MonitoringTab:
    def __init__(self, main_tab):
        self.main_tab = main_tab

    def create_monitoring_tab(self, parent):
        page = ctk.CTkScrollableFrame(
            parent,
            fg_color=COLORS["content_bg"],
            scrollbar_fg_color=COLORS["content_bg"],
            scrollbar_button_color="#2d2d44",
            corner_radius=0,
        )
        page.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(
            page,
            fg_color="#171b2f",
            corner_radius=16,
            border_width=1,
            border_color="#2d2d44",
        )
        header.pack(fill="x", padx=18, pady=(16, 12))

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(fill="x", padx=18, pady=16)

        ctk.CTkLabel(
            title_frame,
            text="Monitoramento do Sistema",
            font=ctk.CTkFont(family="Segoe UI", size=30, weight="bold"),
            text_color="#edf6ff",
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_frame,
            text="Sensores, desempenho e estado do hardware em tempo real.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#90a4c7",
            anchor="w",
        ).pack(anchor="w", pady=(6, 0))

        status_row = ctk.CTkFrame(header, fg_color="transparent")
        status_row.pack(fill="x", padx=18, pady=(0, 16))

        badge = ctk.CTkFrame(
            status_row,
            fg_color="#102744",
            corner_radius=999,
            border_width=1,
            border_color="#1b4d82",
        )
        badge.pack(side="left")

        ctk.CTkLabel(
            badge,
            text="● Coleta ativa",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#6fe7ff",
            padx=12,
            pady=6,
        ).pack()

        ctk.CTkLabel(
            status_row,
            text="Painel técnico | dados reais do sistema",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#8ea3c7",
            anchor="e",
        ).pack(side="right", padx=(0, 10))

        self.main_tab.create_system_monitor_section(page)
        return page
