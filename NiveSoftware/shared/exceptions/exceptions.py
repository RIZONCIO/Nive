"""
exceptions.py - Exceções personalizadas para o NiveSoftware.
"""


class NiveError(Exception):
    """Exceção base para o ecossistema Nive."""
    pass


class AdminPrivilegeError(NiveError):
    """Lançada quando uma operação requer privilégios de Administrador."""
    pass


class CommandExecutionError(NiveError):
    """Lançada quando a execução de um comando falha."""
    def __init__(self, message: str, returncode: int = 1, output: str = ""):
        super().__init__(message)
        self.returncode = returncode
        self.output = output


class ValidationError(NiveError):
    """Lançada quando uma validação de parâmetro ou caminho falha."""
    pass
