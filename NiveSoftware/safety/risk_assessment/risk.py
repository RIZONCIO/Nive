"""
risk.py - Avaliação de riscos para tweaks e operações do sistema.
"""

from typing import Dict, Any


class RiskAssessment:
    """Avaliação de riscos de operações de otimização e reparo."""

    RISK_LEVELS = {
        "acelerar_windows": {
            "level": "ALTO",
            "warning": "Não recomendado para SSD NVMe M.2 sem ponto de restauração.",
            "requires_backup": True,
        },
        "desabilitar_servicos": {
            "level": "MÉDIO",
            "warning": "Desativa serviços secundários do Windows. Pode afetar recursos específicos.",
            "requires_backup": True,
        },
        "reparo_completo": {
            "level": "MÉDIO",
            "warning": "Reinicia serviços de rede e atualização. Pode solicitar reinicialização.",
            "requires_backup": False,
        },
        "limpar_temp": {
            "level": "BAIXO",
            "warning": "Limpa arquivos temporários sem impacto estrutural no sistema.",
            "requires_backup": False,
        },
    }

    @classmethod
    def get_risk_info(cls, operation: str) -> Dict[str, Any]:
        """Retorna o nível de risco e avisos da operação."""
        return cls.RISK_LEVELS.get(
            operation,
            {
                "level": "DESCONHECIDO",
                "warning": "Recomenda-se criar um ponto de restauração antes de continuar.",
                "requires_backup": True,
            },
        )
