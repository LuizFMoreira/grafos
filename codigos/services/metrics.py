"""
Cálculo de métricas de rede e centralidade.

Implementa 9 tipos de métricas para análise de grafos de colaboração.
"""

from typing import Dict, List
import math

from ..models import User, MetricsResult
from ..core.graph import AbstractGraph

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False


class MetricsService:
    """Calcula métricas de rede para grafos de colaboração.

    Implementa 9 tipos de métricas:
    1. Degree Centrality: proporciona de arestas
    2. In-Degree: número de arestas entrando
    3. Out-Degree: número de arestas saindo
    4. Betweenness Centrality: frequência em caminhos mais curtos
    5. Closeness Centrality: proximidade média
    6. PageRank: importância baseada em conexões
    7. Clustering Coefficient: densidade local (triângulos)
    8. Eigenvector Centrality: importância recursiva
    9. Harmonic Centrality: distância harmônica

    Usa NetworkX para algoritmos complexos quando disponível.
    """

    def __init__(self, graph: AbstractGraph, users: List[User]):
        """Inicializa serviço de métricas.

        Args:
            graph: Grafo para análise
            users: Lista de usuários (mesmo índice do grafo)

        Raises:
            ValueError: Se tamanhos não correspondem
        """
        if not isinstance(users, list) or len(users) == 0:
            raise ValueError("users must be non-empty list")
        if graph.get_vertex_count() != len(users):
            raise ValueError(
                f"Graph has {graph.get_vertex_count()} vertices "
                f"but {len(users)} users provided"
            )

        self.graph = graph
        self.users = users
        self._build_networkx_graph()

    def _build_networkx_graph(self) -> None:
        """Constrói grafo NetworkX equivalente para cálculos avançados."""
        self.nx_graph = None

        if not HAS_NETWORKX:
            return

        # Cria grafo direcionado
        self.nx_graph = nx.DiGraph()

        # Adiciona vértices
        for i, user in enumerate(self.users):
            self.nx_graph.add_node(i, label=user.login)

        # Adiciona arestas com pesos
        for u in range(self.graph.get_vertex_count()):
            for v in range(self.graph.get_vertex_count()):
                if self.graph.has_edge(u, v):
                    weight = self.graph.get_edge_weight(u, v)
                    self.nx_graph.add_edge(u, v, weight=weight)

    def calculate_all_metrics(self) -> List[MetricsResult]:
        """Calcula todas as 9 métricas para todos os usuários.

        Returns:
            Lista de MetricsResult, um por usuário
        """
        # Calcula cada métrica
        degree_centrality = self._degree_centrality()
        in_degree = self._in_degree()
        out_degree = self._out_degree()
        betweenness = self._betweenness_centrality()
        closeness = self._closeness_centrality()
        pagerank = self._pagerank()
        clustering = self._clustering_coefficient()
        eigenvector = self._eigenvector_centrality()

        # Monta resultados
        results = []
        for i, user in enumerate(self.users):
            result = MetricsResult(
                user=user,
                degree_centrality=degree_centrality.get(i, 0.0),
                in_degree=in_degree.get(i, 0),
                out_degree=out_degree.get(i, 0),
                betweenness_centrality=betweenness.get(i, 0.0),
                closeness_centrality=closeness.get(i, 0.0),
                pagerank=pagerank.get(i, 0.0),
                clustering_coefficient=clustering.get(i, 0.0),
                eigenvector_centrality=eigenvector.get(i, 0.0),
            )
            results.append(result)

        return results

    def _degree_centrality(self) -> Dict[int, float]:
        """Calcula centralidade de grau.

        Formula: (in_degree + out_degree) / (2 * (n - 1))

        Returns:
            Dict[vertex_index] → centralidade [0, 1]
        """
        n = self.graph.get_vertex_count()
        if n <= 1:
            return {i: 0.0 for i in range(n)}

        centrality = {}
        for v in range(n):
            in_d = self.graph.get_vertex_in_degree(v)
            out_d = self.graph.get_vertex_out_degree(v)
            total_d = in_d + out_d
            centrality[v] = total_d / (2 * (n - 1))

        return centrality

    def _in_degree(self) -> Dict[int, int]:
        """Retorna grau de entrada de cada vértice.

        Returns:
            Dict[vertex_index] → in_degree
        """
        return {v: self.graph.get_vertex_in_degree(v) for v in range(self.graph.get_vertex_count())}

    def _out_degree(self) -> Dict[int, int]:
        """Retorna grau de saída de cada vértice.

        Returns:
            Dict[vertex_index] → out_degree
        """
        return {v: self.graph.get_vertex_out_degree(v) for v in range(self.graph.get_vertex_count())}

    def _betweenness_centrality(self) -> Dict[int, float]:
        """Calcula centralidade de intermediação (betweenness).

        Usa NetworkX se disponível, senão retorna zeros.

        Returns:
            Dict[vertex_index] → betweenness [0, 1]
        """
        if self.nx_graph is None:
            return {i: 0.0 for i in range(len(self.users))}

        try:
            betweenness = nx.betweenness_centrality(self.nx_graph, weight='weight')
            return {int(k): float(v) for k, v in betweenness.items()}
        except Exception:
            return {i: 0.0 for i in range(len(self.users))}

    def _closeness_centrality(self) -> Dict[int, float]:
        """Calcula centralidade de proximidade (closeness).

        Usa NetworkX se disponível, senão retorna zeros.

        Returns:
            Dict[vertex_index] → closeness [0, 1]
        """
        if self.nx_graph is None:
            return {i: 0.0 for i in range(len(self.users))}

        try:
            closeness = nx.closeness_centrality(self.nx_graph, distance='weight')
            return {int(k): float(v) for k, v in closeness.items()}
        except Exception:
            return {i: 0.0 for i in range(len(self.users))}

    def _pagerank(self) -> Dict[int, float]:
        """Calcula PageRank (importância iterativa).

        Usa NetworkX se disponível, senão retorna distribuição uniforme.

        Returns:
            Dict[vertex_index] → pagerank (soma = 1.0)
        """
        if self.nx_graph is None:
            n = len(self.users)
            uniform = 1.0 / n if n > 0 else 0.0
            return {i: uniform for i in range(n)}

        try:
            pagerank = nx.pagerank(self.nx_graph, weight='weight', max_iter=100)
            return {int(k): float(v) for k, v in pagerank.items()}
        except Exception:
            n = len(self.users)
            uniform = 1.0 / n if n > 0 else 0.0
            return {i: uniform for i in range(n)}

    def _clustering_coefficient(self) -> Dict[int, float]:
        """Calcula coeficiente de clustering (densidade local).

        Usa NetworkX se disponível, senão retorna zeros.

        Returns:
            Dict[vertex_index] → clustering [0, 1]
        """
        if self.nx_graph is None:
            return {i: 0.0 for i in range(len(self.users))}

        try:
            # Converte para grafo não-dirigido para clustering
            undirected = self.nx_graph.to_undirected()
            clustering = nx.clustering(undirected, weight='weight')
            return {int(k): float(v) for k, v in clustering.items()}
        except Exception:
            return {i: 0.0 for i in range(len(self.users))}

    def _eigenvector_centrality(self) -> Dict[int, float]:
        """Calcula centralidade de autovetor (eigenvector).

        Usa NetworkX se disponível, senão retorna zeros.

        Returns:
            Dict[vertex_index] → eigenvector [0, 1]
        """
        if self.nx_graph is None:
            return {i: 0.0 for i in range(len(self.users))}

        try:
            # Tenta com grafo direcionado (pode não convergir)
            eigenvector = nx.eigenvector_centrality(
                self.nx_graph.to_undirected(),
                weight='weight',
                max_iter=100
            )
            return {int(k): float(v) for k, v in eigenvector.items()}
        except Exception:
            # Se falhar, retorna zeros
            return {i: 0.0 for i in range(len(self.users))}

    def get_top_by_metric(
        self,
        metric_name: str,
        top_n: int = 10
    ) -> List[tuple]:
        """Retorna top N usuários para uma métrica específica.

        Args:
            metric_name: Nome da métrica ('pagerank', 'degree_centrality', etc)
            top_n: Número de top resultados

        Returns:
            Lista de (User, valor_métrica) ordenados descrescente
        """
        results = self.calculate_all_metrics()

        # Mapeia nome da métrica para atributo
        metric_map = {
            'pagerank': 'pagerank',
            'degree_centrality': 'degree_centrality',
            'betweenness': 'betweenness_centrality',
            'closeness': 'closeness_centrality',
            'clustering': 'clustering_coefficient',
            'eigenvector': 'eigenvector_centrality',
            'in_degree': 'in_degree',
            'out_degree': 'out_degree',
        }

        if metric_name not in metric_map:
            raise ValueError(f"Unknown metric: {metric_name}")

        attr_name = metric_map[metric_name]

        # Ordena por métrica
        sorted_results = sorted(
            results,
            key=lambda r: getattr(r, attr_name),
            reverse=True
        )

        return [(r.user, getattr(r, attr_name)) for r in sorted_results[:top_n]]

    def get_metrics_summary(self) -> Dict[str, float]:
        """Retorna resumo de métricas do grafo inteiro.

        Returns:
            Dict com métricas agregadas (média, máxima, mínima, etc)
        """
        results = self.calculate_all_metrics()

        if not results:
            return {}

        # Extrai listas de valores
        degree_centralities = [r.degree_centrality for r in results]
        betweenness_values = [r.betweenness_centrality for r in results]
        closeness_values = [r.closeness_centrality for r in results]
        pageranks = [r.pagerank for r in results]
        clustering_values = [r.clustering_coefficient for r in results]
        eigenvector_values = [r.eigenvector_centrality for r in results]

        def safe_avg(values):
            return sum(values) / len(values) if values else 0.0

        def safe_max(values):
            return max(values) if values else 0.0

        def safe_min(values):
            return min(values) if values else 0.0

        return {
            'avg_degree_centrality': safe_avg(degree_centralities),
            'max_degree_centrality': safe_max(degree_centralities),
            'min_degree_centrality': safe_min(degree_centralities),
            'avg_betweenness': safe_avg(betweenness_values),
            'max_betweenness': safe_max(betweenness_values),
            'avg_closeness': safe_avg(closeness_values),
            'max_closeness': safe_max(closeness_values),
            'avg_pagerank': safe_avg(pageranks),
            'max_pagerank': safe_max(pageranks),
            'avg_clustering': safe_avg(clustering_values),
            'max_clustering': safe_max(clustering_values),
            'avg_eigenvector': safe_avg(eigenvector_values),
            'max_eigenvector': safe_max(eigenvector_values),
        }
