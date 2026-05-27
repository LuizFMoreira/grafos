"""
Modelo de Usuário.

Representa um desenvolvedor no GitHub com id e login.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    """Representa um usuário (desenvolvedor) no GitHub.

    Atributos:
        id: Identificador numérico único do usuário (GitHub user ID)
        login: Nome de usuário (GitHub username)

    Exemplo:
        >>> user = User(id=12345, login="john_doe")
        >>> print(user.id)
        12345
    """

    id: int
    login: str

    def __post_init__(self):
        """Valida atributos após inicialização."""
        if self.id < 0:
            raise ValueError(f"User id must be >= 0, got {self.id}")
        if not self.login or not isinstance(self.login, str):
            raise ValueError(f"User login must be non-empty string, got {self.login}")

    def __repr__(self) -> str:
        """Representação string."""
        return f"User(id={self.id}, login='{self.login}')"

    def __hash__(self) -> int:
        """Hashable para usar em sets/dicts."""
        return hash((self.id, self.login))
