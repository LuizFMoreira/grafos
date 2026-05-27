"""
Exceções customizadas do sistema.

Este módulo centraliza todas as exceções customizadas utilizadas no projeto.
"""

from .graph_exceptions import (
    GraphOperationError,
    InvalidVertexError,
    InvalidEdgeError,
    SelfLoopError,
)

from .mining_exceptions import (
    GithubMiningError,
    RateLimitExceededError,
    InvalidRepositoryError,
    DataParsingError,
)

from .validation_exceptions import (
    ValidationError,
    ConfigurationError,
)

__all__ = [
    "GraphOperationError",
    "InvalidVertexError",
    "InvalidEdgeError",
    "SelfLoopError",
    "GithubMiningError",
    "RateLimitExceededError",
    "InvalidRepositoryError",
    "DataParsingError",
    "ValidationError",
    "ConfigurationError",
]
