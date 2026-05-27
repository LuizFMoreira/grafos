"""
Exceções relacionadas a mineração de dados do GitHub.

Este módulo define exceções específicas para erros que podem ocorrer
durante a integração com a API do GitHub.
"""


class GithubMiningError(Exception):
    """Exceção base para erros de mineração."""
    pass


class RateLimitExceededError(GithubMiningError):
    """Levantada quando o rate limit da API GitHub é excedido.

    GitHub limita requisições a 5000 por hora. Esta exceção indica
    que é necessário esperar antes de fazer mais requisições.
    """

    def __init__(self, message: str):
        super().__init__(message)


class InvalidRepositoryError(GithubMiningError):
    """Levantada quando o repositório especificado não existe."""

    def __init__(self, message: str):
        super().__init__(message)


class DataParsingError(GithubMiningError):
    """Levantada quando há erro ao parsear dados da API."""

    def __init__(self, message: str):
        super().__init__(f"Erro ao parsear dados: {message}")
