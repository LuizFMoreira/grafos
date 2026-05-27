"""
Algoritmos fundamentais para grafos.

Este módulo implementa algoritmos essenciais para análise de grafos:
- DFS (Depth First Search): Busca em profundidade
- BFS (Breadth First Search): Busca em largura
- Dijkstra: Caminho mais curto ponderado

Todos implementados sem usar bibliotecas externas.
"""

from typing import Dict, List, Optional, Set, Tuple
from collections import deque
import math

from .abstract_graph import AbstractGraph


class GraphAlgorithms:
    """Classe com métodos estáticos para algoritmos de grafos.

    Implementa algoritmos fundamentais que podem ser usados em
    qualquer implementação concreta de AbstractGraph.
    """

    @staticmethod
    def dfs(
        graph: AbstractGraph, start: int, visited: Optional[Set[int]] = None
    ) -> Set[int]:
        """DFS (Depth First Search) recursiva.

        Visita todos os vértices alcançáveis a partir de start.

        Algoritmo:
        1. Marca start como visitado
        2. Para cada vizinho não visitado:
           - Chama DFS recursivamente
        3. Retorna conjunto de visitados

        Complexidade:
        - Tempo: O(V + E)
        - Espaço: O(V) para stack recursivo

        Args:
            graph: Grafo a explorar
            start: Vértice inicial
            visited: Conjunto de visitados (para chamadas recursivas)

        Returns:
            Conjunto de vértices visitados
        """
        if visited is None:
            visited = set()

        visited.add(start)

        # Pega vizinhos do vértice (método auxiliar)
        if hasattr(graph, "get_successors"):
            neighbors = graph.get_successors(start)
        else:
            # Fallback: itera por todos os vértices
            neighbors = [
                v
                for v in range(graph.get_vertex_count())
                if graph.has_edge(start, v)
            ]

        for neighbor in neighbors:
            if neighbor not in visited:
                GraphAlgorithms.dfs(graph, neighbor, visited)

        return visited

    @staticmethod
    def dfs_iterative(graph: AbstractGraph, start: int) -> Set[int]:
        """DFS iterativa (usando stack explícito).

        Evita possível estouro de pilha com grafos muito profundos.

        Algoritmo:
        1. Push start na pilha
        2. Enquanto pilha não vazia:
           - Pop um vértice
           - Se não visitado, marca e adiciona vizinhos

        Complexidade:
        - Tempo: O(V + E)
        - Espaço: O(V)

        Args:
            graph: Grafo a explorar
            start: Vértice inicial

        Returns:
            Conjunto de vértices visitados
        """
        visited = set()
        stack = [start]

        while stack:
            v = stack.pop()

            if v in visited:
                continue

            visited.add(v)

            # Pega vizinhos
            if hasattr(graph, "get_successors"):
                neighbors = graph.get_successors(v)
            else:
                neighbors = [
                    target
                    for target in range(graph.get_vertex_count())
                    if graph.has_edge(v, target)
                ]

            # Adiciona vizinhos não visitados
            for neighbor in reversed(neighbors):  # reverse para manter ordem
                if neighbor not in visited:
                    stack.append(neighbor)

        return visited

    @staticmethod
    def bfs(graph: AbstractGraph, start: int) -> Set[int]:
        """BFS (Breadth First Search).

        Visita vértices em ordem de distância do vértice inicial.

        Algoritmo:
        1. Enfileira start
        2. Enquanto fila não vazia:
           - Defileira um vértice
           - Marca como visitado
           - Enfileira vizinhos não visitados
        3. Retorna visitados

        Complexidade:
        - Tempo: O(V + E)
        - Espaço: O(V)

        Args:
            graph: Grafo a explorar
            start: Vértice inicial

        Returns:
            Conjunto de vértices visitados
        """
        visited = set()
        queue = deque([start])
        visited.add(start)

        while queue:
            v = queue.popleft()

            # Pega vizinhos
            if hasattr(graph, "get_successors"):
                neighbors = graph.get_successors(v)
            else:
                neighbors = [
                    target
                    for target in range(graph.get_vertex_count())
                    if graph.has_edge(v, target)
                ]

            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return visited

    @staticmethod
    def dijkstra(
        graph: AbstractGraph, start: int
    ) -> Tuple[Dict[int, float], Dict[int, Optional[int]]]:
        """Algoritmo de Dijkstra para caminho mais curto.

        Encontra o caminho mais curto de um vértice para todos os outros.

        Algoritmo:
        1. Inicializa distâncias (start=0, outros=infinito)
        2. Inicializa previousos (None para todos)
        3. Enquanto há vértices não visitados:
           - Pega vértice não visitado com menor distância
           - Para cada vizinho:
               - Se distância é melhorada, atualiza
        4. Retorna distâncias e predecessores

        Complexidade:
        - Tempo: O(V²) com lista, O((V+E)logV) com heap
        - Espaço: O(V)

        Args:
            graph: Grafo ponderado (deve ter arestas com pesos > 0)
            start: Vértice inicial

        Returns:
            Tupla (distâncias, predecessores)
            - distâncias: Dict[vértice] → distância
            - predecessores: Dict[vértice] → vértice anterior no caminho
        """
        v_count = graph.get_vertex_count()

        # Inicialização
        distances = {v: float("inf") for v in range(v_count)}
        distances[start] = 0.0

        predecessors: Dict[int, Optional[int]] = {v: None for v in range(v_count)}

        unvisited = set(range(v_count))

        while unvisited:
            # Encontra vértice não visitado com menor distância
            current = min(unvisited, key=lambda v: distances[v])

            # Se distância é infinita, não há caminho
            if distances[current] == float("inf"):
                break

            unvisited.remove(current)

            # Relaxamento das arestas
            if hasattr(graph, "get_successors"):
                neighbors = graph.get_successors(current)
            else:
                neighbors = [
                    v
                    for v in range(v_count)
                    if graph.has_edge(current, v)
                ]

            for neighbor in neighbors:
                if neighbor in unvisited:
                    # Pega peso da aresta
                    try:
                        weight = graph.get_edge_weight(current, neighbor)
                    except Exception:
                        continue

                    # Relaxamento
                    new_distance = distances[current] + weight
                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        predecessors[neighbor] = current

        return distances, predecessors

    @staticmethod
    def shortest_path(
        graph: AbstractGraph, start: int, end: int
    ) -> Optional[List[int]]:
        """Encontra o caminho mais curto entre dois vértices.

        Usa Dijkstra para encontrar o caminho.

        Args:
            graph: Grafo ponderado
            start: Vértice inicial
            end: Vértice final

        Returns:
            Lista de vértices no caminho, ou None se não existe caminho
        """
        distances, predecessors = GraphAlgorithms.dijkstra(graph, start)

        # Se não há caminho
        if distances[end] == float("inf"):
            return None

        # Reconstrói o caminho
        path = []
        current = end

        while current is not None:
            path.append(current)
            current = predecessors[current]

        path.reverse()
        return path

    @staticmethod
    def shortest_path_distance(
        graph: AbstractGraph, start: int, end: int
    ) -> float:
        """Retorna a distância do caminho mais curto.

        Args:
            graph: Grafo ponderado
            start: Vértice inicial
            end: Vértice final

        Returns:
            Distância do caminho mais curto, ou float('inf') se não existe
        """
        distances, _ = GraphAlgorithms.dijkstra(graph, start)
        return distances[end]

    @staticmethod
    def count_paths(
        graph: AbstractGraph, start: int, end: int
    ) -> int:
        """Conta o número de caminhos distintos entre dois vértices.

        Usa DFS com memoização.

        Args:
            graph: Grafo
            start: Vértice inicial
            end: Vértice final

        Returns:
            Número de caminhos
        """
        memo: Dict[int, int] = {}

        def count_from(v: int) -> int:
            if v == end:
                return 1

            if v in memo:
                return memo[v]

            total = 0

            if hasattr(graph, "get_successors"):
                neighbors = graph.get_successors(v)
            else:
                neighbors = [
                    target
                    for target in range(graph.get_vertex_count())
                    if graph.has_edge(v, target)
                ]

            for neighbor in neighbors:
                total += count_from(neighbor)

            memo[v] = total
            return total

        return count_from(start)

    @staticmethod
    def all_shortest_paths(
        graph: AbstractGraph, start: int
    ) -> Tuple[Dict[int, float], Dict[int, List[int]]]:
        """Calcula todos os caminhos mais curtos a partir de um vértice.

        Basicamente, retorna Dijkstra com predecessores em forma de lista.

        Args:
            graph: Grafo ponderado
            start: Vértice inicial

        Returns:
            Tupla (distâncias, predecessores_lista)
        """
        v_count = graph.get_vertex_count()

        distances, single_pred = GraphAlgorithms.dijkstra(graph, start)

        # Converte predecessores únicos em lista de predecessores
        predecessors_list: Dict[int, List[int]] = {
            v: [] for v in range(v_count)
        }

        for v in range(v_count):
            if single_pred[v] is not None:
                predecessors_list[v].append(single_pred[v])

        return distances, predecessors_list
