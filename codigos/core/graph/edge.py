"""
Classe que representa uma aresta em um grafo.

Uma aresta representa uma conexão direcionada entre dois vértices.
Neste sistema, cada aresta possui um destino e um peso que representa
a intensidade/força da conexão.
"""

from typing import Optional


class Edge:
    """Representa uma aresta direcionada em um grafo.

    Uma aresta conecta um vértice de origem (implícito) a um vértice de destino.
    O peso representa a intensidade da conexão (ex: número de interações).

    Attributes:
        destination: Identificador do vértice destino (>= 0)
        weight: Peso da aresta (>= 0.0)

    Example:
        >>> edge = Edge(destination=5, weight=2.5)
        >>> edge.destination
        5
        >>> edge.weight
        2.5
        >>> edge.increase_weight(1.5)
        >>> edge.weight
        4.0
    """

    __slots__ = ("_destination", "_weight")

    def __init__(self, destination: int, weight: float = 1.0):
        """Inicializa uma aresta.

        Args:
            destination: Identificador do vértice destino
            weight: Peso inicial da aresta (padrão: 1.0)

        Raises:
            ValueError: Se destination < 0 ou weight < 0
        """
        if destination < 0:
            raise ValueError(f"Destination must be >= 0, got {destination}")
        if weight < 0:
            raise ValueError(f"Weight must be >= 0, got {weight}")

        self._destination = destination
        self._weight = float(weight)

    @property
    def destination(self) -> int:
        """Retorna o vértice destino desta aresta."""
        return self._destination

    @property
    def weight(self) -> float:
        """Retorna o peso desta aresta."""
        return self._weight

    @weight.setter
    def weight(self, value: float) -> None:
        """Define um novo peso para esta aresta.

        Args:
            value: Novo peso (deve ser >= 0)

        Raises:
            ValueError: Se value < 0
        """
        if value < 0:
            raise ValueError(f"Weight must be >= 0, got {value}")
        self._weight = float(value)

    def increase_weight(self, delta: float) -> None:
        """Aumenta o peso desta aresta.

        Útil para acumular pesos quando a mesma conexão ocorre múltiplas vezes.

        Args:
            delta: Valor a adicionar (deve ser > 0)

        Raises:
            ValueError: Se delta < 0
        """
        if delta < 0:
            raise ValueError(f"Delta must be >= 0, got {delta}")
        self._weight += delta

    def __repr__(self) -> str:
        """Representação string da aresta."""
        return f"Edge(dest={self._destination}, weight={self._weight:.2f})"

    def __eq__(self, other: object) -> bool:
        """Duas arestas são iguais se têm o mesmo destino."""
        if not isinstance(other, Edge):
            return NotImplemented
        return self._destination == other._destination

    def __hash__(self) -> int:
        """Hash baseado no destino (para usar em sets/dicts)."""
        return hash(self._destination)

    def __lt__(self, other: "Edge") -> bool:
        """Compara arestas por destino (para ordenação)."""
        if not isinstance(other, Edge):
            return NotImplemented
        return self._destination < other._destination
