"""
Classe abstrata que define a API comum para todas as implementações de grafos.

Esta classe estabelece o contrato que todas as implementações concretas
(AdjacencyListGraph, AdjacencyMatrixGraph) devem seguir.

Um grafo simples é aquele que:
- Não possui self-loops (arestas u → u)
- Não possui múltiplas arestas entre o mesmo par de vértices
- Permite ponderar arestas com pesos

A herança é fundamental aqui pois centraliza validações e oferece
uma interface consistente para diferentes implementações.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ...exceptions.graph_exceptions import InvalidVertexError


class AbstractGraph(ABC):
    """Classe abstrata que define a API comum de um grafo direcionado simples.

    Esta classe não pode ser instanciada diretamente; deve ser subclasseada
    por implementações concretas como AdjacencyListGraph ou AdjacencyMatrixGraph.

    Protected Attributes:
        _vertex_count: Número total de vértices no grafo
        _edge_count: Número total de arestas no grafo
        _vertex_weights: Lista de pesos dos vértices [0, 1, ...]
        _labels: Lista de rótulos dos vértices (ex: nomes de usuários)
    """

    def __init__(self, vertex_count: int):
        """Inicializa um grafo vazio com um número específico de vértices.

        Args:
            vertex_count: Número de vértices (deve ser > 0)

        Raises:
            ValueError: Se vertex_count <= 0
        """
        if vertex_count <= 0:
            raise ValueError(f"vertex_count must be > 0, got {vertex_count}")

        self._vertex_count = vertex_count
        self._edge_count = 0

        # Pesos padrão de 1.0 para cada vértice
        self._vertex_weights: List[float] = [1.0] * vertex_count

        # Rótulos inicialmente None (podem ser atribuídos depois)
        self._labels: List[Optional[str]] = [None] * vertex_count

    # ========== VALIDAÇÃO ==========

    def _validate_vertex(self, v: int) -> None:
        """Valida se um vértice está no intervalo válido [0, vertex_count).

        Args:
            v: Identificador do vértice

        Raises:
            InvalidVertexError: Se vértice inválido
        """
        if v < 0 or v >= self._vertex_count:
            raise InvalidVertexError(v, self._vertex_count)

    def _validate_vertices(self, u: int, v: int) -> None:
        """Valida se dois vértices são válidos.

        Args:
            u: Primeiro vértice
            v: Segundo vértice

        Raises:
            InvalidVertexError: Se algum vértice for inválido
        """
        self._validate_vertex(u)
        self._validate_vertex(v)

    # ========== INFORMAÇÃO BÁSICA ==========

    def get_vertex_count(self) -> int:
        """Retorna o número total de vértices no grafo."""
        return self._vertex_count

    def get_edge_count(self) -> int:
        """Retorna o número total de arestas no grafo."""
        return self._edge_count

    def is_empty_graph(self) -> bool:
        """Verifica se o grafo não possui nenhuma aresta."""
        return self._edge_count == 0

    # ========== PESOS DE VÉRTICES ==========

    def set_vertex_weight(self, v: int, weight: float) -> None:
        """Define o peso de um vértice.

        O peso de um vértice pode representar importância, centralidade, etc.

        Args:
            v: Identificador do vértice
            weight: Novo peso (deve ser >= 0)

        Raises:
            InvalidVertexError: Se vértice inválido
            ValueError: Se weight < 0
        """
        self._validate_vertex(v)
        if weight < 0:
            raise ValueError(f"Weight must be >= 0, got {weight}")
        self._vertex_weights[v] = float(weight)

    def get_vertex_weight(self, v: int) -> float:
        """Retorna o peso de um vértice.

        Args:
            v: Identificador do vértice

        Returns:
            Peso do vértice

        Raises:
            InvalidVertexError: Se vértice inválido
        """
        self._validate_vertex(v)
        return self._vertex_weights[v]

    # ========== RÓTULOS DE VÉRTICES ==========

    def set_vertex_label(self, v: int, label: str) -> None:
        """Define o rótulo de um vértice (ex: nome de usuário).

        Args:
            v: Identificador do vértice
            label: Novo rótulo

        Raises:
            InvalidVertexError: Se vértice inválido
        """
        self._validate_vertex(v)
        self._labels[v] = label

    def get_vertex_label(self, v: int) -> Optional[str]:
        """Retorna o rótulo de um vértice.

        Args:
            v: Identificador do vértice

        Returns:
            Rótulo do vértice, ou None se não foi atribuído

        Raises:
            InvalidVertexError: Se vértice inválido
        """
        self._validate_vertex(v)
        return self._labels[v]

    # ========== OPERAÇÕES COM ARESTAS (ABSTRATAS) ==========

    @abstractmethod
    def add_edge(self, u: int, v: int, weight: float = 1.0) -> None:
        """Adiciona uma aresta direcionada u → v.

        Comportamento:
        - Rejeita self-loops (u == v) levantando SelfLoopError
        - Se aresta já existe, acumula o peso (idempotência)
        - Valida automaticamente os vértices

        Args:
            u: Vértice origem
            v: Vértice destino
            weight: Peso da aresta (padrão: 1.0)

        Raises:
            InvalidVertexError: Se vértice inválido
            SelfLoopError: Se tentou criar u → u
            ValueError: Se weight < 0
        """
        pass

    @abstractmethod
    def remove_edge(self, u: int, v: int) -> None:
        """Remove a aresta direcionada u → v.

        Args:
            u: Vértice origem
            v: Vértice destino

        Raises:
            InvalidVertexError: Se vértice inválido
            InvalidEdgeError: Se aresta não existe
        """
        pass

    @abstractmethod
    def has_edge(self, u: int, v: int) -> bool:
        """Verifica se existe aresta u → v.

        Args:
            u: Vértice origem
            v: Vértice destino

        Returns:
            True se aresta existe, False caso contrário

        Raises:
            InvalidVertexError: Se vértice inválido
        """
        pass

    # ========== PESOS DE ARESTAS ==========

    @abstractmethod
    def set_edge_weight(self, u: int, v: int, weight: float) -> None:
        """Define o peso da aresta u → v.

        Args:
            u: Vértice origem
            v: Vértice destino
            weight: Novo peso (deve ser >= 0)

        Raises:
            InvalidVertexError: Se vértice inválido
            InvalidEdgeError: Se aresta não existe
            ValueError: Se weight < 0
        """
        pass

    @abstractmethod
    def get_edge_weight(self, u: int, v: int) -> float:
        """Retorna o peso da aresta u → v.

        Args:
            u: Vértice origem
            v: Vértice destino

        Returns:
            Peso da aresta (>= 0)

        Raises:
            InvalidVertexError: Se vértice inválido
            InvalidEdgeError: Se aresta não existe
        """
        pass

    # ========== GRAUS ==========

    @abstractmethod
    def get_vertex_in_degree(self, v: int) -> int:
        """Retorna o grau de entrada (in-degree) de um vértice.

        O in-degree é o número de arestas que chegam em v.

        Exemplo:
            Se existem arestas 1 → 3 e 2 → 3, então in_degree(3) = 2

        Args:
            v: Identificador do vértice

        Returns:
            Número de arestas entrando em v (>= 0)

        Raises:
            InvalidVertexError: Se vértice inválido
        """
        pass

    @abstractmethod
    def get_vertex_out_degree(self, v: int) -> int:
        """Retorna o grau de saída (out-degree) de um vértice.

        O out-degree é o número de arestas que saem de v.

        Exemplo:
            Se existem arestas 0 → 1 e 0 → 2, então out_degree(0) = 2

        Args:
            v: Identificador do vértice

        Returns:
            Número de arestas saindo de v (>= 0)

        Raises:
            InvalidVertexError: Se vértice inválido
        """
        pass

    # ========== RELAÇÕES ENTRE VÉRTICES ==========

    @abstractmethod
    def is_successor(self, u: int, v: int) -> bool:
        """Verifica se v é sucessor de u (existe aresta u → v).

        Args:
            u: Vértice origem
            v: Vértice destino

        Returns:
            True se u → v existe, False caso contrário

        Raises:
            InvalidVertexError: Se vértice inválido
        """
        pass

    @abstractmethod
    def is_predecessor(self, u: int, v: int) -> bool:
        """Verifica se v é predecessor de u (existe aresta v → u).

        Args:
            u: Vértice destino
            v: Vértice origem (potencial)

        Returns:
            True se v → u existe, False caso contrário

        Raises:
            InvalidVertexError: Se vértice inválido
        """
        pass

    @abstractmethod
    def is_divergent(self, u1: int, v1: int, u2: int, v2: int) -> bool:
        """Verifica se duas arestas divergem do mesmo ponto.

        Arestas divergem se partem do mesmo vértice mas vão para destinos diferentes.

        Exemplo:
            is_divergent(0, 1, 0, 2) → True (ambas saem de 0)

        Args:
            u1, v1: Primeira aresta (u1 → v1)
            u2, v2: Segunda aresta (u2 → v2)

        Returns:
            True se arestas divergem, False caso contrário

        Raises:
            InvalidVertexError: Se algum vértice inválido
        """
        pass

    @abstractmethod
    def is_convergent(self, u1: int, v1: int, u2: int, v2: int) -> bool:
        """Verifica se duas arestas convergem para o mesmo ponto.

        Arestas convergem se vêm de origens diferentes mas vão para o mesmo destino.

        Exemplo:
            is_convergent(0, 2, 1, 2) → True (ambas chegam em 2)

        Args:
            u1, v1: Primeira aresta (u1 → v1)
            u2, v2: Segunda aresta (u2 → v2)

        Returns:
            True se arestas convergem, False caso contrário

        Raises:
            InvalidVertexError: Se algum vértice inválido
        """
        pass

    @abstractmethod
    def is_incident(self, u: int, v: int, x: int) -> bool:
        """Verifica se vértice x participa da aresta u → v.

        Um vértice participa da aresta se é origem ou destino.

        Exemplo:
            is_incident(0, 2, 0) → True (0 é origem de 0 → 2)
            is_incident(0, 2, 2) → True (2 é destino de 0 → 2)
            is_incident(0, 2, 1) → False (1 não participa)

        Args:
            u: Vértice origem da aresta
            v: Vértice destino da aresta
            x: Vértice a verificar

        Returns:
            True se x participa de u → v, False caso contrário

        Raises:
            InvalidVertexError: Se algum vértice inválido
        """
        pass

    # ========== PROPRIEDADES DO GRAFO ==========

    @abstractmethod
    def is_connected(self) -> bool:
        """Verifica se o grafo é fortemente conectado.

        Um grafo é fortemente conectado se existe caminho de todo vértice
        para todo outro vértice (considerando a direção das arestas).

        Implementação: Usar DFS ou BFS a partir de cada vértice e verificar
        se todos os vértices são alcançáveis.

        Returns:
            True se grafo é fortemente conectado, False caso contrário
        """
        pass

    @abstractmethod
    def is_complete_graph(self) -> bool:
        """Verifica se o grafo é completo.

        Um grafo direcionado é completo se existe aresta entre TODOS
        os pares distintos de vértices (em ambas direções).

        Para um grafo com n vértices, deve haver n*(n-1) arestas.

        Returns:
            True se grafo é completo, False caso contrário
        """
        pass

    # ========== EXPORTAÇÃO ==========

    @abstractmethod
    def export_to_gephi(self, filepath: str, format: str = "gexf") -> None:
        """Exporta o grafo para formato aceito pelo Gephi.

        Formatos suportados:
        - 'gexf': GEXF (Graph Exchange XML Format)
        - 'graphml': GraphML (XML)
        - 'csv': CSV simples (nodes.csv + edges.csv)

        Args:
            filepath: Caminho do arquivo (sem extensão)
            format: Formato desejado ('gexf', 'graphml', 'csv')

        Raises:
            ValueError: Se formato não suportado
            IOError: Se erro ao escrever arquivo
        """
        pass

    # ========== REPRESENTAÇÃO ==========

    def __repr__(self) -> str:
        """Representação string concisa do grafo."""
        return (
            f"{self.__class__.__name__}("
            f"vertices={self._vertex_count}, "
            f"edges={self._edge_count})"
        )

    def __str__(self) -> str:
        """String descritiva detalhada do grafo."""
        return (
            f"Grafo: {self._vertex_count} vértices, "
            f"{self._edge_count} arestas\n"
            f"Conectado: {self.is_connected()}\n"
            f"Completo: {self.is_complete_graph()}"
        )
