"""
utils/icons.py - Carregamento do Font Awesome 6 Free e mapa de ícones

Coloque os TTFs em:  <raiz_do_projeto>/assets/font/
  fa-solid-900.ttf
  fa-regular-400.ttf
  fa-brands-400.ttf

Download gratuito: https://fontawesome.com/download  →  "Free For Desktop"
"""

import sys
import ctypes
from pathlib import Path

# ── Localização dos arquivos ──────────────────────────────────────────────────
def _find_fonts_dir() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        cand = parent / "assets" / "font"
        if cand.exists():
            return cand
        cand = parent / "assets" / "fonts"
        if cand.exists():
            return cand
    return current.parents[2] / "assets" / "font"

_FONTS_DIR = _find_fonts_dir()
_FA_SOLID = _FONTS_DIR / "fa-solid-900.ttf"
_FA_REGULAR = _FONTS_DIR / "fa-regular-400.ttf"
_FA_BRANDS = _FONTS_DIR / "fa-brands-400.ttf"

# ── Nomes das famílias (após carregamento no GDI do Windows) ─────────────────
FA_SOLID = "Font Awesome 6 Free"  # weight="bold"   (900)
FA_REGULAR = "Font Awesome 6 Free"  # weight="normal" (400)
FA_BRANDS = "Font Awesome 6 Brands"  # weight="normal"

_FR_PRIVATE = 0x10  # carrega só no processo, sem afetar o sistema
_fonts_loaded = False


def _load(path: Path) -> bool:
    if not path.exists():
        print(f"[icons] Fonte não encontrada: {path}")
        return False
    if sys.platform == "win32":
        ok = bool(ctypes.windll.gdi32.AddFontResourceExW(str(path), _FR_PRIVATE, 0))
        if not ok:
            print(f"[icons] Falha ao carregar: {path.name}")
        else:
            print(f"[icons] Fonte carregada: {path.name}")
        return ok
    return False  # Linux/macOS: instale as fontes no sistema manualmente


def load_all() -> bool:
    """
    Carrega as três variantes do Font Awesome Free no GDI do Windows.
    Chame uma vez no início da aplicação (ex: run.py ou BaseInterface.__init__).
    Retorna True se ao menos a variante Solid foi carregada.
    """
    global _fonts_loaded
    if _fonts_loaded:
        return True

    print(f"[icons] Buscando fontes em: {_FONTS_DIR}")
    ok = _load(_FA_SOLID)
    _load(_FA_REGULAR)
    _load(_FA_BRANDS)
    _fonts_loaded = ok

    if not ok:
        print(
            "[icons] AVISO: Font Awesome Solid não carregado.\n"
            f"        Verifique se os arquivos .ttf existem em:\n"
            f"        {_FONTS_DIR}"
        )
    return ok


