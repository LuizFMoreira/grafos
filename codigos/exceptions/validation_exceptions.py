"""
Exceções relacionadas a validação de dados.

Este módulo define exceções para falhas em validações gerais do sistema.
"""


class ValidationError(Exception):
    """Levantada quando dados não passam em validação."""

    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(f"Validação falhou para '{field}': {message}")


class ConfigurationError(Exception):
    """Levantada quando há erro na configuração do sistema."""

    def __init__(self, message: str):
        super().__init__(f"Erro de configuração: {message}")
