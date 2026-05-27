"""
Minerador de dados do GitHub.

Responsável por coletar dados da API do GitHub, parseá-los
em modelos de domínio e preparar para construção de grafos.
"""

from .github_client import GithubClient
from .github_parser import GithubParser
from .rate_limiter import RateLimiter
from .data_transformer import DataTransformer

__all__ = [
    "GithubClient",
    "GithubParser",
    "RateLimiter",
    "DataTransformer",
]
