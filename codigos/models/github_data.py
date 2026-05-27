"""
Modelos de dados do GitHub.

Representa estruturas de dados retornadas pela API do GitHub:
Issues, Pull Requests, Reviews, Comments, etc.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

from .user import User


@dataclass
class Issue:
    """Representa uma issue do GitHub.

    Atributos:
        number: Número da issue no repositório
        title: Título da issue
        author: Usuário que criou a issue
        created_at: Data de criação
        updated_at: Data da última atualização
        url: URL da issue
        state: Estado ('open' ou 'closed')
    """

    number: int
    title: str
    author: User
    created_at: datetime
    updated_at: datetime
    url: str
    state: str = "open"

    def __post_init__(self):
        if self.number < 1:
            raise ValueError(f"Issue number must be >= 1, got {self.number}")
        if self.state not in ("open", "closed"):
            raise ValueError(f"Invalid state: {self.state}")


@dataclass
class PullRequest:
    """Representa um Pull Request do GitHub.

    Atributos:
        number: Número do PR no repositório
        title: Título do PR
        author: Usuário que criou o PR
        created_at: Data de criação
        updated_at: Data da última atualização
        merged_at: Data do merge (None se não mergeado)
        merged_by: Usuário que fez merge (None se não mergeado)
        url: URL do PR
        state: Estado ('open', 'closed', ou 'merged')
    """

    number: int
    title: str
    author: User
    created_at: datetime
    updated_at: datetime
    url: str
    merged_at: Optional[datetime] = None
    merged_by: Optional[User] = None
    state: str = "open"

    def __post_init__(self):
        if self.number < 1:
            raise ValueError(f"PR number must be >= 1, got {self.number}")
        if self.state not in ("open", "closed", "merged"):
            raise ValueError(f"Invalid state: {self.state}")
        if self.merged_at and not self.merged_by:
            raise ValueError("merged_at requires merged_by to be set")

    @property
    def is_merged(self) -> bool:
        """Verifica se o PR foi mergeado."""
        return self.merged_by is not None


@dataclass
class Review:
    """Representa um Code Review do GitHub.

    Atributos:
        id: Identificador único do review
        author: Usuário que fez o review
        pr_number: Número do PR que foi revisado
        state: Estado do review ('APPROVED', 'REQUESTED_CHANGES', 'COMMENTED', 'PENDING')
        submitted_at: Data do envio
        url: URL do review
    """

    id: int
    author: User
    pr_number: int
    state: str
    submitted_at: datetime
    url: str

    def __post_init__(self):
        valid_states = ("APPROVED", "REQUESTED_CHANGES", "COMMENTED", "PENDING", "DISMISSED")
        if self.state not in valid_states:
            raise ValueError(f"Invalid review state: {self.state}")

    @property
    def is_approval(self) -> bool:
        """Verifica se é uma aprovação."""
        return self.state == "APPROVED"


@dataclass
class Comment:
    """Representa um comentário no GitHub.

    Atributos:
        id: Identificador único do comentário
        author: Usuário que fez o comentário
        body: Texto do comentário
        created_at: Data de criação
        updated_at: Data da última atualização
        url: URL do comentário
        issue_number: Número da issue (None se em PR)
        pr_number: Número do PR (None se em issue)
    """

    id: int
    author: User
    body: str
    created_at: datetime
    updated_at: datetime
    url: str
    issue_number: Optional[int] = None
    pr_number: Optional[int] = None

    def __post_init__(self):
        if not self.body or not isinstance(self.body, str):
            raise ValueError(f"Comment body must be non-empty string, got {self.body}")
        if not (self.issue_number or self.pr_number):
            raise ValueError("Comment must be in an issue or PR")


@dataclass
class MetricsResult:
    """Armazena resultados de cálculos de métricas.

    Atributos:
        user: Usuário analisado
        degree_centrality: Centralidade de grau (0-1)
        in_degree: Número de arestas entrando
        out_degree: Número de arestas saindo
        betweenness_centrality: Centralidade de intermediação (0-1)
        closeness_centrality: Centralidade de proximidade (0-1)
        pagerank: PageRank do usuário
        clustering_coefficient: Coeficiente de clustering (0-1)
        eigenvector_centrality: Centralidade de autovetor (0-1)
    """

    user: User
    degree_centrality: float = 0.0
    in_degree: int = 0
    out_degree: int = 0
    betweenness_centrality: float = 0.0
    closeness_centrality: float = 0.0
    pagerank: float = 0.0
    clustering_coefficient: float = 0.0
    eigenvector_centrality: float = 0.0

    def __post_init__(self):
        # Valida que métricas estão em [0, 1]
        metrics = [
            self.degree_centrality,
            self.betweenness_centrality,
            self.closeness_centrality,
            self.clustering_coefficient,
            self.eigenvector_centrality,
        ]
        for metric in metrics:
            if not (0.0 <= metric <= 1.0):
                raise ValueError(f"Metric must be in [0, 1], got {metric}")

        if self.pagerank < 0.0:
            raise ValueError(f"PageRank must be >= 0, got {self.pagerank}")

        if self.in_degree < 0 or self.out_degree < 0:
            raise ValueError("Degrees must be >= 0")

    def __repr__(self) -> str:
        """Representação string."""
        return (
            f"MetricsResult({self.user.login}, "
            f"degree={self.degree_centrality:.3f}, "
            f"pagerank={self.pagerank:.3f})"
        )


@dataclass
class CollaborationGraph:
    """Representa a estrutura completa do grafo de colaboração.

    Atributos:
        repository: Nome do repositório (owner/repo)
        users: Lista de usuários únicos
        interactions: Lista de interações
        issues: Lista de issues mineradas
        pull_requests: Lista de PRs minerados
        reviews: Lista de reviews minerados
        comments: Lista de comentários minerados
        mined_at: Data da mineração
    """

    repository: str
    users: List[User] = field(default_factory=list)
    interactions: List = field(default_factory=list)  # List[Interaction]
    issues: List[Issue] = field(default_factory=list)
    pull_requests: List[PullRequest] = field(default_factory=list)
    reviews: List[Review] = field(default_factory=list)
    comments: List[Comment] = field(default_factory=list)
    mined_at: Optional[datetime] = None

    @property
    def user_count(self) -> int:
        """Número de usuários únicos."""
        return len(self.users)

    @property
    def interaction_count(self) -> int:
        """Número total de interações."""
        return len(self.interactions)

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Busca usuário por ID."""
        for user in self.users:
            if user.id == user_id:
                return user
        return None

    def get_user_by_login(self, login: str) -> Optional[User]:
        """Busca usuário por login."""
        for user in self.users:
            if user.login.lower() == login.lower():
                return user
        return None
