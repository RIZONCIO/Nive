import os
import shutil
import subprocess
import csv
import io
import math
import time
from collections import deque
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
import psutil
import threading
import platform
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
    "teal": "#14b8a6",
    "orange": "#f97316",
}


def alpha_blend(hex_color: str, bg: str = "#252537", alpha: float = 0.15) -> str:
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


class Tooltip:
    def __init__(self, widget, text, delay=400):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tip_window = None
        self._after_id = None
        widget.bind("<Enter>", self._schedule)
        widget.bind("<Leave>", self._hide)
        widget.bind("<Motion>", self._move)

    def _schedule(self, event=None):
        self._unschedule()
        self._after_id = self.widget.after(self.delay, self._show)

    def _unschedule(self):
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None

    def _show(self, event=None):
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_pointerx() + 12
        y = self.widget.winfo_pointery() + 12
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_attributes("-topmost", True)
        label = tk.Label(
            tw,
            text=self.text,
            justify="left",
            background="#20232a",
            foreground="#f8fafc",
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", 10),
            padx=8,
            pady=4,
            wraplength=260,
        )
        label.pack()
        tw.wm_geometry(f"+{x}+{y}")

    def _move(self, event):
        if self.tip_window:
            x = event.x_root + 12
            y = event.y_root + 12
            self.tip_window.wm_geometry(f"+{x}+{y}")

    def _hide(self, event=None):
        self._unschedule()
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


def make_action_card(
    parent, icon_key, title, subtitle, command, accent_color, row, col
):
    card = ctk.CTkFrame(
        parent,
        fg_color=COLORS["card_bg"],
        corner_radius=12,
        border_width=1,
        border_color="#2d2d44",
    )
    card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

    icon_frame = ctk.CTkFrame(
        card,
        fg_color=alpha_blend(accent_color, COLORS["card_bg"], 0.15),
        width=48,
        height=48,
        corner_radius=10,
    )
    icon_frame.pack_propagate(False)
    icon_frame.pack(side="left", padx=(14, 10), pady=14)

    icon_label = ctk.CTkLabel(
        icon_frame,
        text=ic.get(icon_key),
        font=ctk.CTkFont(
            family=ic.family(icon_key), size=20, weight=ic.weight(icon_key)
        ),
        text_color=accent_color,
    )
    icon_label.pack(expand=True)

    text_frame = ctk.CTkFrame(card, fg_color="transparent")
    text_frame.pack(side="left", fill="both", expand=True, pady=12, padx=(0, 14))

    title_label = ctk.CTkLabel(
        text_frame,
        text=title,
        font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
        text_color=COLORS["text_primary"],
        anchor="w",
    )
    title_label.pack(fill="x")

    subtitle_label = ctk.CTkLabel(
        text_frame,
        text=subtitle,
        font=ctk.CTkFont(size=11),
        text_color=COLORS["text_muted"],
        anchor="w",
        wraplength=190,
    )
    subtitle_label.pack(fill="x", pady=(2, 0))

    border_hover = alpha_blend(accent_color, COLORS["card_hover"], 0.38)

    def on_enter(e):
        card.configure(fg_color=COLORS["card_hover"], border_color=border_hover)

    def on_leave(e):
        card.configure(fg_color=COLORS["card_bg"], border_color="#2d2d44")

    def on_click(e):
        command()

    for w in (
        card,
        icon_frame,
        icon_label,
        text_frame,
        title_label,
        subtitle_label,
    ):
        w.bind("<Enter>", on_enter)
        w.bind("<Leave>", on_leave)
        w.bind("<Button-1>", on_click)

    Tooltip(card, subtitle)
    return card


