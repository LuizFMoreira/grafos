"""
Implementação de grafo usando listas de adjacência.

Esta implementação usa um dicionário que mapeia cada vértice a uma lista de arestas.
É mais eficiente para grafos esparsos (poucos arestas) pois usa espaço O(V + E)
em vez de O(V²) como a matriz.

Estrutura:
    {
        0: [Edge(1, 2.0), Edge(2, 3.5)],
        1: [Edge(3, 1.5)],
        2: [],
        3: [Edge(0, 2.0)]
    }
"""

from typing import Dict, List, Optional, Tuple

from .edge import Edge
from .abstract_graph import AbstractGraph
from ..exceptions.graph_exceptions import (
    InvalidVertexError,
    InvalidEdgeError,
    SelfLoopError,
)


class AdjacencyListGraph(AbstractGraph):
    """Implementação de grafo usando listas de adjacência.

    Usa um dicionário onde cada vértice mapeia para uma lista de arestas.
    Ideal para grafos esparsos (muitos vértices, poucas arestas).

    Complexidade de Espaço: O(V + E)
    Complexidade de Tempo:
        - has_edge: O(grau do vértice)
        - add_edge: O(grau do vértice)
        - remove_edge: O(grau do vértice)
        - get neighbors: O(1)

    Attributes:
        _adjacency: Dict[int, List[Edge]] - Mapa vértice → lista de arestas
    """

    def __init__(self, vertex_count: int):
        """Inicializa um grafo vazio com listas de adjacência.

        Args:
            vertex_count: Número de vértices

        Raises:
            ValueError: Se vertex_count <= 0
        """
        super().__init__(vertex_count)

        # Dicionário: vértice → lista de arestas saindo dele
        self._adjacency: Dict[int, List[Edge]] = {
            v: [] for v in range(vertex_count)
        }

    # ========== OPERAÇÕES COM ARESTAS ==========

    def add_edge(self, u: int, v: int, weight: float = 1.0) -> None:
        """Adiciona aresta direcionada u → v.

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
        self._validate_vertices(u, v)

        # Rejeita self-loops (restrição de grafos simples)
        if u == v:
            raise SelfLoopError(u)

        if weight < 0:
            raise ValueError(f"Weight must be >= 0, got {weight}")

        # Procura se aresta já existe
        for edge in self._adjacency[u]:
            if edge.destination == v:
                # Aresta existe: acumula peso (idempotência)
                edge.increase_weight(weight)
                return

        # Aresta não existe: cria nova
        new_edge = Edge(v, weight)
        self._adjacency[u].append(new_edge)
        self._edge_count += 1

    def remove_edge(self, u: int, v: int) -> None:
        """Remove a aresta direcionada u → v.

        Args:
            u: Vértice origem
            v: Vértice destino

        Raises:
            InvalidVertexError: Se vértice inválido
            InvalidEdgeError: Se aresta não existe
        """
        self._validate_vertices(u, v)

        # Procura a aresta
        for i, edge in enumerate(self._adjacency[u]):
            if edge.destination == v:
                # Encontrou: remove
                self._adjacency[u].pop(i)
                self._edge_count -= 1
                return

        # Não encontrou
        raise InvalidEdgeError(u, v)

    def has_edge(self, u: int, v: int) -> bool:
        """Verifica se existe aresta u → v."""
        self._validate_vertices(u, v)

        for edge in self._adjacency[u]:
            if edge.destination == v:
                return True
        return False

    def set_edge_weight(self, u: int, v: int, weight: float) -> None:
        """Define o peso da aresta u → v."""
        self._validate_vertices(u, v)

        if weight < 0:
            raise ValueError(f"Weight must be >= 0, got {weight}")

        for edge in self._adjacency[u]:
            if edge.destination == v:
                edge.weight = weight
                return

        raise InvalidEdgeError(u, v)

    def get_edge_weight(self, u: int, v: int) -> float:
        """Retorna o peso da aresta u → v."""
        self._validate_vertices(u, v)

        for edge in self._adjacency[u]:
            if edge.destination == v:
                return edge.weight

        raise InvalidEdgeError(u, v)

    # ========== GRAUS ==========

    def get_vertex_in_degree(self, v: int) -> int:
        """Retorna o grau de entrada do vértice v.

        Para lista de adjacência, deve iterar sobre todas as listas.
        """
        self._validate_vertex(v)

        in_degree = 0
        # Itera sobre todos os vértices
        for source in self._adjacency:
            # Verifica se há aresta source → v
            for edge in self._adjacency[source]:
                if edge.destination == v:
                    in_degree += 1
                    break  # Pode haver apenas uma aresta

        return in_degree

    def get_vertex_out_degree(self, v: int) -> int:
        """Retorna o grau de saída do vértice v."""
        self._validate_vertex(v)
        return len(self._adjacency[v])

    # ========== RELAÇÕES ENTRE VÉRTICES ==========

    def is_successor(self, u: int, v: int) -> bool:
        """Verifica se v é sucessor de u (existe u → v)."""
        return self.has_edge(u, v)

    def is_predecessor(self, u: int, v: int) -> bool:
        """Verifica se v é predecessor de u (existe v → u)."""
        return self.has_edge(v, u)

    def is_divergent(self, u1: int, v1: int, u2: int, v2: int) -> bool:
        """Verifica se arestas divergem do mesmo ponto."""
        self._validate_vertices(u1, v1, u2, v2)
        return u1 == u2 and v1 != v2

    def is_convergent(self, u1: int, v1: int, u2: int, v2: int) -> bool:
        """Verifica se arestas convergem para o mesmo ponto."""
        self._validate_vertices(u1, v1, u2, v2)
        return v1 == v2 and u1 != u2

    def is_incident(self, u: int, v: int, x: int) -> bool:
        """Verifica se x participa da aresta u → v."""
        self._validate_vertices(u, v, x)
        return x == u or x == v

    # ========== PROPRIEDADES DO GRAFO ==========

    def is_connected(self) -> bool:
        """Verifica se o grafo é fortemente conectado.

        Um grafo é fortemente conectado se existe caminho de todo vértice
        para todo outro vértice.

        Usa DFS a partir de cada vértice para verificar conectividade.
        """
        if self._vertex_count == 0:
            return True

        # Verifica se todos os vértices são alcançáveis a partir do vértice 0
        visited = set()
        self._dfs(0, visited)

        # Se nem todos foram visitados a partir de 0, não é conectado
        if len(visited) != self._vertex_count:
            return False

        # Cria grafo reverso (inverte todas as arestas)
        reversed_graph = AdjacencyListGraph(self._vertex_count)
        for u in self._adjacency:
            for edge in self._adjacency[u]:
                reversed_graph.add_edge(edge.destination, u, edge.weight)

        # Verifica se todos são alcançáveis no grafo reverso
        visited = set()
        reversed_graph._dfs(0, visited)

        return len(visited) == self._vertex_count

    def is_complete_graph(self) -> bool:
        """Verifica se o grafo é completo.

        Um grafo direcionado é completo se existe aresta entre todos
        os pares distintos de vértices (em ambas direções).

        Para n vértices, deve haver n*(n-1) arestas.
        """
        expected_edges = self._vertex_count * (self._vertex_count - 1)
        return self._edge_count == expected_edges

    # ========== MÉTODOS AUXILIARES ==========

    def _dfs(self, start: int, visited: set) -> None:
        """DFS (Depth First Search) iterativa.

        Args:
            start: Vértice inicial
            visited: Conjunto de vértices visitados (modificado in-place)
        """
        stack = [start]

        while stack:
            v = stack.pop()

            if v in visited:
                continue

            visited.add(v)

            # Adiciona vizinhos não visitados
            for edge in self._adjacency[v]:
                if edge.destination not in visited:
                    stack.append(edge.destination)

    def get_successors(self, v: int) -> List[int]:
        """Retorna lista de sucessores (vizinhos de saída) do vértice v."""
        self._validate_vertex(v)
        return [edge.destination for edge in self._adjacency[v]]

    def get_predecessors(self, v: int) -> List[int]:
        """Retorna lista de predecessores (vizinhos de entrada) do vértice v."""
        self._validate_vertex(v)

        predecessors = []
        for source in self._adjacency:
            for edge in self._adjacency[source]:
                if edge.destination == v:
                    predecessors.append(source)
                    break

        return predecessors

    # ========== EXPORTAÇÃO ==========

    def export_to_gephi(self, filepath: str, format: str = "gexf") -> None:
        """Exporta o grafo para formato Gephi.

        Args:
            filepath: Caminho do arquivo (sem extensão)
            format: Formato ('gexf', 'graphml', 'csv')

        Raises:
            ValueError: Se formato não suportado
            IOError: Se erro ao escrever arquivo
        """
        if format == "gexf":
            self._export_gexf(filepath)
        elif format == "graphml":
            self._export_graphml(filepath)
        elif format == "csv":
            self._export_csv(filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_gexf(self, filepath: str) -> None:
        """Exporta para formato GEXF (XML)."""
        with open(f"{filepath}.gexf", "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">\n')
            f.write('  <graph mode="static" defaultedgetype="directed">\n')

            # Nós
            f.write('    <nodes>\n')
            for v in range(self._vertex_count):
                label = self._labels[v] or f"v{v}"
                f.write(f'      <node id="{v}" label="{label}" />\n')
            f.write('    </nodes>\n')

            # Arestas
            f.write('    <edges>\n')
            edge_id = 0
            for u in self._adjacency:
                for edge in self._adjacency[u]:
                    f.write(
                        f'      <edge id="{edge_id}" source="{u}" '
                        f'target="{edge.destination}" weight="{edge.weight}" />\n'
                    )
                    edge_id += 1
            f.write('    </edges>\n')

            f.write('  </graph>\n')
            f.write('</gexf>\n')

    def _export_graphml(self, filepath: str) -> None:
        """Exporta para formato GraphML (XML)."""
        with open(f"{filepath}.graphml", "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<graphml xmlns="http://graphml.graphdrawing.org/xmlschema/graphml">\n')
            f.write('  <graph edgedefault="directed">\n')

            # Nós
            for v in range(self._vertex_count):
                label = self._labels[v] or f"v{v}"
                f.write(f'    <node id="{v}" label="{label}" />\n')

            # Arestas
            edge_id = 0
            for u in self._adjacency:
                for edge in self._adjacency[u]:
                    f.write(
                        f'    <edge id="{edge_id}" source="{u}" '
                        f'target="{edge.destination}" weight="{edge.weight}" />\n'
                    )
                    edge_id += 1

            f.write('  </graph>\n')
            f.write('</graphml>\n')

    def _export_csv(self, filepath: str) -> None:
        """Exporta para formato CSV (nodes.csv + edges.csv)."""
        # Nodes
        with open(f"{filepath}_nodes.csv", "w", encoding="utf-8") as f:
            f.write("id,label,weight\n")
            for v in range(self._vertex_count):
                label = self._labels[v] or f"v{v}"
                weight = self._vertex_weights[v]
                f.write(f"{v},{label},{weight}\n")

        # Edges
        with open(f"{filepath}_edges.csv", "w", encoding="utf-8") as f:
            f.write("source,target,weight\n")
            for u in self._adjacency:
                for edge in self._adjacency[u]:
                    f.write(f"{u},{edge.destination},{edge.weight}\n")

    # ========== REPRESENTAÇÃO ==========

    def __repr__(self) -> str:
        """Representação string do grafo."""
        return (
            f"AdjacencyListGraph("
            f"vertices={self._vertex_count}, "
            f"edges={self._edge_count})"
        )
