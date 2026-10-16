"""
gui/widgets.py - Widgets reutilizáveis com ícones Font Awesome

CTkButton só aceita uma fonte por vez, então IconButton usa um CTkFrame
com dois CTkLabels internos (ícone FA + texto normal) para misturar fontes.
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
    "card_bg": "#252537",
    "card_hover": "#2e2e45",
    "text_primary": "#e2e8f0",
    "text_muted": "#8892a4",
}


def icon_label(
    parent, icon_name: str, size: int = 16, color: str = "#e2e8f0", **kwargs
) -> ctk.CTkLabel:
    """CTkLabel simples com um ícone Font Awesome."""
    return ctk.CTkLabel(
        parent,
        text=ic.get(icon_name),
        font=ctk.CTkFont(
            family=ic.family(icon_name), size=size, weight=ic.weight(icon_name)
        ),
        text_color=color,
        **kwargs,
    )


class IconButton(ctk.CTkFrame):
    """
    Frame que se comporta como botão, com ícone FA + texto lado a lado.

    Parâmetros:
        parent        – widget pai
        icon_name     – chave em utils/icons.py (ex: "trash")
        text          – rótulo do botão
        command       – função chamada no clique
        fg_color      – cor de fundo normal
        hover_color   – cor de fundo no hover
        icon_color    – cor do ícone (padrão = text_color)
        text_color    – cor do texto
        icon_size     – tamanho do ícone em pt
        font_size     – tamanho do texto em pt
        height        – altura do botão em px
        corner_radius – raio dos cantos
        border_width  – espessura da borda
        border_color  – cor da borda
        icon_side     – "left" ou "right"
        expand        – se True, preenche horizontalmente
    """

    def __init__(
        self,
        parent,
        icon_name: str,
        text: str,
        command=None,
        fg_color: str = "#252537",
        hover_color: str = "#2e2e45",
        icon_color: str | None = None,
        text_color: str = "#e2e8f0",
        icon_size: int = 14,
        font_size: int = 12,
        height: int = 36,
        corner_radius: int = 8,
        border_width: int = 0,
        border_color: str = "#3d3d5c",
        icon_side: str = "left",
        anchor: str = "center",
        **kwargs,
    ):
        super().__init__(
            parent,
            fg_color=fg_color,
            corner_radius=corner_radius,
            border_width=border_width,
            border_color=border_color,
            height=height,
            **kwargs,
        )
        self._fg = fg_color
        self._hover = hover_color
        self._command = command
        self._height = height

        self.pack_propagate(False)
        self.grid_propagate(False)

        _icon_color = icon_color if icon_color else text_color

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.place(relx=0.5, rely=0.5, anchor="center")

        ico = ctk.CTkLabel(
            inner,
            text=ic.get(icon_name),
            font=ctk.CTkFont(
                family=ic.family(icon_name), size=icon_size, weight=ic.weight(icon_name)
            ),
            text_color=_icon_color,
        )
        lbl = ctk.CTkLabel(
            inner,
            text=f"  {text}" if icon_side == "left" else f"{text}  ",
            font=ctk.CTkFont(size=font_size),
            text_color=text_color,
        )

        if icon_side == "left":
            ico.pack(side="left")
            lbl.pack(side="left")
        else:
            lbl.pack(side="left")
            ico.pack(side="left")

        # Hover & clique em todos os widgets filhos
        for w in (self, inner, ico, lbl):
            w.bind("<Enter>", self._on_enter)
            w.bind("<Leave>", self._on_leave)
            w.bind("<Button-1>", self._on_click)

    def _on_enter(self, _e=None):
        self.configure(fg_color=self._hover)

    def _on_leave(self, _e=None):
        self.configure(fg_color=self._fg)

    def _on_click(self, _e=None):
        if self._command:
            self._command()

    def configure(self, **kwargs):
        # repassa fg_color para atualizar estado interno
        if "fg_color" in kwargs:
            self._fg = kwargs["fg_color"]
        super().configure(**kwargs)
