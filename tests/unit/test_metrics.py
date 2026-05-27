"""
Testes para MetricsService.

Testa cálculo de métricas de rede e centralidade.
"""

import pytest

from codigos.models import User
from codigos.core.graph import AdjacencyListGraph
from codigos.services import MetricsService


class TestMetricsService:
    """Testes para MetricsService."""

    @pytest.fixture
    def simple_graph(self):
        """Cria grafo simples para testes.

        Grafo:
            0 → 1 (weight 2)
            1 → 2 (weight 3)
            2 → 0 (weight 1)
        """
        graph = AdjacencyListGraph(3)
        graph.add_edge(0, 1, weight=2.0)
        graph.add_edge(1, 2, weight=3.0)
        graph.add_edge(2, 0, weight=1.0)
        return graph

    @pytest.fixture
    def users(self):
        """Cria usuários para testes."""
        return [
            User(id=1, login="alice"),
            User(id=2, login="bob"),
            User(id=3, login="charlie"),
        ]

    def test_init_valid(self, simple_graph, users):
        """Cria MetricsService com dados válidos."""
        service = MetricsService(simple_graph, users)
        assert service.graph == simple_graph
        assert service.users == users

    def test_init_invalid_graph(self, users):
        """Rejeita grafo com tamanho incompatível."""
        graph = AdjacencyListGraph(5)
        with pytest.raises(ValueError):
            MetricsService(graph, users)

    def test_init_invalid_users(self, simple_graph):
        """Rejeita lista de usuários vazia."""
        with pytest.raises(ValueError):
            MetricsService(simple_graph, [])

    def test_calculate_all_metrics(self, simple_graph, users):
        """Calcula todas as 9 métricas."""
        service = MetricsService(simple_graph, users)
        results = service.calculate_all_metrics()

        assert len(results) == 3
        for result in results:
            assert result.user in users
            assert 0 <= result.degree_centrality <= 1
            assert 0 <= result.betweenness_centrality <= 1
            assert 0 <= result.closeness_centrality <= 1
            assert result.pagerank >= 0
            assert 0 <= result.clustering_coefficient <= 1
            assert result.in_degree >= 0
            assert result.out_degree >= 0

    def test_degree_centrality(self, simple_graph, users):
        """Calcula degree centrality corretamente."""
        service = MetricsService(simple_graph, users)
        centrality = service._degree_centrality()

        assert len(centrality) == 3
        # Todos devem ter grau 2 (1 in + 1 out)
        # Formula: 2 / (2 * (3-1)) = 2 / 4 = 0.5
        for v in range(3):
            assert centrality[v] == pytest.approx(0.5, abs=0.01)

    def test_in_degree(self, simple_graph, users):
        """Calcula in-degree corretamente."""
        service = MetricsService(simple_graph, users)
        in_degree = service._in_degree()

        assert in_degree[0] == 1  # 2 → 0
        assert in_degree[1] == 1  # 0 → 1
        assert in_degree[2] == 1  # 1 → 2

    def test_out_degree(self, simple_graph, users):
        """Calcula out-degree corretamente."""
        service = MetricsService(simple_graph, users)
        out_degree = service._out_degree()

        assert out_degree[0] == 1  # 0 → 1
        assert out_degree[1] == 1  # 1 → 2
        assert out_degree[2] == 1  # 2 → 0

    def test_pagerank(self, simple_graph, users):
        """Calcula PageRank."""
        service = MetricsService(simple_graph, users)
        pagerank = service._pagerank()

        assert len(pagerank) == 3
        # PageRank soma deve ser ~1.0
        total = sum(pagerank.values())
        assert total == pytest.approx(1.0, abs=0.01)

        # Todos devem ter valor positivo
        for v in range(3):
            assert pagerank[v] > 0

    def test_betweenness_centrality(self, simple_graph, users):
        """Calcula betweenness centrality."""
        service = MetricsService(simple_graph, users)
        betweenness = service._betweenness_centrality()

        assert len(betweenness) == 3
        for v in range(3):
            assert 0 <= betweenness[v] <= 1

    def test_closeness_centrality(self, simple_graph, users):
        """Calcula closeness centrality."""
        service = MetricsService(simple_graph, users)
        closeness = service._closeness_centrality()

        assert len(closeness) == 3
        for v in range(3):
            assert 0 <= closeness[v] <= 1

    def test_clustering_coefficient(self, simple_graph, users):
        """Calcula clustering coefficient."""
        service = MetricsService(simple_graph, users)
        clustering = service._clustering_coefficient()

        assert len(clustering) == 3
        for v in range(3):
            assert 0 <= clustering[v] <= 1

    def test_eigenvector_centrality(self, simple_graph, users):
        """Calcula eigenvector centrality."""
        service = MetricsService(simple_graph, users)
        eigenvector = service._eigenvector_centrality()

        assert len(eigenvector) == 3
        for v in range(3):
            assert 0 <= eigenvector[v] <= 1

    def test_get_top_by_metric_pagerank(self, simple_graph, users):
        """Retorna top usuários por PageRank."""
        service = MetricsService(simple_graph, users)
        top = service.get_top_by_metric('pagerank', top_n=2)

        assert len(top) == 2
        for user, value in top:
            assert user in users
            assert value > 0

    def test_get_top_by_metric_degree(self, simple_graph, users):
        """Retorna top usuários por degree centrality."""
        service = MetricsService(simple_graph, users)
        top = service.get_top_by_metric('degree_centrality', top_n=3)

        assert len(top) == 3

    def test_get_top_by_metric_invalid(self, simple_graph, users):
        """Rejeita métrica desconhecida."""
        service = MetricsService(simple_graph, users)
        with pytest.raises(ValueError):
            service.get_top_by_metric('invalid_metric')

    def test_get_metrics_summary(self, simple_graph, users):
        """Retorna resumo de métricas."""
        service = MetricsService(simple_graph, users)
        summary = service.get_metrics_summary()

        assert 'avg_degree_centrality' in summary
        assert 'max_degree_centrality' in summary
        assert 'avg_pagerank' in summary
        assert 'max_pagerank' in summary
        assert 'avg_clustering' in summary

        # Verificar que valores são razoáveis
        assert summary['avg_degree_centrality'] >= 0
        assert summary['max_degree_centrality'] >= summary['avg_degree_centrality']
        assert summary['avg_pagerank'] > 0

    def test_metrics_on_star_graph(self):
        """Testa métricas em grafo de estrela (hub-and-spoke).

        Grafo:
            1 → 0, 2 → 0, 3 → 0 (todos apontam para 0)
        """
        graph = AdjacencyListGraph(4)
        users = [
            User(id=1, login="hub"),
            User(id=2, login="spoke1"),
            User(id=3, login="spoke2"),
            User(id=4, login="spoke3"),
        ]

        graph.add_edge(1, 0, weight=1.0)
        graph.add_edge(2, 0, weight=1.0)
        graph.add_edge(3, 0, weight=1.0)

        service = MetricsService(graph, users)
        results = service.calculate_all_metrics()

        # Nó 0 (hub) deve ter maior in-degree
        hub_result = results[0]
        spoke_result = results[1]

        assert hub_result.in_degree > spoke_result.in_degree
        assert hub_result.in_degree == 3
        assert spoke_result.in_degree == 0

    def test_metrics_on_disconnected_graph(self):
        """Testa métricas em grafo desconectado.

        Grafo:
            0 → 1 (componente 1)
            2 → 3 (componente 2)
        """
        graph = AdjacencyListGraph(4)
        users = [
            User(id=1, login="u1"),
            User(id=2, login="u2"),
            User(id=3, login="u3"),
            User(id=4, login="u4"),
        ]

        graph.add_edge(0, 1, weight=1.0)
        graph.add_edge(2, 3, weight=1.0)

        service = MetricsService(graph, users)
        results = service.calculate_all_metrics()

        assert len(results) == 4
        # Todos devem ter alguma métrica calculada
        for result in results:
            assert result.pagerank > 0
