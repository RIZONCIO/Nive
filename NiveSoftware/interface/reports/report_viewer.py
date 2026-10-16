"""
report_viewer.py - Visualização e apresentação de relatórios de auditoria e diagnóstico.
"""

from typing import Dict, Any, Optional
from datetime import datetime


class ReportViewer:
    """Apresentação de relatórios para interface gráfica e exportação."""

    @staticmethod
    def format_summary(report_data: Dict[str, Any]) -> str:
        """Formata os dados de um relatório para exibição em texto/widget."""
        lines = [
            "=" * 50,
            f" RELATÓRIO DO SCRIPTNIVE - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            "=" * 50,
            "",
        ]
        for key, value in report_data.items():
            lines.append(f"[{key.upper()}]: {value}")
        lines.append("")
        lines.append("=" * 50)
        return "\n".join(lines)
