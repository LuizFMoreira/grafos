"""
Modelo de Interação entre Usuários.

Representa uma ação colaborativa entre dois usuários.
"""

from dataclasses import dataclass
from datetime import datetime

from .user import User
from .interaction_type import InteractionType


@dataclass(frozen=True)
class Interaction:
    """Representa uma interação entre dois usuários.

    Atributos:
        source: Usuário que realizou a ação
        target: Usuário que recebeu a ação
        interaction_type: Tipo de interação
        timestamp: Data e hora da interação
        url: URL da ação (issue, PR, comentário, etc)

    Exemplo:
        >>> user_a = User(id=1, login="alice")
        >>> user_b = User(id=2, login="bob")
        >>> interaction = Interaction(
        ...     source=user_a,
        ...     target=user_b,
        ...     interaction_type=InteractionType.PR_REVIEW,
        ...     timestamp=datetime.now(),
        ...     url="https://github.com/owner/repo/pull/1"
        ... )
        >>> interaction.weight
        4
    """

    source: User
    target: User
    interaction_type: InteractionType
    timestamp: datetime
    url: str

    def __post_init__(self):
        """Valida a interação."""
        if self.source.id == self.target.id:
            raise ValueError(f"Interaction cannot be self-loop: {self.source} → {self.target}")
        if not isinstance(self.url, str) or not self.url:
            raise ValueError(f"URL must be non-empty string, got {self.url}")

    @property
    def weight(self) -> int:
        """Retorna o peso da interação baseado no tipo."""
        return self.interaction_type.weight

    def __repr__(self) -> str:
        """Representação string."""
        return (
            f"Interaction({self.source.login} → {self.target.login}, "
            f"type={self.interaction_type.name}, weight={self.weight})"
        )

    def __hash__(self) -> int:
        """Hashable para usar em sets/dicts."""
        return hash((self.source, self.target, self.interaction_type))
