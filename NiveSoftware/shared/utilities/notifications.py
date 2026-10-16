"""
notifications.py - Módulo para notificações nativas do Windows
"""

import platform
from win10toast import ToastNotifier


class Notifications:
    """Gerenciador de notificações nativas"""

    def __init__(self):
        self.toaster = ToastNotifier() if platform.system() == "Windows" else None

    def show_notification(self, title: str, message: str, duration: int = 5):
        """Exibe uma notificação nativa"""
        if self.toaster:
            try:
                self.toaster.show_toast(
                    title, message, duration=duration, threaded=True
                )
            except Exception as e:
                print(f"Erro na notificação: {e}")
        else:
            print(f"Notificação: {title} - {message}")  # Fallback para outros SO