class MainTab:
    def __init__(self, parent_interface):
        self.parent = parent_interface
        self.system_commands = parent_interface.system_commands
        self.config = parent_interface.config
        self.logger = parent_interface.logger
        self.monitor_running = False
        self.monitor_stop_event = threading.Event()
        self.monitor_thread = None
        self.cpu_history = deque(maxlen=60)
        self.ram_history = deque(maxlen=60)
        self.gpu_history = deque(maxlen=60)
        self.disk_history = deque(maxlen=60)
        self._disk_io_previous = {}
        self._disk_io_sample_time = None

    def create_main_tab(self, notebook):
        page = ctk.CTkScrollableFrame(
            notebook,
            fg_color=COLORS["content_bg"],
            scrollbar_fg_color=COLORS["content_bg"],
            scrollbar_button_color="#2d2d44",
            corner_radius=0,
        )

        self._create_computer_summary(page)

        self._section(page, "Tarefas Comuns")
        grid1 = ctk.CTkFrame(page, fg_color="transparent")
        grid1.pack(fill="x", padx=16, pady=(4, 8))
        grid1.columnconfigure((0, 1), weight=1, uniform="cards")

        COMMON = [
            (
                "trash",
                "Esvaziar Lixeira",
                "Remove arquivos deletados",
                self.system_commands.empty_recycle_bin,
                COLORS["success"],
            ),
            (
                "bolt",
                "Ativar GodMode",
                "Acesso a todas as configurações",
                self.system_commands.activate_godmode,
                COLORS["accent"],
            ),
            (
                "hdd",
                "Verificar Disco (C:)",
                "Verificação online com CHKDSK",
                self.system_commands.check_disk_errors,
                COLORS["warning"],
            ),
            (
                "microchip",
                "Verificar RAM",
                "Diagnóstico de memória",
                self.system_commands.check_ram,
                COLORS["info"],
            ),
            (
                "wrench",
                "Reparar Sistema",
                "SFC + DISM automático",
                self.system_commands.repair_system,
                COLORS["danger"],
            ),
            (
                "broom",
                "Limpar Temporários",
                "Apaga arquivos temp do sistema",
                self.system_commands.clean_temp_files,
                COLORS["teal"],
            ),
        ]
        for i, (k, t, s, c, col) in enumerate(COMMON):
            make_action_card(grid1, k, t, s, c, col, i // 2, i % 2)

        return page

    def _create_computer_summary(self, parent):
        self._section(parent, "Resumo do Computador")
        summary = ctk.CTkFrame(
            parent,
            fg_color=COLORS["card_bg"],
            corner_radius=12,
            border_width=1,
            border_color="#2d2d44",
        )
        summary.pack(fill="x", padx=16, pady=(4, 12))

        memory_gb = psutil.virtual_memory().total / (1024**3)
        details = (
            f"Nome: {platform.node()}\n"
            f"Sistema: {platform.system()} {platform.release()} "
            f"({platform.machine()})  •  RAM: {memory_gb:.1f} GB"
        )
        ctk.CTkLabel(
            summary,
            text=details,
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_primary"],
            justify="left",
            anchor="w",
            wraplength=600,
        ).pack(fill="x", padx=16, pady=12)

    def create_system_tools_section(self, parent):
        self._section(parent, "Ferramentas do Sistema")
        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="x", padx=16, pady=(4, 24))
        grid.columnconfigure((0, 1), weight=1, uniform="cards")

        SYSTEM = [
            (
                "task_manager",
                "Gerenciador de Tarefas",
                "Processos e desempenho",
                self.open_task_manager,
                COLORS["info"],
            ),
            (
                "shield",
                "Iniciar MRT",
                "Remove malware da Microsoft",
                self.start_mrt,
                COLORS["purple"],
            ),
            (
                "box",
                "Atualizar Programas",
                "Winget / Windows Update",
                self.system_commands.update_programs,
                COLORS["success"],
            ),
            (
                "sliders",
                "Reparar Som",
                "Reinicia serviço de áudio",
                self.system_commands.fix_audio,
                COLORS["orange"],
            ),
            (
                "box",
                "Reinstalar Software",
                "Instala pacotes essenciais",
                self.parent.reinstall_software_placeholder,
                COLORS["danger"],
            ),
            (
                "folder",
                "Deletar Pasta Corrompida",
                "Remove diretórios problemáticos",
                self.delete_corrupted_folders,
                COLORS["warning"],
            ),
            (
                "medkit",
                "Reparo Completo Windows",
                "Pipeline completo de reparo",
                self.parent.complete_repair_placeholder,
                COLORS["danger"],
            ),
            (
                "sliders",
                "Painel de Controle",
                "Configurações clássicas do Windows",
                self.open_control_panel,
                COLORS["text_muted"],
            ),
        ]
        for i, (k, t, s, c, col) in enumerate(SYSTEM):
            make_action_card(grid, k, t, s, c, col, i // 2, i % 2)

    def create_system_monitor_section(self, parent):
        """Cria o painel de sensores e gráficos em um layout premium."""
        self.monitor_updated_label = ctk.CTkLabel(
            parent,
            text="Aguardando a primeira amostra...",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLORS["text_muted"],
            anchor="e",
        )
        self.monitor_updated_label.pack(fill="x", padx=18, pady=(18, 8))

        cards = ctk.CTkFrame(parent, fg_color="transparent")
        cards.pack(fill="x", padx=16, pady=(0, 8))
        cards.grid_columnconfigure((0, 1), weight=1)

        self.cpu_label = self._metric_card(
            cards,
            title="CPU",
            accent=COLORS["accent"],
            default="Coletando a primeira amostra...",
            column=0,
            row=0,
            chart_color=COLORS["accent"],
        )
        self.cpu_chart = self.cpu_label["chart"]

        self.gpu_label = self._metric_card(
            cards,
            title="GPU",
            accent="#5fa2ff",
            default="Aguardando leitura do sensor...",
            column=1,
            row=0,
            chart_color="#5fa2ff",
        )
        self.gpu_chart = self.gpu_label["chart"]

        self.ram_label = self._metric_card(
            cards,
            title="RAM",
            accent=COLORS["teal"],
            default="Coletando a primeira amostra...",
            column=0,
            row=1,
            chart_color=COLORS["teal"],
        )
        self.ram_chart = self.ram_label["chart"]

        self.disk_label = self._metric_card(
            cards,
            title="Armazenamento",
            accent=COLORS["warning"],
            default="Coletando volumes e atividade...",
            column=1,
            row=1,
            chart_color=COLORS["warning"],
        )
        self.disk_chart = self.disk_label["chart"]

        self.sensor_note = ctk.CTkLabel(
            parent,
            text=(
                "Temperatura e consumo elétrico de CPU, SMART e temperatura de discos "
                "dependem de sensores não expostos pelas APIs instaladas. "
                "GPU é consultada por nvidia-smi quando disponível."
            ),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["text_muted"],
            justify="left",
            anchor="w",
            wraplength=760,
        )
        self.sensor_note.pack(fill="x", padx=20, pady=(8, 20))

    def _metric_card(self, parent, title, accent, default, column, row, chart_color):
        card = ctk.CTkFrame(
            parent,
            fg_color="#070b12",
            corner_radius=18,
            border_width=1,
            border_color="#182437",
        )
        card.grid(
            row=row,
            column=column,
            padx=8,
            pady=8,
            sticky="nsew",
        )

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(14, 4))

        icon_key = self._metric_icon_key(title)

        icon_wrap = ctk.CTkFrame(
            header,
            fg_color=alpha_blend(accent, "#070b12", 0.18),
            corner_radius=10,
            width=34,
            height=34,
        )
        icon_wrap.pack(side="left")
        icon_wrap.pack_propagate(False)

        icon = ctk.CTkLabel(
            icon_wrap,
            text=ic.get(icon_key),
            font=ctk.CTkFont(
                family=ic.family(icon_key), size=15, weight=ic.weight(icon_key)
            ),
            text_color=accent,
        )
        icon.pack(expand=True)

        title_block = ctk.CTkFrame(header, fg_color="transparent")
        title_block.pack(side="left", fill="x", expand=True, padx=(10, 0))

        ctk.CTkLabel(
            title_block,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#edf6ff",
            anchor="w",
        ).pack(fill="x")

        status = ctk.CTkLabel(
            header,
            text="ativo",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=accent,
        )
        status.pack(side="right")

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=14, pady=(4, 12))
        body.grid_columnconfigure(0, weight=0)
        body.grid_columnconfigure(1, weight=1)

        gauge = tk.Canvas(
            body,
            width=240,
            height=130,
            bg="#070b12",
            highlightthickness=0,
            borderwidth=0,
        )
        gauge.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 16))

        value_row = ctk.CTkFrame(body, fg_color="transparent")
        value_row.grid(row=0, column=1, sticky="new", pady=(8, 0))

        value_label = ctk.CTkLabel(
            value_row,
            text="--",
            font=ctk.CTkFont(family="Segoe UI", size=42, weight="bold"),
            text_color="#edf6ff",
            anchor="w",
        )
        value_label.pack(side="left")

        unit_label = ctk.CTkLabel(
            value_row,
            text="%",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=accent,
        )
        unit_label.pack(side="left", padx=(4, 0), pady=(18, 0))

        metric = ctk.CTkLabel(
            body,
            text=default,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#b9c7df",
            justify="left",
            anchor="w",
            wraplength=520,
        )
        metric.grid(row=1, column=1, sticky="new", pady=(2, 0))

        canvas = tk.Canvas(
            card,
            height=58,
            bg="#070b12",
            highlightthickness=0,
            borderwidth=0,
        )
        canvas.pack(fill="x", padx=14, pady=(0, 14))
        canvas.bind(
            "<Configure>",
            lambda event, widget=canvas, history=self._metric_history(title), line_color=chart_color: self._draw_history(
                widget, history, line_color, event.width
            ),
        )
        gauge.bind(
            "<Configure>",
            lambda event, widget=gauge, item=title, line_color=chart_color: self._draw_gauge(
                widget, getattr(widget, "_scriptnive_percent", None), line_color, item
            ),
        )

        self._draw_gauge(gauge, None, chart_color, title)
        return {
            "card": card,
            "metric": metric,
            "chart": canvas,
            "gauge": gauge,
            "value": value_label,
            "unit": unit_label,
            "status": status,
            "color": chart_color,
            "title": title,
        }

    def _metric_icon_key(self, title):
        return {
            "CPU": "cpu",
            "GPU": "gpu",
            "RAM": "memory",
            "Armazenamento": "disk",
        }.get(title, "chart_line")

    def _metric_history(self, title):
        return {
            "CPU": self.cpu_history,
            "GPU": self.gpu_history,
            "RAM": self.ram_history,
            "Armazenamento": self.disk_history,
        }.get(title, self.cpu_history)

    def _update_metric_card(self, card, percent, detail, color=None, status="ativo"):
        color = color or card["color"]
        muted = percent is None
        value_text = "--" if muted else f"{max(0.0, min(100.0, percent)):.0f}"
        card["value"].configure(text=value_text, text_color=color if not muted else COLORS["text_muted"])
        card["unit"].configure(text="%" if not muted else "", text_color=color)
        card["metric"].configure(text=detail, text_color="#b9c7df")
        card["status"].configure(text=status, text_color=color if not muted else COLORS["text_muted"])
        card["gauge"]._scriptnive_percent = percent
        self._draw_gauge(card["gauge"], percent, color, card["title"])
        self._draw_history(card["chart"], self._metric_history(card["title"]), color)

    def _create_history_chart(self, parent, title, color):
        chart_card = ctk.CTkFrame(
            parent,
            fg_color="#171b2f",
            corner_radius=18,
            border_width=1,
            border_color="#2c3a52",
        )
        chart_card.pack(fill="x", padx=16, pady=(4, 10))
        ctk.CTkLabel(
            chart_card,
            text=f"{title} — até 60 amostras recentes",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_muted"],
            anchor="w",
        ).pack(fill="x", padx=12, pady=(8, 0))
        canvas = tk.Canvas(
            chart_card,
            height=140,
            bg="#171b2f",
            highlightthickness=0,
            borderwidth=0,
        )
        canvas.pack(fill="x", padx=8, pady=(0, 8))
        canvas.bind(
            "<Configure>",
            lambda event, widget=canvas, history=(
                self.cpu_history if color == COLORS["accent"] else self.ram_history
            ), line_color=color: self._draw_history(
                widget, history, line_color, event.width
            ),
        )
        return canvas

    def _draw_history(self, canvas, history, color, available_width=None):
        canvas.delete("all")
        width = max(available_width or canvas.winfo_width(), 220)
        height = max(canvas.winfo_height(), 52)
        left, right, top, bottom = 14, width - 14, 8, height - 10

        canvas.create_rectangle(0, 0, width, height, fill="#070b12", outline="")

        for grid_y in range(1, 4):
            y = top + (bottom - top) * (grid_y / 4)
            canvas.create_line(left, y, right, y, fill="#111a28", width=1)

        values = list(history)
        if not values:
            canvas.create_text(
                width / 2,
                height / 2,
                text="aguardando dados em tempo real",
                fill=COLORS["text_muted"],
                anchor="center",
                font=("Segoe UI", 9, "bold"),
            )
            return

        if len(values) == 1:
            x_positions = [right]
        else:
            step = (right - left) / (len(values) - 1)
            x_positions = [left + index * step for index in range(len(values))]

        points = []
        for x, value in zip(x_positions, values):
            y = bottom - (bottom - top) * max(0.0, min(100.0, value)) / 100
            points.extend((x, y))

        if len(points) >= 4:
            fill_points = [left, bottom, *points, right, bottom]
            canvas.create_polygon(*fill_points, fill=alpha_blend(color, "#070b12", 0.12), outline="")
            canvas.create_line(*points, fill=alpha_blend(color, "#070b12", 0.45), width=6, smooth=True)
            canvas.create_line(*points, fill=color, width=2.5, smooth=True)
            canvas.create_oval(
                points[-2] - 1.5,
                points[-1] - 1.5,
                points[-2] + 1.5,
                points[-1] + 1.5,
                fill=color,
                outline=color,
            )
        else:
            canvas.create_oval(
                points[0] - 3,
                points[1] - 3,
                points[0] + 3,
                points[1] + 3,
                fill=color,
                outline=color,
            )

    def _draw_gauge(self, canvas, percent, color, title):
        canvas.delete("all")
        width = max(canvas.winfo_width(), 220)
        height = max(canvas.winfo_height(), 120)
        cx = width / 2
        cy = height - 14
        radius = min(width * 0.42, height * 0.88)
        bbox = (cx - radius, cy - radius, cx + radius, cy + radius)
        canvas.create_arc(
            bbox,
            start=180,
            extent=-180,
            style="arc",
            outline="#111a28",
            width=22,
        )

        pct = None if percent is None else max(0.0, min(100.0, float(percent)))
        segments = 36
        for index in range(segments):
            start = 180 - index * (180 / segments)
            active = pct is not None and index < round((pct / 100) * segments)
            outline = color if active else "#1b2230"
            width_line = 14 if active else 10
            canvas.create_arc(
                bbox,
                start=start,
                extent=-(180 / segments) * 0.58,
                style="arc",
                outline=outline,
                width=width_line,
            )

        if pct is not None:
            canvas.create_arc(
                (cx - radius * 0.72, cy - radius * 0.72, cx + radius * 0.72, cy + radius * 0.72),
                start=180,
                extent=-(pct / 100) * 180,
                style="arc",
                outline=alpha_blend(color, "#070b12", 0.65),
                width=4,
            )
            center_value = f"{pct:.0f}%"
            center_color = "#edf6ff"
        else:
            center_value = "--"
            center_color = COLORS["text_muted"]

        canvas.create_oval(
            cx - radius * 0.58,
            cy - radius * 0.18,
            cx + radius * 0.58,
            cy + radius * 0.18,
            fill=alpha_blend(color, "#070b12", 0.2),
            outline="",
        )
        canvas.create_text(
            cx,
            cy - radius * 0.28,
            text=center_value,
            fill=center_color,
            font=("Segoe UI", 26, "bold"),
        )
        canvas.create_text(
            cx,
            cy - radius * 0.08,
            text=title.upper(),
            fill=COLORS["text_muted"],
            font=("Segoe UI", 9, "bold"),
        )
    def _update_monitor(self):
        """Coleta métricas fora da thread gráfica e publica snapshots."""
        while self.monitor_running and not self.monitor_stop_event.is_set():
            try:
                metrics = self._collect_monitor_metrics()
                if not self.monitor_stop_event.is_set():
                    self.logger.run_on_ui(
                        lambda values=metrics: self._display_monitor_metrics(values)
                    )

            except Exception as e:
                error = str(e)
                self.logger.log_error(f"Erro ao coletar métricas do sistema: {error}")
                if not self.monitor_stop_event.is_set():
                    self.logger.run_on_ui(
                        lambda message=error: self._display_monitor_error(message)
                    )

            self.monitor_stop_event.wait(1.5)

    def start_monitor(self):
        if self.monitor_thread and self.monitor_thread.is_alive():
            if self.monitor_running:
                return
            self.monitor_thread.join(timeout=2)
            if self.monitor_thread.is_alive():
                self.logger.log_warning(
                    "A coleta anterior ainda está finalizando; aguarde antes de reabrir o monitor."
                )
                return

        self.monitor_running = True
        self.monitor_stop_event.clear()
        psutil.cpu_percent(interval=None)
        self.monitor_thread = threading.Thread(
            target=self._update_monitor, name="ScriptNiveMonitor", daemon=True
        )
        self.monitor_thread.start()

    def stop_monitor(self):
        self.monitor_running = False
        self.monitor_stop_event.set()
        if self.monitor_thread and self.monitor_thread is not threading.current_thread():
            self.monitor_thread.join(timeout=2)
            if self.monitor_thread.is_alive():
                self.logger.log_warning(
                    "A thread de monitoramento excedeu o prazo de encerramento."
                )

    def _collect_monitor_metrics(self):
        cpu_percent = psutil.cpu_percent(interval=0.5)
        try:
            frequency = psutil.cpu_freq()
        except (OSError, NotImplementedError):
            frequency = None
        memory = psutil.virtual_memory()
        now = time.monotonic()

        previous_time = self._disk_io_sample_time
        previous_io = self._disk_io_previous
        disk_io_error = None
        try:
            current_io = psutil.disk_io_counters(perdisk=True)
        except (OSError, NotImplementedError) as error:
            current_io = None
            disk_io_error = str(error)
        disk_rates = {}
        if current_io:
            elapsed = now - previous_time if previous_time is not None else None
            for device, counters in current_io.items():
                old = previous_io.get(device)
                if old and elapsed and elapsed > 0:
                    disk_rates[device] = (
                        max(0, counters.read_bytes - old[0]) / elapsed,
                        max(0, counters.write_bytes - old[1]) / elapsed,
                    )
                else:
                    disk_rates[device] = None
            self._disk_io_previous = {
                device: (counters.read_bytes, counters.write_bytes)
                for device, counters in current_io.items()
            }
            self._disk_io_sample_time = now

        volumes = []
        try:
            partitions = psutil.disk_partitions(all=False)
            partition_error = None
        except (OSError, NotImplementedError) as error:
            partitions = []
            partition_error = str(error)

        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
            except OSError as error:
                volumes.append(
                    {
                        "device": partition.device or partition.mountpoint,
                        "mountpoint": partition.mountpoint,
                        "filesystem": partition.fstype or "N/D",
                        "error": str(error),
                    }
                )
                continue
            volumes.append(
                {
                    "device": partition.device or partition.mountpoint,
                    "mountpoint": partition.mountpoint,
                    "filesystem": partition.fstype or "N/D",
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent,
                }
            )

        return {
            "cpu_percent": cpu_percent,
            "cpu_frequency_mhz": (
                frequency.current
                if frequency and frequency.current and frequency.current > 0
                else None
            ),
            "cpu_physical_cores": psutil.cpu_count(logical=False),
            "cpu_logical_processors": psutil.cpu_count(logical=True),
            "memory_total": memory.total,
            "memory_used": memory.used,
            "memory_available": memory.available,
            "memory_percent": memory.percent,
            "volumes": volumes,
            "partition_error": partition_error,
            "disk_rates": disk_rates,
            "disk_io_error": disk_io_error,
            "gpu": self._get_gpu_info(),
        }

    def _display_monitor_metrics(self, metrics):
        if not self.monitor_running:
            return
        cpu_percent = metrics["cpu_percent"]
        ram_percent = metrics["memory_percent"]
        gpu_percent = metrics["gpu"].get("percent")
        disk_percent = self._max_volume_percent(metrics["volumes"])
        self.cpu_history.append(cpu_percent)
        self.ram_history.append(ram_percent)
        if gpu_percent is not None:
            self.gpu_history.append(gpu_percent)
        if disk_percent is not None:
            self.disk_history.append(disk_percent)

        self._update_metric_card(
            self.cpu_label,
            cpu_percent,
            (
                f"Utilização medida: {cpu_percent:.1f}%\n"
                f"Frequência atual: {self._format_frequency(metrics['cpu_frequency_mhz'])}  |  "
                f"Núcleos: {self._format_count(metrics['cpu_physical_cores'])} físicos  |  "
                f"Processadores lógicos: {self._format_count(metrics['cpu_logical_processors'])}\n"
                "Temperatura: não suportada pela API disponível  |  "
                "Consumo elétrico: não disponível (nenhum sensor compatível)"
            ),
            color=self._get_usage_color(cpu_percent),
        )
        self._update_metric_card(
            self.ram_label,
            ram_percent,
            (
                f"Utilização medida: {ram_percent:.1f}%  |  "
                f"Total: {self._format_bytes(metrics['memory_total'])}  |  "
                f"Em uso: {self._format_bytes(metrics['memory_used'])}  |  "
                f"Disponível: {self._format_bytes(metrics['memory_available'])}"
            ),
            color=self._get_usage_color(ram_percent),
        )
        self._update_metric_card(
            self.gpu_label,
            gpu_percent,
            metrics["gpu"]["text"],
            color=self._get_usage_color(gpu_percent) if gpu_percent is not None else "#5fa2ff",
            status="sensor ativo" if gpu_percent is not None else "sem leitura",
        )
        self._update_metric_card(
            self.disk_label,
            disk_percent,
            self._format_disk_metrics(metrics),
            color=self._get_usage_color(disk_percent) if disk_percent is not None else COLORS["warning"],
            status="volumes ativos" if disk_percent is not None else "sem volumes",
        )
        self.monitor_updated_label.configure(
            text=f"Última amostra: {datetime.now().strftime('%H:%M:%S')}",
            text_color=COLORS["text_muted"],
        )

    def _display_monitor_error(self, error):
        if not self.monitor_running:
            return
        message = f"Falha na coleta: {error}"
        for card in (self.cpu_label, self.ram_label, self.gpu_label, self.disk_label):
            self._update_metric_card(card, None, message, color=COLORS["danger"], status="erro")
        self.monitor_updated_label.configure(
            text="Amostra indisponível — consulte o log para detalhes.",
            text_color=COLORS["danger"],
        )

    @staticmethod
    def _format_bytes(value):
        return f"{value / (1024**3):.1f} GB"

    @staticmethod
    def _format_frequency(value):
        return f"{value:.0f} MHz (medida)" if value is not None else "indisponível"

    @staticmethod
    def _format_count(value):
        return str(value) if value is not None else "indisponível"

    @staticmethod
    def _format_rate(value):
        if value is None:
            return "aguardando segunda amostra"
        units = ("B/s", "KB/s", "MB/s", "GB/s")
        rate = float(value)
        unit = units[0]
        for unit in units:
            if rate < 1024 or unit == units[-1]:
                break
            rate /= 1024
        return f"{rate:.1f} {unit}"

    def _format_disk_metrics(self, metrics):
        lines = []
        if metrics["partition_error"]:
            lines.append(
                f"Não foi possível enumerar volumes: {metrics['partition_error']}"
            )
        for volume in metrics["volumes"]:
            if "error" in volume:
                lines.append(
                    f"{volume['device']} ({volume['mountpoint']}): "
                    f"não foi possível obter espaço — {volume['error']}"
                )
                continue
            lines.append(
                f"{volume['device']} [{volume['filesystem']}] — "
                f"em uso {self._format_bytes(volume['used'])} "
                f"({volume['percent']:.1f}%), disponível "
                f"{self._format_bytes(volume['free'])}, total "
                f"{self._format_bytes(volume['total'])}"
            )

        if not lines:
            lines.append("Volumes: não foi possível obter informações.")

        if metrics["disk_io_error"]:
            lines.append(
                f"Não foi possível obter contadores de I/O: {metrics['disk_io_error']}"
            )
        elif metrics["disk_rates"]:
            for device, rates in metrics["disk_rates"].items():
                if rates is None:
                    lines.append(f"{device} — aguardando segunda amostra de I/O.")
                else:
                    lines.append(
                        f"{device} — leitura {self._format_rate(rates[0])}  |  "
                        f"gravação {self._format_rate(rates[1])}"
                    )
        elif not metrics["disk_io_error"]:
            lines.append("Atividade de disco: contadores de I/O indisponíveis.")

        lines.append(
            "Temperatura e SMART/saúde: não suportados pelas APIs instaladas."
        )
        return "\n".join(lines)

    @staticmethod
    def _max_volume_percent(volumes):
        percentages = [
            float(volume["percent"])
            for volume in volumes
            if "percent" in volume and volume["percent"] is not None
        ]
        if not percentages:
            return None
        return max(percentages)

    def _get_usage_color(self, percent):
        """Retorna cor baseada no uso"""
        if percent < 50:
            return COLORS["success"]
        elif percent < 80:
            return COLORS["warning"]
        else:
            return COLORS["danger"]

    def _get_gpu_info(self):
        fields = (
            "name",
            "utilization.gpu",
            "memory.used",
            "memory.total",
            "temperature.gpu",
            "power.draw",
            "power.limit",
            "clocks.gr",
        )
        try:
            nvidia_smi = shutil.which("nvidia-smi")
            if nvidia_smi is None:
                nvidia_smi = str(
                    Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
                    / "NVIDIA Corporation"
                    / "NVSMI"
                    / "nvidia-smi.exe"
                )
                if not os.path.isfile(nvidia_smi):
                    return {
                        "text": (
                            "Modelo e sensores: fonte NVIDIA indisponível "
                            "(nvidia-smi não encontrado)."
                        )
                    }

            result = subprocess.run(
                [
                    nvidia_smi,
                    f"--query-gpu={','.join(fields)}",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=1.5,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            if result.returncode != 0:
                details = result.stderr.strip() or "sem detalhes"
                self.logger.log_warning(
                    f"nvidia-smi não conseguiu ler os sensores: {details}"
                )
                return {"text": f"Não foi possível obter os sensores NVIDIA: {details}"}

            rows = list(csv.reader(io.StringIO(result.stdout.strip())))
            if not rows:
                return {"text": "nvidia-smi não retornou placas ou leituras.", "percent": None}

            gpu_lines = []
            gpu_percentages = []
            for row in rows:
                values = [value.strip() for value in row]
                if len(values) != len(fields):
                    self.logger.log_warning(
                        "Resposta de nvidia-smi incompatível com os campos solicitados."
                    )
                    return {"text": "Não foi possível interpretar a resposta de nvidia-smi.", "percent": None}
                (
                    name,
                    utilization,
                    memory_used,
                    memory_total,
                    temperature,
                    power,
                    power_limit,
                    clock,
                ) = values
                utilization_value = self._gpu_numeric(utilization)
                if utilization_value is not None:
                    gpu_percentages.append(utilization_value)
                gpu_lines.append(
                    f"{name}: utilização {self._gpu_value(utilization, '%')}; "
                    f"VRAM {self._gpu_value(memory_used, ' MiB')} / "
                    f"{self._gpu_value(memory_total, ' MiB')}; "
                    f"temperatura {self._gpu_value(temperature, ' °C')}; "
                    f"potência {self._gpu_value(power, ' W')} "
                    f"(limite {self._gpu_value(power_limit, ' W')}); "
                    f"frequência {self._gpu_value(clock, ' MHz')}"
                )
            return {
                "text": "\n".join(gpu_lines),
                "percent": max(gpu_percentages) if gpu_percentages else None,
            }
        except subprocess.TimeoutExpired:
            self.logger.log_warning("Timeout ao consultar sensores NVIDIA.")
            return {"text": "Não foi possível obter os sensores NVIDIA (timeout)."}
        except OSError as error:
            self.logger.log_warning(f"Não foi possível consultar sensores NVIDIA: {error}")
            return {"text": f"Não foi possível obter sensores NVIDIA: {error}"}

    @staticmethod
    def _gpu_value(value, unit):
        normalized = value.strip().lower()
        if normalized in {"n/a", "[n/a]", "not supported", "[not supported]"}:
            return "não suportado"
        if normalized in {"", "unknown", "[unknown]"}:
            return "indisponível"
        try:
            numeric_value = float(normalized)
        except ValueError:
            return "indisponível"
        if not math.isfinite(numeric_value):
            return "indisponível"
        return f"{value}{unit}"

    @staticmethod
    def _gpu_numeric(value):
        normalized = value.strip().lower()
        if normalized in {"n/a", "[n/a]", "not supported", "[not supported]", "", "unknown", "[unknown]"}:
            return None
        try:
            numeric_value = float(normalized)
        except ValueError:
            return None
        if not math.isfinite(numeric_value):
            return None
        return max(0.0, min(100.0, numeric_value))

    def _section(self, parent, text):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=16, pady=(18, 4))
        ctk.CTkLabel(
            f,
            text=text,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left")
        ctk.CTkFrame(
            f,
            height=2,
            fg_color=alpha_blend(COLORS["accent"], COLORS["content_bg"], 0.25),
            corner_radius=1,
        ).pack(side="left", fill="x", expand=True, padx=(10, 0), pady=10)

    def open_control_panel(self):
        subprocess.Popen("control.exe")
        self.logger.log_info("Painel de Controle aberto")
        self.parent.update_status("Painel de Controle aberto")

    def open_task_manager(self):
        subprocess.Popen("taskmgr.exe")
        self.logger.log_info("Gerenciador de Tarefas aberto")
        self.parent.update_status("Gerenciador de Tarefas aberto")

    def start_mrt(self):
        try:
            subprocess.Popen(self.config.get_command("mrt"), shell=True)
            self.logger.log_success("MRT iniciado com sucesso")
            self.parent.update_status("MRT iniciado")
        except Exception as e:
            self.logger.log_error(f"Erro ao iniciar MRT: {e}")
            messagebox.showerror("Erro", f"Erro ao iniciar MRT:\n{e}")

    def delete_corrupted_folders(self):
        path = filedialog.askdirectory(title="Selecione a pasta corrompida")
        if path and messagebox.askyesno(
            "Confirmar",
            f"Deletar permanentemente:\n{path}\n\nEsta ação não pode ser desfeita!",
        ):
            def show_success(_result):
                messagebox.showinfo("Sucesso", "Pasta deletada com sucesso!")

            def show_error(_error):
                messagebox.showwarning(
                    "Aviso", "A pasta pode ainda existir.\nTente em modo seguro."
                )

            self.system_commands.delete_corrupted_folder_async(
                path, show_success, show_error
            )
