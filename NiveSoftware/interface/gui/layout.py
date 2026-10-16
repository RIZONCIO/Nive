"""
layout.py - Interface base modernizada do ScriptNive
Layout: sidebar escura + área de conteúdo com cards (customtkinter)
Ícones: Font Awesome 6 Free via utils/icons.py
"""

import customtkinter as ctk
try:
    from shared.utilities import icons as ic
except ImportError:
    try:
        from NiveSoftware.shared.utilities import icons as ic
    except ImportError:
        from utils import icons as ic

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLORS = {
    "sidebar_bg": "#1a1a2e",
    "sidebar_hover": "#16213e",
    "sidebar_active": "#0f3460",
    "accent": "#4f9cf9",
    "accent2": "#7b61ff",
    "header_bg": "#0f3460",
    "content_bg": "#1e1e2e",
    "card_bg": "#252537",
    "card_hover": "#2e2e45",
    "text_primary": "#e2e8f0",
    "text_muted": "#8892a4",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "info": "#3b82f6",
}

# (icon_key, label, page_key)
NAV_ITEMS = [
    ("home", "Principal", "main"),
    ("chart_line", "Monitoramento", "monitoring"),
    ("network", "Rede", "network"),
    ("bolt", "Otimização", "optimization"),
    ("tools", "Ferramentas", "tools"),
    ("info", "Sobre", "info"),
]


class _NavButton(ctk.CTkFrame):
    """
    Botão de navegação da sidebar com ícone FA + texto.
    Usa dois CTkLabels para misturar fontes.
    """

    def __init__(self, parent, icon_key: str, label: str, command, **kwargs):
        super().__init__(
            parent,
            fg_color="transparent",
            corner_radius=8,
            height=42,
            **kwargs,
        )
        self.pack_propagate(False)
        self._command = command
        self._active = False

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.place(x=14, rely=0.5, anchor="w")

        self._icon_lbl = ctk.CTkLabel(
            inner,
            text=ic.get(icon_key),
            font=ctk.CTkFont(
                family=ic.family(icon_key), size=15, weight=ic.weight(icon_key)
            ),
            text_color=COLORS["text_primary"],
            width=22,
        )
        self._icon_lbl.pack(side="left")

        self._text_lbl = ctk.CTkLabel(
            inner,
            text=f"  {label}",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_primary"],
        )
        self._text_lbl.pack(side="left")

        for w in (self, inner, self._icon_lbl, self._text_lbl):
            w.bind("<Enter>", self._on_enter)
            w.bind("<Leave>", self._on_leave)
            w.bind("<Button-1>", self._on_click)

    def set_active(self, active: bool):
        self._active = active
        color = COLORS["sidebar_active"] if active else "transparent"
        text_color = COLORS["accent"] if active else COLORS["text_primary"]
        fw = "bold" if active else "normal"

        self.configure(fg_color=color)
        self._icon_lbl.configure(text_color=text_color)
        self._text_lbl.configure(
            text_color=text_color,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight=fw),
        )

    def _on_enter(self, _e=None):
        if not self._active:
            self.configure(fg_color=COLORS["sidebar_hover"])

    def _on_leave(self, _e=None):
        if not self._active:
            self.configure(fg_color="transparent")

    def _on_click(self, _e=None):
        self._command()