# ── Mapa semântico → (unicode_char, família, weight) ─────────────────────────
#
# Para obter o codepoint de qualquer ícone:
#   https://fontawesome.com/icons  →  selecione "Solid" → veja o código Unicode
#
_ICONS: dict[str, tuple[str, str, str]] = {
    # ── Sidebar / Navegação ──────────────────────────────────────────────────
    "home": ("\uf015", FA_SOLID, "bold"),  # fa-house
    "network": ("\uf6ff", FA_SOLID, "bold"),  # fa-network-wired
    "bolt": ("\uf0e7", FA_SOLID, "bold"),  # fa-bolt
    "tools": ("\uf7d9", FA_SOLID, "bold"),  # fa-screwdriver-wrench
    "info": ("\uf05a", FA_SOLID, "bold"),  # fa-circle-info
    "logo": ("\uf6e3", FA_SOLID, "bold"),  # fa-hammer
    # ── Manutenção geral ─────────────────────────────────────────────────────
    "trash": ("\uf1f8", FA_SOLID, "bold"),  # fa-trash
    "hdd": ("\uf0a0", FA_SOLID, "bold"),  # fa-hard-drive
    "microchip": ("\uf2db", FA_SOLID, "bold"),  # fa-microchip
    "wrench": ("\uf0ad", FA_SOLID, "bold"),  # fa-wrench
    "broom": ("\uf51a", FA_SOLID, "bold"),  # fa-broom
    "shield": ("\uf3ed", FA_SOLID, "bold"),  # fa-shield-halved
    "box": ("\uf187", FA_SOLID, "bold"),  # fa-box-archive
    "volume": ("\uf028", FA_SOLID, "bold"),  # fa-volume-high
    "download": ("\uf019", FA_SOLID, "bold"),  # fa-download
    "folder": ("\uf07c", FA_SOLID, "bold"),  # fa-folder-open
    "medkit": ("\uf479", FA_SOLID, "bold"),  # fa-kit-medical
    "sliders": ("\uf1de", FA_SOLID, "bold"),  # fa-sliders
    "task_manager": ("\uf080", FA_SOLID, "bold"),  # fa-chart-bar
    # ── Monitoramento de hardware ────────────────────────────────────────────
    "cpu": ("\uf2db", FA_SOLID, "bold"),  # fa-microchip
    "gpu": ("\uf108", FA_SOLID, "bold"),  # fa-desktop
    "memory": ("\uf538", FA_SOLID, "bold"),  # fa-memory
    "disk": ("\uf0a0", FA_SOLID, "bold"),  # fa-hard-drive
    # ── Rede ─────────────────────────────────────────────────────────────────
    "rotate": ("\uf2f1", FA_SOLID, "bold"),  # fa-rotate
    "bomb": ("\uf1e2", FA_SOLID, "bold"),  # fa-bomb
    "globe": ("\uf0ac", FA_SOLID, "bold"),  # fa-globe
    "wifi": ("\uf1eb", FA_SOLID, "bold"),  # fa-wifi
    "map": ("\uf279", FA_SOLID, "bold"),  # fa-map
    "chart_line": ("\uf201", FA_SOLID, "bold"),  # fa-chart-line
    "search": ("\uf002", FA_SOLID, "bold"),  # fa-magnifying-glass
    "plug": ("\uf1e6", FA_SOLID, "bold"),  # fa-plug
    # ── Ferramentas / Log ─────────────────────────────────────────────────────
    "clipboard": ("\uf46d", FA_SOLID, "bold"),  # fa-clipboard-list
    "desktop": ("\uf108", FA_SOLID, "bold"),  # fa-desktop
    "save": ("\uf0c7", FA_SOLID, "bold"),  # fa-floppy-disk
    # ── Otimização ────────────────────────────────────────────────────────────
    "calendar": ("\uf073", FA_SOLID, "bold"),  # fa-calendar
    "user_secret": ("\uf21b", FA_SOLID, "bold"),  # fa-user-secret
    "paintbrush": ("\uf1fc", FA_SOLID, "bold"),  # fa-paintbrush
    "lock": ("\uf023", FA_SOLID, "bold"),  # fa-lock
    # ── Sobre / Links ─────────────────────────────────────────────────────────
    "file_pdf": ("\uf1c1", FA_SOLID, "bold"),  # fa-file-pdf
    "book": ("\uf02d", FA_SOLID, "bold"),  # fa-book
    "lightbulb": ("\uf0eb", FA_SOLID, "bold"),  # fa-lightbulb
    "github": ("\uf09b", FA_BRANDS, "normal"),  # fa-github (brands)
    # ── Genéricos ─────────────────────────────────────────────────────────────
    "check": ("\uf058", FA_SOLID, "bold"),  # fa-circle-check
    "times": ("\uf057", FA_SOLID, "bold"),  # fa-circle-xmark
    "circle": ("\uf111", FA_SOLID, "bold"),  # fa-circle
    "gear": ("\uf013", FA_SOLID, "bold"),  # fa-gear
    "power": ("\uf011", FA_SOLID, "bold"),  # fa-power-off
    "refresh": ("\uf021", FA_SOLID, "bold"),  # fa-arrows-rotate
    "close": ("\uf00d", FA_SOLID, "bold"),  # fa-xmark
    "question": ("\uf128", FA_SOLID, "bold"),  # fa-question (fallback)
}


def get(name: str) -> str:
    """Retorna o caractere Unicode do ícone (fallback: '?')."""
    entry = _ICONS.get(name)
    return entry[0] if entry else _ICONS["question"][0]


def family(name: str) -> str:
    """Retorna a família da fonte para o ícone."""
    entry = _ICONS.get(name, _ICONS["question"])
    return entry[1]


def weight(name: str) -> str:
    """Retorna o weight ('bold' ou 'normal') para o ícone."""
    entry = _ICONS.get(name, _ICONS["question"])
    return entry[2]


def font_tuple(name: str, size: int = 16) -> tuple:
    """Retorna (family, size, weight) para uso direto no tkinter clássico."""
    e = _ICONS.get(name, _ICONS["question"])
    return (e[1], size, e[2])
