"""
Implementação de grafo usando matriz de adjacência.

Esta implementação usa uma matriz n×n onde matrix[u][v] representa o peso
da aresta u → v. É mais visual e melhor para entender a estrutura, mas
menos eficiente para grafos esparsos pois usa espaço O(V²).

Matriz de exemplo:
    0 1 2
  0 0 2 3
  1 0 0 1
  2 1 0 0

matrix[0][1] = 2 significa aresta 0 → 1 com peso 2
"""

from typing import List, Optional

from .abstract_graph import AbstractGraph
from ..exceptions.graph_exceptions import (
    InvalidVertexError,
    InvalidEdgeError,
    SelfLoopError,
)


class AdjacencyMatrixGraph(AbstractGraph):
    """Implementação de grafo usando matriz de adjacência.

    Usa uma matriz n×n onde matrix[u][v] é o peso da aresta u → v.
    Valor 0 significa ausência de aresta.

    Complexidade de Espaço: O(V²)
    Complexidade de Tempo:
        - has_edge: O(1)
        - add_edge: O(1)
        - remove_edge: O(1)
        - get neighbors: O(V)

    Attributes:
        _matrix: List[List[float]] - Matriz de pesos
    """

    def __init__(self, vertex_count: int):
        """Inicializa um grafo vazio com matriz de adjacência.

        Args:
            vertex_count: Número de vértices

        Raises:
            ValueError: Se vertex_count <= 0
        """
        super().__init__(vertex_count)

        # Matriz n×n inicializada com 0 (sem arestas)
        # Usamos 0 para indicar ausência de aresta
        self._matrix: List[List[float]] = [
            [0.0 for _ in range(vertex_count)] for _ in range(vertex_count)
        ]

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

        # Rejeita self-loops
        if u == v:
            raise SelfLoopError(u)

        if weight < 0:
            raise ValueError(f"Weight must be >= 0, got {weight}")

        # Verifica se aresta já existe
        if self._matrix[u][v] == 0.0:
            # Nova aresta
            self._matrix[u][v] = float(weight)
            self._edge_count += 1
        else:
            # Aresta existe: acumula peso (idempotência)
            self._matrix[u][v] += weight

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

        if self._matrix[u][v] == 0.0:
            raise InvalidEdgeError(u, v)

        self._matrix[u][v] = 0.0
        self._edge_count -= 1

    def has_edge(self, u: int, v: int) -> bool:
        """Verifica se existe aresta u → v."""
        self._validate_vertices(u, v)
        return self._matrix[u][v] != 0.0

    def set_edge_weight(self, u: int, v: int, weight: float) -> None:
        """Define o peso da aresta u → v."""
        self._validate_vertices(u, v)

        if weight < 0:
            raise ValueError(f"Weight must be >= 0, got {weight}")

        if self._matrix[u][v] == 0.0:
            raise InvalidEdgeError(u, v)

        self._matrix[u][v] = float(weight)

    def get_edge_weight(self, u: int, v: int) -> float:
        """Retorna o peso da aresta u → v."""
        self._validate_vertices(u, v)

        if self._matrix[u][v] == 0.0:
            raise InvalidEdgeError(u, v)

        return self._matrix[u][v]

    # ========== GRAUS ==========

    def get_vertex_in_degree(self, v: int) -> int:
        """Retorna o grau de entrada do vértice v."""
        self._validate_vertex(v)

        in_degree = 0
        # Conta quantas arestas chegam em v (coluna v)
        for u in range(self._vertex_count):
            if self._matrix[u][v] != 0.0:
                in_degree += 1

        return in_degree

    def get_vertex_out_degree(self, v: int) -> int:
        """Retorna o grau de saída do vértice v."""
        self._validate_vertex(v)

        out_degree = 0
        # Conta quantas arestas saem de v (linha v)
        for target in range(self._vertex_count):
            if self._matrix[v][target] != 0.0:
                out_degree += 1

        return out_degree

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

        Usa DFS a partir de cada vértice.
        """
        if self._vertex_count == 0:
            return True

        # DFS a partir de 0
        visited = set()
        self._dfs(0, visited)

        if len(visited) != self._vertex_count:
            return False

        # Cria grafo transposto (inverte todas as arestas)
        transposed = AdjacencyMatrixGraph(self._vertex_count)
        for u in range(self._vertex_count):
            for v in range(self._vertex_count):
                if self._matrix[u][v] != 0.0:
                    transposed._matrix[v][u] = self._matrix[u][v]
                    transposed._edge_count += 1

        # DFS no grafo transposto a partir de 0
        visited = set()
        transposed._dfs(0, visited)

        return len(visited) == self._vertex_count

    def is_complete_graph(self) -> bool:
        """Verifica se o grafo é completo.

        Um grafo direcionado completo tem aresta entre todos os pares
        distintos de vértices (em ambas direções).

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
            for neighbor in range(self._vertex_count):
                if (
                    self._matrix[v][neighbor] != 0.0
                    and neighbor not in visited
                ):
                    stack.append(neighbor)

    def get_successors(self, v: int) -> List[int]:
        """Retorna lista de sucessores do vértice v."""
        self._validate_vertex(v)

        successors = []
        for target in range(self._vertex_count):
            if self._matrix[v][target] != 0.0:
                successors.append(target)

        return successors

    def get_predecessors(self, v: int) -> List[int]:
        """Retorna lista de predecessores do vértice v."""
        self._validate_vertex(v)

        predecessors = []
        for source in range(self._vertex_count):
            if self._matrix[source][v] != 0.0:
                predecessors.append(source)

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
            for u in range(self._vertex_count):
                for v in range(self._vertex_count):
                    if self._matrix[u][v] != 0.0:
                        f.write(
                            f'      <edge id="{edge_id}" source="{u}" '
                            f'target="{v}" weight="{self._matrix[u][v]}" />\n'
                        )
                        edge_id += 1
            f.write('    </edges>\n')

            f.write('  </graph>\n')
            f.write('</gexf>\n')

    def _export_graphml(self, filepath: str) -> None:
        """Exporta para formato GraphML (XML)."""
        with open(f"{filepath}.graphml", "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(
                '<graphml xmlns="http://graphml.graphdrawing.org/xmlschema/graphml">\n'
            )
            f.write('  <graph edgedefault="directed">\n')

            # Nós
            for v in range(self._vertex_count):
                label = self._labels[v] or f"v{v}"
                f.write(f'    <node id="{v}" label="{label}" />\n')

            # Arestas
            edge_id = 0
            for u in range(self._vertex_count):
                for v in range(self._vertex_count):
                    if self._matrix[u][v] != 0.0:
                        f.write(
                            f'    <edge id="{edge_id}" source="{u}" '
                            f'target="{v}" weight="{self._matrix[u][v]}" />\n'
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
            for u in range(self._vertex_count):
                for v in range(self._vertex_count):
                    if self._matrix[u][v] != 0.0:
                        f.write(f"{u},{v},{self._matrix[u][v]}\n")

    # ========== REPRESENTAÇÃO ==========

    def __repr__(self) -> str:
        """Representação string do grafo."""
        return (
            f"AdjacencyMatrixGraph("
            f"vertices={self._vertex_count}, "
            f"edges={self._edge_count})"
        )

    def visualize_matrix(self) -> str:
        """Retorna visualização textual da matriz (para debug).

        Útil para entender visualmente a estrutura do grafo.
        """
        lines = ["Adjacency Matrix:"]

        # Header com índices das colunas
        header = "  "
        for j in range(self._vertex_count):
            header += f"{j:5}"
        lines.append(header)

        # Linhas da matriz
        for i in range(self._vertex_count):
            row = f"{i} "
            for j in range(self._vertex_count):
                value = self._matrix[i][j]
                row += f"{value:5.1f}"
            lines.append(row)

        return "\n".join(lines)
