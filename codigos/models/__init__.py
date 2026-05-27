"""
Modelos de dados do projeto.

Contém classes que representam:
- Usuários (User)
- Tipos de interação (InteractionType)
- Interações (Interaction)
- Dados do GitHub (Issue, PullRequest, Review, Comment, MetricsResult)
- Grafo de colaboração (CollaborationGraph)
"""

from .user import User
from .interaction_type import InteractionType
from .interaction import Interaction
from .github_data import (
    Issue,
    PullRequest,
    Review,
    Comment,
    MetricsResult,
    CollaborationGraph,
)

__all__ = [
    "User",
    "InteractionType",
    "Interaction",
    "Issue",
    "PullRequest",
    "Review",
    "Comment",
    "MetricsResult",
    "CollaborationGraph",
]