class BaseInterface:
    """Interface base: sidebar + header + content area + status bar."""

    def __init__(self, root, system_commands, logger, config):
        self.root = root
        self.system_commands = system_commands
        self.logger = logger
        self.config = config

        self._active_page = "main"
        self._nav_buttons = {}  # page_key → _NavButton
        self._content_frames = {}  # page_key → CTkFrame

        self.status_var = ctk.StringVar(value="Pronto")

        self.reinstall_software_placeholder = lambda: None
        self.complete_repair_placeholder = lambda: None

    # ── Setup principal ───────────────────────────────────────────────────────

    def setup_base_widgets(self):
        self.root.configure(fg_color=COLORS["content_bg"])

        self._main_frame = ctk.CTkFrame(
            self.root, fg_color="transparent", corner_radius=0
        )
        self._main_frame.pack(fill="both", expand=True)
        self._main_frame.columnconfigure(1, weight=1)
        self._main_frame.rowconfigure(0, weight=1)

        self._build_sidebar()

        right_col = ctk.CTkFrame(
            self._main_frame, fg_color="transparent", corner_radius=0
        )
        right_col.grid(row=0, column=1, sticky="nsew")
        right_col.rowconfigure(1, weight=1)
        right_col.columnconfigure(0, weight=1)

        self._build_header(right_col)
        self._build_content_area(right_col)
        self._build_status_bar(right_col)

        return self._main_frame

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(
            self._main_frame,
            width=210,
            fg_color=COLORS["sidebar_bg"],
            corner_radius=0,
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.pack_propagate(False)
        sidebar.grid_propagate(False)

        # ── Logo ─────────────────────────────────────────────────────────────
        logo_frame = ctk.CTkFrame(
            sidebar,
            fg_color=COLORS["sidebar_active"],
            corner_radius=0,
            height=68,
        )
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)

        logo_inner = ctk.CTkFrame(logo_frame, fg_color="transparent")
        logo_inner.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            logo_inner,
            text=ic.get("logo"),
            font=ctk.CTkFont(
                family=ic.family("logo"), size=22, weight=ic.weight("logo")
            ),
            text_color=COLORS["accent"],
        ).pack(side="left")

        ctk.CTkLabel(
            logo_inner,
            text="  ScriptNive",
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            text_color=COLORS["accent"],
        ).pack(side="left")

        # Versão
        ctk.CTkLabel(
            sidebar,
            text=f"v{getattr(self.config, 'version', '2.0')}",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"],
        ).pack(pady=(6, 14))

        # Linha separadora
        ctk.CTkFrame(sidebar, height=1, fg_color="#2d2d44", corner_radius=0).pack(
            fill="x", padx=12, pady=(0, 10)
        )

        # ── Botões de navegação ───────────────────────────────────────────────
        nav_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", padx=10)

        for icon_key, label, page_key in NAV_ITEMS:
            btn = _NavButton(
                nav_frame,
                icon_key=icon_key,
                label=label,
                command=lambda k=page_key: self.navigate_to(k),
            )
            btn.pack(fill="x", pady=2)
            self._nav_buttons[page_key] = btn

        # ── Rodapé ────────────────────────────────────────────────────────────
        footer = ctk.CTkFrame(sidebar, fg_color="transparent")
        footer.pack(side="bottom", fill="x", pady=14, padx=14)

        ctk.CTkFrame(footer, height=1, fg_color="#2d2d44", corner_radius=0).pack(
            fill="x", pady=(0, 10)
        )

        ctk.CTkLabel(
            footer,
            text="by Ryan Vinicius",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_muted"],
        ).pack()

    # ── Header ────────────────────────────────────────────────────────────────

    def _build_header(self, parent):
        self._header_frame = ctk.CTkFrame(
            parent,
            height=72,
            fg_color=COLORS["header_bg"],
            corner_radius=0,
        )
        self._header_frame.grid(row=0, column=0, sticky="ew")
        self._header_frame.pack_propagate(False)

        header_inner = ctk.CTkFrame(self._header_frame, fg_color="transparent")
        header_inner.place(x=24, rely=0.5, anchor="w")

        self._header_icon = ctk.CTkLabel(
            header_inner,
            text=ic.get("home"),
            font=ctk.CTkFont(
                family=ic.family("home"), size=20, weight=ic.weight("home")
            ),
            text_color=COLORS["accent"],
        )
        self._header_icon.pack(side="left")

        title_block = ctk.CTkFrame(header_inner, fg_color="transparent")
        title_block.pack(side="left", padx=(12, 0))

        self._header_title = ctk.CTkLabel(
            title_block,
            text="Principal",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLORS["text_primary"],
        )
        self._header_title.pack(anchor="w")

        self._header_sub = ctk.CTkLabel(
            title_block,
            text="Ferramentas mais usadas do Windows",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"],
        )
        self._header_sub.pack(anchor="w")

    def set_header(self, icon_key: str, title: str, subtitle: str = ""):
        self._header_icon.configure(
            text=ic.get(icon_key),
            font=ctk.CTkFont(
                family=ic.family(icon_key), size=20, weight=ic.weight(icon_key)
            ),
        )
        self._header_title.configure(text=title)
        self._header_sub.configure(text=subtitle)

    # ── Content area ──────────────────────────────────────────────────────────

    def _build_content_area(self, parent):
        self._content_area = ctk.CTkFrame(
            parent,
            fg_color=COLORS["content_bg"],
            corner_radius=0,
        )
        self._content_area.grid(row=1, column=0, sticky="nsew")

    def register_page(self, key: str, frame: ctk.CTkFrame):
        self._content_frames[key] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_remove()

    def navigate_to(self, page_key: str):
        for frame in self._content_frames.values():
            frame.grid_remove()
        if page_key in self._content_frames:
            self._content_frames[page_key].grid()
        for key, btn in self._nav_buttons.items():
            btn.set_active(key == page_key)
        self._active_page = page_key

    # ── Status bar ────────────────────────────────────────────────────────────

    def _build_status_bar(self, parent):
        status_bar = ctk.CTkFrame(
            parent,
            height=28,
            fg_color=COLORS["sidebar_bg"],
            corner_radius=0,
        )
        status_bar.grid(row=2, column=0, sticky="ew")
        status_bar.pack_propagate(False)

        status_inner = ctk.CTkFrame(status_bar, fg_color="transparent")
        status_inner.place(x=14, rely=0.5, anchor="w")

        ctk.CTkLabel(
            status_inner,
            text=ic.get("circle"),
            font=ctk.CTkFont(
                family=ic.family("circle"), size=8, weight=ic.weight("circle")
            ),
            text_color=COLORS["success"],
        ).pack(side="left")

        ctk.CTkLabel(
            status_inner,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"],
        ).pack(side="left", padx=(6, 0))

    # ── Helpers públicos ──────────────────────────────────────────────────────

    def update_status(self, message: str):
        self.status_var.set(message)

    def log_activity(self, message: str):
        if self.logger:
            self.logger.log(message)

    def get_content_area(self) -> ctk.CTkFrame:
        self._content_area.columnconfigure(0, weight=1)
        self._content_area.rowconfigure(0, weight=1)
        return self._content_area

    @property
    def notebook(self):
        return self._content_area

    @property
    def progress(self):
        return None
