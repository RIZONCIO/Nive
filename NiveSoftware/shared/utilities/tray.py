"""
tray_icon.py - Gerencia ícone de bandeja para ScriptNive
"""

import threading
import pystray
from PIL import Image, ImageDraw


class TrayIconManager:
    """Gerencia o ícone de bandeja e as ações de restaurar / sair."""

    def __init__(self, root, restore_callback, exit_callback, dispatch):
        self.root = root
        self.restore_callback = restore_callback
        self.exit_callback = exit_callback
        self.dispatch = dispatch
        self.icon = pystray.Icon(
            "scriptnive",
            self._create_image(),
            "ScriptNive",
            menu=pystray.Menu(
                pystray.MenuItem("Abrir ScriptNive", self._on_restore),
                pystray.MenuItem("Sair", self._on_exit),
            ),
        )
        self._thread = None

    def _create_image(self):
        image = Image.new("RGBA", (64, 64), (30, 30, 46, 255))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 64, 64), fill=(40, 45, 70, 255))
        draw.text((18, 14), "N", fill=(79, 156, 249, 255))
        draw.text((16, 28), "V", fill=(255, 255, 255, 255))
        return image

    def _on_restore(self, icon, item):
        if self.restore_callback:
            self.dispatch(self.restore_callback)

    def _on_exit(self, icon, item):
        if self.exit_callback:
            self.dispatch(self.exit_callback)

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self.icon.run, daemon=True)
        self._thread.start()

    def stop(self):
        try:
            self.icon.stop()
        except Exception:
            pass
        self._thread = None
